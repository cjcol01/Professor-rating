# Professor Rating System

to access the admin page use the details:
```
username: cjcoleman
password: Hello123 
```

The python anywhere domain is 
```
py20cjcb.pythonanywhere.com
```

## Using the Client Application

The command-line client allows users to interact with the API. Here are the available commands:

### Register
```
python rating_client.py register
```

### Login
```
python rating_client.py login <server_url (optional)>
```

### Logout
```
python rating_client.py logout
```

### List Modules
```
python rating_client.py list
```

### View Professor Ratings
```
python rating_client.py view
```

### View Average Rating of a Professor in a Module
```
python rating_client.py average <professor_id> <module_code>
```

### Rate a Professor
```
python rating_client.py rate <professor_id> <module_code> <year> <semester> <rating>
```

## Example Usage

start the client with
```
 python rating_client.py
```
```
# Login to the service
login py20cjcb.pythonanywhere.com

# List all module instances
list

# View all professor ratings
view

# View the average rating of a professor in a specific module
average JE1 CD1

# Rate a professor
rate JE1 CD1 2018 1 5
```
