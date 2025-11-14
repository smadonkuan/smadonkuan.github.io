from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    github_url = models.URLField()
    demo_url = models.URLField(blank=True, null=True)
    technologies = models.CharField(max_length=300, help_text="以逗號分隔，例如: Python, Django, React")
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_technologies(self):
        return [tech.strip() for tech in self.technologies.split(',')]
    
    def __str__(self):
        return self.title