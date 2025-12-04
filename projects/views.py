from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, inlineformset_factory
from django.db.models import Q
from .models import Project, ProjectImage, Folder, Bookmark
from .forms import ProjectForm, ProjectImageForm, FolderForm, BookmarkForm, UserEmailForm
from django.contrib import messages

# Create your views here.

def home(request):
    recent_projects = Project.objects.order_by('-created_at')[:5] # Get 5 most recent projects
    context = {
        'recent_projects': recent_projects
    }
    return render(request, 'projects/home.html', context)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home') # Redirect to home page after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

ProjectImageFormSet = inlineformset_factory(Project, ProjectImage, form=ProjectImageForm, extra=3, max_num=10, fields=('image', 'is_key_image'))
ProjectImageFormSetForEdit = inlineformset_factory(Project, ProjectImage, form=ProjectImageForm, extra=1, max_num=10, can_delete=True, fields=('image', 'is_key_image'))

@login_required
def create_project(request):
    if request.method == 'POST':
        project_form = ProjectForm(request.POST)
        formset = ProjectImageFormSet(request.POST, request.FILES)

        if project_form.is_valid() and formset.is_valid():
            project = project_form.save(commit=False)
            project.author = request.user
            project.save()
            formset.instance = project # Associate formset with the newly created project
            formset.save()

            return redirect('home') # Redirect to home or project detail page
    else:
        project_form = ProjectForm()
        formset = ProjectImageFormSet()

    context = {
        'project_form': project_form,
        'formset': formset,
        'is_edit': False, # Add a context variable to indicate if it's an edit view
    }
    return render(request, 'projects/project_form.html', context)

@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk, author=request.user) # Ensure only author can edit

    if request.method == 'POST':
        project_form = ProjectForm(request.POST, instance=project)
        formset = ProjectImageFormSetForEdit(request.POST, request.FILES, instance=project)

        if project_form.is_valid() and formset.is_valid():
            project_form.save()
            formset.save()
            return redirect('project_detail', pk=project.pk)
    else:
        project_form = ProjectForm(instance=project)
        formset = ProjectImageFormSetForEdit(instance=project)

    context = {
        'project_form': project_form,
        'formset': formset,
        'project': project, # Pass project instance for potential use in template
        'is_edit': True, # Indicate that this is an edit view
    }
    return render(request, 'projects/project_form.html', context)

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    key_images = project.images.filter(is_key_image=True).order_by('id')[:5] # Get up to 5 key images
    all_images = project.images.all().order_by('id')

    is_bookmarked = False
    bookmark_pk = None
    bookmark_form = None # 為未登入使用者預設為 None

    if request.user.is_authenticated:
        bookmark = Bookmark.objects.filter(user=request.user, project=project).first()
        if bookmark:
            is_bookmarked = True
            bookmark_pk = bookmark.pk
        else:
            is_bookmarked = False
            bookmark_pk = None

        bookmark_form = BookmarkForm(request.user, initial={'project': project.pk})

    context = {
        'project': project,
        'key_images': key_images,
        'all_images': all_images,
        'is_bookmarked': is_bookmarked,
        'bookmark_form': bookmark_form,
        'bookmark_pk': bookmark_pk, # Pass bookmark_pk to the template
    }
    return render(request, 'projects/project_detail.html', context)

def search_projects(request):
    query = request.GET.get('q')
    projects = Project.objects.all()
    if query:
        projects = projects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(project_type__icontains=query) |
            Q(region__icontains=query)
        ).distinct()
    context = {
        'query': query,
        'projects': projects
    }
    return render(request, 'projects/search_results.html', context)

@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user
            cover_image = form.cleaned_data.get('cover_image')
            if cover_image: # Assign cover_image if selected
                folder.cover_image = cover_image
            folder.save()
            return redirect('folder_list')
    else:
        form = FolderForm()
    context = {'form': form}
    return render(request, 'projects/create_folder.html', context)

@login_required
def folder_list(request):
    folders = Folder.objects.filter(user=request.user).order_by('name')
    for folder in folders:
        first_bookmark = folder.bookmarks.first()
        if first_bookmark and first_bookmark.project.images.first():
            folder.cover_image_url = first_bookmark.project.images.first().image.url
        else:
            folder.cover_image_url = None

    # Get all bookmarks for the user, regardless of folder
    user_bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'folders': folders,
        'user_bookmarks': user_bookmarks,  # Changed from 'standalone_bookmarks'
        'folder_form': FolderForm() # For creating new folders on the same page
    }
    return render(request, 'projects/folder_list.html', context)

@login_required
def folder_detail(request, pk):
    folder = get_object_or_404(Folder, pk=pk, user=request.user) # Ensure only owner can view
    bookmarks_in_folder = Bookmark.objects.filter(folder=folder).order_by('-created_at')
    for bookmark in bookmarks_in_folder:
        if bookmark.cover_image:
            bookmark.display_image_url = bookmark.cover_image.url
        elif bookmark.project.images.first():
            bookmark.display_image_url = bookmark.project.images.first().image.url
        else:
            bookmark.display_image_url = None

    context = {
        'folder': folder,
        'bookmarks_in_folder': bookmarks_in_folder,
    }
    return render(request, 'projects/folder_detail.html', context)

