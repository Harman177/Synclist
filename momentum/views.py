from django.views.generic import ListView, DetailView
from .models import Topic, Article

class ProductivityHomeView(ListView):
    model = Article
    template_name = 'momentum/productivity_guide/home.html'
    context_object_name = 'featured_article'

    def get_queryset(self):
        # Get most recent article as featured
        return Article.objects.order_by('-created_at').first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        return context

class TopicDetailView(DetailView):
    model = Topic
    template_name = 'momentum/productivity_guide/topic.html'
    context_object_name = 'topic'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        context['articles'] = Article.objects.filter(topic=self.object)
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'momentum/productivity_guide/article.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        return context