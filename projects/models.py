from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    project_type = models.CharField(max_length=100) # e.g., 'Residential', 'Commercial'
    region = models.CharField(max_length=100)
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = RichTextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def bookmark_count(self):
        """返回此專案的收藏數量"""
        return self.bookmarked_by.count()

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='project_images/')
    is_key_image = models.BooleanField(default=False) # For the 3-5 key images gallery

    def __str__(self):
        return f"Image for {self.project.title}"

class Folder(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    description = models.TextField(blank=True, null=True)
    cover_image = models.ForeignKey(ProjectImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='folder_covers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bookmarked_by')
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookmarks')
    cover_image = models.ForeignKey(ProjectImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookmark_covers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project', 'folder') # A project can only be bookmarked once per user per folder

    def __str__(self):
        return f"{self.user.username} bookmarked {self.project.title}"
