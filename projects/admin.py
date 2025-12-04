from django.contrib import admin
from .models import Project, ProjectImage, Folder, Bookmark

# Register your models here.
admin.site.register(Project)
admin.site.register(ProjectImage)
admin.site.register(Folder)
admin.site.register(Bookmark)
