from django.contrib import admin
from .models import User,ScholarShipProvider,ScholarShip,ApplyScholarShip,CentralGoverment,StateGoverment,Log,Student
# Register your models here.
admin.site.register(User)
admin.site.register(CentralGoverment)
admin.site.register(StateGoverment)
admin.site.register(ScholarShipProvider)
admin.site.register(ScholarShip)
admin.site.register(ApplyScholarShip)
admin.site.register(Log)
admin.site.register(Student)