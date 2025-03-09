from django.contrib import admin
from .models import Professor, Module, ModuleInstance, Rating

class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor_id', 'first_name', 'last_name', 'average_rating')
    search_fields = ('professor_id', 'first_name', 'last_name')

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

class ModuleInstanceAdmin(admin.ModelAdmin):
    list_display = ('module', 'year', 'semester', 'get_professors')
    list_filter = ('year', 'semester')
    search_fields = ('module__code', 'module__name')
    filter_horizontal = ('professors',)
    
    def get_professors(self, obj):
        return ", ".join([p.professor_id for p in obj.professors.all()])
    get_professors.short_description = 'Professors'

class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'professor', 'module_instance', 'rating')
    list_filter = ['rating']
    search_fields = ('user__username', 'professor__professor_id', 'module_instance__module__code')

admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(ModuleInstance, ModuleInstanceAdmin)
admin.site.register(Rating, RatingAdmin)
