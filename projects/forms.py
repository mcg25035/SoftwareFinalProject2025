from django import forms
from .models import Project, ProjectImage, Folder, Bookmark
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.auth.models import User

class ProjectForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Project
        fields = ['title', 'project_type', 'region', 'area', 'description']
        # widgets = {
        #     'description': forms.Textarea(attrs={'rows': 10}), # This will be overridden by CKEditorUploadingWidget
        # }

class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image', 'is_key_image']

class FolderForm(forms.ModelForm):
    cover_image = forms.ModelChoiceField(queryset=None, required=False, label="選擇封面圖片 (可選)")

    class Meta:
        model = Folder
        fields = ['name', 'description', 'cover_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '資料夾名稱'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': '資料夾描述 (可選)'}),
        }
        labels = {
            'name': '',
            'description': '',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk: # Only for existing folders
            # Get all unique projects bookmarked in this folder
            bookmarked_projects = Project.objects.filter(bookmarked_by__folder=self.instance).distinct()
            
            # Collect all images from these projects
            all_images = ProjectImage.objects.none()
            for project in bookmarked_projects:
                all_images |= project.images.all()
            
            if all_images.count() > 1: # Only show cover_image field if more than 1 image in the folder
                self.fields['cover_image'].queryset = all_images
            else:
                del self.fields['cover_image']
        else:
            # For new folders, or folders without bookmarks, remove the cover_image field
            del self.fields['cover_image']

class BookmarkForm(forms.ModelForm):
    # 移除 folder 和 cover_image 欄位，因為使用者會在「我的收藏」頁面中歸類
    class Meta:
        model = Bookmark
        fields = [] # project field will be hidden and set in view

    def __init__(self, user, *args, **kwargs):
        project_pk = kwargs.pop('project_pk', None) # Get project_pk from kwargs
        super().__init__(*args, **kwargs)
        # 由於 folder 和 cover_image 欄位已被移除，這裡不再需要對它們進行操作
        # self.fields['folder'].queryset = Folder.objects.filter(user=user)
        # if project_pk:
        #     project = Project.objects.get(pk=project_pk)
        #     project_images = project.images.all()
        #     if project_images.count() > 1:
        #         self.fields['cover_image'].queryset = project_images
        #     else:
        #         del self.fields['cover_image']
        # else:
        #     del self.fields['cover_image']

class UserEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '您的新電子郵件'}),
        }
        labels = {
            'email': '電子郵件',
        } 