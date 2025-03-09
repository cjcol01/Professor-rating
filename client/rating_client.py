# imports
import cmd
import requests
import getpass
import os
import pickle


# main CL progam using cmd lib
class ProfessorRatingShell(cmd.Cmd):

    intro = "Welcome to the Professor Rating System. Type help to list commands.\n"
    prompt = "rating system client $ "
    
    def __init__(self):
        super().__init__()
        self.base_url = None
        self.token = None
        self.session = requests.Session()
        self.session_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.session')
        self.load_session()
    
    # save session data to file
    def save_session(self):
        try:
            with open(self.session_file, 'wb') as f:
                session_data = {
                    'base_url': self.base_url,
                    'token': self.token,
                    'cookies': self.session.cookies,
                    'headers': dict(self.session.headers)
                }
                pickle.dump(session_data, f)
        except Exception as e:
            print(f"Warning: failed to save session: {e}")
    
    # load session data from save file
    def load_session(self):
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'rb') as f:
                    session_data = pickle.load(f)
                    self.base_url = session_data.get('base_url')
                    self.token = session_data.get('token')
                    
                    # get session cookies 
                    self.session.cookies = session_data.get('cookies', self.session.cookies)
                    
                    # set auth header if token exists
                    if self.token:
                        self.session.headers.update({
                            'Authorization': f'Token {self.token}',
                            'Content-Type': 'application/json'
                        })
                    
                    # load other headers
                    for key, value in session_data.get('headers', {}).items():
                        if key not in ['Authorization', 'Content-Type']:
                            self.session.headers[key] = value
        
        # else create a new session if loading fails                            
        except Exception as e:
            print(f"Warning: Couldnt load session: {e}")
            self.session = requests.Session()
    
    # clear session data
    def clear_session(self):
        self.base_url = None
        self.token = None
        self.session = requests.Session()
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception as e:
            print(f"unable to delete session: {e}")
    
    # check if user is logged in and server URL is set (for some reason)
    def check_login(self):
        if not self.base_url:
            # set default URL if not already set
            self.base_url = "http://127.0.0.1:8000/api"
        return True

    # register new user
    def do_register(self, arg):
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = getpass.getpass("Enter password: ")
        
        # Set default URL if not already set
        if not self.base_url:
            self.base_url = "http://127.0.0.1:8000/api"
        
        url = f"{self.base_url}/register/"
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 201:
                print("Registration successful!")
                print("You can now login.")
            else:
                print(f"Registration failed: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to server: {e}")
    
    # log in to the service. 
    def do_login(self, arg):
        args = arg.split()
        if not args:
            # Use default URL if not provided
            url = "127.0.0.1:8000"
            print(f"Using the default server URL: {url}")
        else:
            url = args[0]
        
        # set base URL with the provided URL (by user)
        self.base_url = f"http://{url}/api"
        
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")
        
        url = f"{self.base_url}/login/"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            # use session object forthe request
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                self.token = response.json().get("token")
                
                # set the authorisation header
                self.session.headers.update({
                    'Authorization': f'Token {self.token}',
                    'Content-Type': 'application/json'
                })
                
                self.save_session()
                print("Login successful!")
            else:
                print(f"Login failed: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to the server: {e}")
    
    # logout of session
    def do_logout(self, arg):
        if os.path.exists(self.session_file):
            self.clear_session()
            print("Logged out successfully.")

        else:
            print("Your not logged in yet!")
    
    # list all module instances and professors
    def do_list(self, arg):
        if not self.check_login():
            return
        
        url = f"{self.base_url}/modules/instances/"
        
        try:
            # use session object for the request
            response = self.session.get(url)
            if response.status_code == 200:
                instances = response.json()
                
                # print header
                print(f"{'Code':<6} {'Name':<30} {'Year':<6} {'Semester':<10} {'Taught by':<50}")
                print("-" * 100)
                
                # print each module instance
                for instance in instances:
                    professors_str = ", \n\t\t\t\t\t\t\t".join([f" {p['display_name']}" 
                                              for p in instance['professors']])
                    
                    print(f"{instance['module_code']:<6} {instance['module_name']:<30} "
                          f"{instance['year']:<6} {instance['semester']:<10} {professors_str:<50}")
                    print("-" * 100)
            else:
                print(f"Unable to retrieve module instances: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to the server: {e}")
    
    # view ratings of professors
    def do_view(self, arg):
        if not self.check_login():
            return
        
        url = f"{self.base_url}/professors/ratings/"
        
        try:
            # Use the session object for the request
            response = self.session.get(url)
            if response.status_code == 200:
                professors = response.json()
                
                for professor in professors:
                    print(f"The rating of {professor['display_name']} is {professor['rating_display']}")
            else:
                print(f"Unable to retrieve professor ratings: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to the server: {e}")
    
    # view average rating of a professor in a module
    def do_average(self, arg):
        args = arg.split()
        if len(args) < 2:
            print("Error: professor_id and module_code are required. \nUsage: average <professor_id> <module_code>")
            return
        
        professor_id = args[0]
        module_code = args[1]
        
        if not self.check_login():
            return
        
        url = f"{self.base_url}/professors/{professor_id}/modules/{module_code}/rating/"
        
        try:
            # Use the session object for the request
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                if not data.get('rating_display'):
                    print(f"Professor with ID {data['professor_id']} has not been rated yet in module {data['module_code']}.")
                else:
                    print(f"The rating of Professor with ID {data['professor_id']} "
                  f"in module {data['module_code']} is {data['rating_display']}")
            else:
                print(f"Failed to retrieve average rating: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to the server: {e}")
    
    # rate professor in a module instance
    def do_rate(self, arg):
        args = arg.split()
        if len(args) != 5:
            print("Error: All arguments are required. \nUsage: rate <professor_id> <module_code> <year> <semester> <rating>")
            return
        
        professor_id = args[0]
        module_code = args[1]
        year = args[2]
        semester = args[3]
        rating_value = args[4]
        
        if not self.check_login():
            return
        
        if not self.token:
            print("Error: You must be logged in to rate a professor.")
            return
        
        url = f"{self.base_url}/ratings/create/"
        data = {
            "professor_id": professor_id,
            "module_code": module_code,
            "year": year,
            "semester": semester,
            "rating": rating_value
        }
        
        try:
            # use sesh! object for the request 
            response = self.session.post(url, json=data)
            if response.status_code in [200, 201]:
                print("Rating submitted successfully!")
            else:
                print(f"Unable to submit rating: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to the server: {e}")
    
    # logout and exit
    def do_exit(self, arg):
        self.do_logout()
        print("Goodbye!")
        return True


if __name__ == "__main__":
    ProfessorRatingShell().cmdloop()