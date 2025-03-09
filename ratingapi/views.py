from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User

from .models import Professor, Module, ModuleInstance, Rating
from .serialisers import (
    UserSerialiser, 
    ModuleInstanceListSerialiser, RatingSerialiser,
    ProfessorRatingSerialiser, ModuleAverageRatingSerialiser
)

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerialiser


    # view to list module instances with the professors teaching them.
class ModuleInstanceListView(generics.ListAPIView):
    queryset = ModuleInstance.objects.all().prefetch_related('professors', 'module')

    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    #I SHOULD NOT RENAME THIS TO SERIALISER_CLASS THAT WAS PAINFUL
    serializer_class = ModuleInstanceListSerialiser
    permission_classes = [AllowAny]

# view to list professors with their average ratings.
class ProfessorRatingListView(generics.ListAPIView):
    queryset = Professor.objects.all()
    serializer_class = ProfessorRatingSerialiser
    permission_classes = [AllowAny]


@api_view(['GET'])
@permission_classes([AllowAny])
def professor_module_average_rating(request, professor_id, module_code):
    """
    view to get average rating of a professor in a  module.
    """
    professor = get_object_or_404(Professor, professor_id=professor_id)
    module = get_object_or_404(Module, code=module_code)
    
    # calc average rating
    avg_rating = Rating.objects.filter(
        professor=professor,
        module_instance__module=module
    ).aggregate(Avg('rating'))['rating__avg']
    
    if avg_rating is None:
        avg_rating = 0
    else:
        avg_rating = round(avg_rating)
    
    data = {
        'professor_id': professor_id,
        'module_code': module_code,
        'average_rating': avg_rating,
        'rating_display': '*' * avg_rating
    }
    
    serialiser = ModuleAverageRatingSerialiser(data)
    return Response(serialiser.data)

# view to create or update a rating.
class RatingCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RatingSerialiser
    
    def perform_create(self, serialiser):
        serialiser.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # get data from request
        professor_id = request.data.get('professor_id')
        module_code = request.data.get('module_code')
        year = request.data.get('year')
        semester = request.data.get('semester')
        rating_value = request.data.get('rating')
        
        # confirm data ahs the right foirmat
        if not all([professor_id, module_code, year, semester, rating_value]):
            return Response(
                {"error": "All fields are required: professor_id, module_code, year, semester, rating"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rating_value = int(rating_value)
            if not (1 <= rating_value <= 5):
                return Response(
                    {"error": "Rating must be between 1 and 5"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            year = int(year)
            semester = int(semester)
            if not (1 <= semester <= 2):
                return Response(
                    {"error": "Semester must be 1 or 2"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"error": "Invalid number format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # get / validate objects
        try:
            professor = Professor.objects.get(professor_id=professor_id)
            module = Module.objects.get(code=module_code)
            
            # get module instance or return error if one isnt found
            try:
                module_instance = ModuleInstance.objects.get(
                    module=module,
                    year=year,
                    semester=semester
                )
            except ModuleInstance.DoesNotExist:
                return Response(
                    {"error": f"Module instance for {module_code} in year {year} semester {semester} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # check if the professor teaches this module instance
            if professor not in module_instance.professors.all():
                return Response(
                    {"error": f"Professor {professor_id} is not teaching {module_code} in year {year} semester {semester}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Professor.DoesNotExist:
            return Response(
                {"error": f"Professor with ID {professor_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Module.DoesNotExist:
            return Response(
                {"error": f"Module with code {module_code} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # create or update profs rating
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            module_instance=module_instance,
            professor=professor,
            defaults={'rating': rating_value}
        )
        
        serialiser = RatingSerialiser(rating)
        return Response(serialiser.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

def home(request):
    return render(request, 'ratingapi/index.html')