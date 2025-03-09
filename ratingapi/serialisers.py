from rest_framework import serializers as serialisers # i cant tell you how much I hate spelling things with a Z
from django.contrib.auth.models import User
from .models import Professor, Module, ModuleInstance, Rating


# no z's allowed (ok some z's)
class UserSerialiser(serialisers.ModelSerializer):
    password = serialisers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serialisers.ValidationError("A user with this email already exists.")
        return value


class ProfessorSerialiser(serialisers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['professor_id', 'first_name', 'last_name', 'full_name', 'display_name']


class ModuleSerialiser(serialisers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['code', 'name']


class ProfessorDisplaySerialiser(serialisers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['professor_id', 'display_name']


class ModuleInstanceListSerialiser(serialisers.ModelSerializer):
    module_code = serialisers.CharField(source='module.code')
    module_name = serialisers.CharField(source='module.name')
    professors = ProfessorDisplaySerialiser(many=True, read_only=True)
    
    class Meta:
        model = ModuleInstance
        fields = ['id', 'module_code', 'module_name', 'year', 'semester', 'professors']


class RatingSerialiser(serialisers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'user', 'module_instance', 'professor', 'rating']
        read_only_fields = ['user']
    
    def validate(self, data):
        # ensure the professor is actually teaching the module instance
        if data['professor'] not in data['module_instance'].professors.all():
            raise serialisers.ValidationError(
                f"Professor {data['professor']} is not teaching this module instance."
            )
        return data


class ProfessorRatingSerialiser(serialisers.ModelSerializer):
    average_rating = serialisers.IntegerField(read_only=True)
    rating_display = serialisers.SerializerMethodField()
    
    class Meta:
        model = Professor
        fields = ['professor_id', 'display_name', 'average_rating', 'rating_display']
    
    def get_rating_display(self, obj):
        """return the rating as stars (*)."""
        return '*' * obj.average_rating


class ModuleAverageRatingSerialiser(serialisers.Serializer):
    professor_id = serialisers.CharField()
    module_code = serialisers.CharField()
    average_rating = serialisers.IntegerField()
    rating_display = serialisers.CharField()

    def to_representation(self, instance):
        return {
            'professor_id': instance['professor_id'],
            'module_code': instance['module_code'],
            'average_rating': instance['average_rating'],
            'rating_display': '*' * instance['average_rating']
        }