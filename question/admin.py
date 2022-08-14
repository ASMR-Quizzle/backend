from django.contrib import admin
from .models import Question, Topic, UserEligibilityTest

# Register your models here.
admin.site.register(Question)
admin.site.register(Topic)
admin.site.register(UserEligibilityTest)
