from django.contrib import admin
from .models import CarMake, CarModel

# CarModelInline class for displaying CarModel instances inline within CarMake admin
class CarModelInline(admin.TabularInline):
    model = CarModel  # The model we want to display inline
    extra = 1  # Number of empty forms to display by default

# CarModelAdmin class for customizing how CarModel is displayed in the admin
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_make', 'type', 'year')  # Customize list view
    list_filter = ('car_make', 'type', 'year')  # Add filters in the sidebar
    search_fields = ('name', 'car_make__name')  # Add search functionality

# CarMakeAdmin class for customizing how CarMake is displayed in the admin
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Customize list view
    search_fields = ('name',)  # Add search functionality
    inlines = [CarModelInline]  # Include the CarModelInline within CarMakeAdmin

# Registering the models with their respective admin classes
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
