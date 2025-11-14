from django.shortcuts import render, get_object_or_404
from .models import Project

def home_view(request):
    from blog.models import Post
    
    featured = Project.objects.filter(featured=True)[:3]
    all_projects = Project.objects.count()  # 統計專案數
    all_posts = Post.objects.filter(published=True).count()  # 統計文章數
    
    return render(request, 'index.html', {
        'featured_projects': featured,
        'projects_count': all_projects,
        'posts_count': all_posts,
    })

def project_list(request):
    all_projects = Project.objects.all()
    featured = Project.objects.filter(featured=True)
    return render(request, 'projects/list.html', {
        'projects': all_projects,
        'featured': featured
    })

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'projects/detail.html', {'project': project})