from django.contrib import admin
from .models import (
    CSVFile,
    Question,
    Topic,
    UserEligibilityTest,
    UserEligibilityTestTracker,
)

# Register your models here.
admin.site.register(Question)
admin.site.register(Topic)
admin.site.register(UserEligibilityTest)
admin.site.register(UserEligibilityTestTracker)
admin.site.register(CSVFile)