@login_required
def add_to_folder(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = BookmarkForm(request.user, request.POST, project_pk=project.pk)
        if form.is_valid():
            # 檢查或創建「所有收藏作品」資料夾
            default_folder, created = Folder.objects.get_or_create(
                user=request.user,
                name="所有收藏作品",
                defaults={'description': '自動創建的資料夾，用於存放所有收藏的作品。'} # 可選的預設描述
            )
            
            # 檢查此專案是否已被收藏過 (無論在哪個資料夾，但現在我們只關心是否已在預設資料夾)
            existing_bookmark = Bookmark.objects.filter(user=request.user, project=project, folder=default_folder).first()

            if not existing_bookmark:
                bookmark = form.save(commit=False)
                bookmark.user = request.user
                bookmark.project = project
                bookmark.folder = default_folder # 將收藏直接關聯到預設資料夾
                bookmark.save()
            return redirect('project_detail', pk=project.pk)
    # 對於 GET 請求或無效表單，也應該重定向回專案詳情頁面
    return redirect('project_detail', pk=project.pk)

@login_required
def remove_bookmark(request, bookmark_pk):
    bookmark = get_object_or_404(Bookmark, pk=bookmark_pk, user=request.user)
    project_pk = bookmark.project.pk # Get project_pk before deleting bookmark
    bookmark.delete()
    # Redirect to folder list if coming from there, otherwise to project detail
    if 'HTTP_REFERER' in request.META and 'folders/' in request.META['HTTP_REFERER']:
        return redirect('folder_list')
    return redirect('project_detail', pk=project_pk)

@login_required
def user_profile(request):
    # 獲取當前用戶上傳的所有作品
    uploaded_projects = Project.objects.filter(author=request.user).order_by('-created_at')
    for project in uploaded_projects:
        first_image = project.images.first()
        if first_image and first_image.image:
            project.first_image_url = first_image.image.url
        else:
            project.first_image_url = None

    # 獲取當前用戶的所有收藏，並按資料夾分組 (或者未分類)
    user_bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')
    bookmarked_projects = [bookmark.project for bookmark in user_bookmarks]
    for project in bookmarked_projects:
        first_image = project.images.first()
        if first_image and first_image.image:
            project.first_image_url = first_image.image.url
        else:
            project.first_image_url = None

    # 獲取當前用戶的資料夾數量
    user_folders_count = Folder.objects.filter(user=request.user).count()
    user_folders = Folder.objects.filter(user=request.user).order_by('name')
    for folder in user_folders:
        first_bookmark = folder.bookmarks.first()
        if first_bookmark and first_bookmark.project.images.first():
            folder.cover_image_url = first_bookmark.project.images.first().image.url
        else:
            folder.cover_image_url = None
    
    # Initialize email form
    email_form = UserEmailForm(instance=request.user)

    if request.method == 'POST':
        if 'update_email' in request.POST: # Check if the request is for email update
            email_form = UserEmailForm(request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, '您的電子郵件已成功更新。')
                return redirect('user_profile') # Redirect to refresh page and show message
            else:
                messages.error(request, '更新電子郵件時發生錯誤。')

    context = {
        'uploaded_projects': uploaded_projects,
        'user_bookmarks': user_bookmarks,
        'user_folders_count': user_folders_count,
        'folders': user_folders, # Pass user_folders to the template
        'email_form': email_form, # Pass the email form to the template
    }
    return render(request, 'projects/user_profile.html', context)

@login_required
def edit_folder(request, pk):
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder)
        if form.is_valid():
            cover_image = form.cleaned_data.get('cover_image')
            if cover_image: # Assign cover_image if selected
                folder.cover_image = cover_image
            else: # If no cover image is selected (and the field was present), clear it
                # This handles cases where the user might unselect a previously chosen image
                # or if the form didn't display the field because there was only one image.
                # However, the form's __init__ should handle removing the field if it's not applicable.
                # So, if cover_image is None here, it means it was either not selected or the field wasn't displayed.
                # We only clear if the field was actually in the form and explicitly made None.
                # For simplicity, we can just save whatever is in cleaned_data if the field was present.
                # If the field was removed by __init__, it won't be in cleaned_data.
                # The simplest approach is to just let form.save() handle it, but if we want to explicitly clear it when unselected,
                # we need to check if 'cover_image' was actually in form.fields.
                if 'cover_image' in form.fields and form.cleaned_data.get('cover_image') is None and folder.cover_image:
                    folder.cover_image = None

            form.save()
            return redirect('folder_list') # Redirect to folder list after editing
    else:
        form = FolderForm(instance=folder)
    context = {
        'form': form,
        'folder': folder,
    }
    return render(request, 'projects/edit_folder.html', context)

@login_required
def delete_folder(request, pk):
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    if request.method == 'POST':
        folder.delete()
        return redirect('folder_list')
    context = {
        'folder': folder
    }
    return render(request, 'projects/delete_folder.html', context)

@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk, author=request.user) # 確保只有作者能刪除
    if request.method == 'POST':
        project.delete()
        return redirect('user_profile') # 刪除後重定向到用戶個人資料頁面
    # 如果是 GET 請求，渲染確認刪除的頁面
    context = {
        'project': project
    }
    return render(request, 'projects/delete_project.html', context)
