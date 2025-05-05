from django.db import models

# Create your models here.
# Add these imports at the top
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField  # You'll need to install ckeditor

# Add your models
class Topic(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def str(self):  # Note: Fixed the method name from _str to _str
        return self.title
    
    def get_absolute_url(self):
        return reverse('topic_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Article(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True)
    topic = models.ForeignKey(Topic, related_name='articles', on_delete=models.CASCADE)
    content = RichTextField()
    image = models.ImageField(upload_to='article_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def str(self):  # Fixed method name
        return self.title
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'topic_slug': self.topic.slug, 'slug':self.slug})
