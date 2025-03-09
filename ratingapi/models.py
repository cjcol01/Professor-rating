from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from django.utils.functional import cached_property


# a professor who teaches modules
class Professor(models.Model):
    professor_id = models.CharField(max_length=10, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    @property
    def full_name(self):
        return f"Professor {self.first_name[0]}. {self.last_name}"
    
    @property
    def display_name(self):
        return f"{self.professor_id}, {self.full_name}"
    
    @property
    def average_rating(self):
        """overall rating of a professor"""
        # Change from module_instance__professors=self to professor=self
        avg = Rating.objects.filter(professor=self).aggregate(Avg('rating'))['rating__avg']
        if avg is None:
            return 0
        return round(avg)
    
    def __str__(self):
        return self.display_name

# a module taught at the university
class Module(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.code} {self.name}"

# a specific instance of a module taught in a particular year and semester by a prof 
class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='instances')
    year = models.IntegerField(help_text="Academic year (2018 for 2018-19)")
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    professors = models.ManyToManyField(Professor, related_name='module_instances')
    
    class Meta:
        unique_together = ['module', 'year', 'semester']
    
    def __str__(self):
        return f"{self.module.code} - {self.year} - Semester {self.semester}"


# a rating given by a user to a professor for a specific module (instance)
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module_instance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    class Meta:
        unique_together = ['user', 'module_instance', 'professor']
    
    def __str__(self):
        return f"Rating by {self.user.username} for {self.professor.professor_id} in {self.module_instance}"
