from django.urls import path
from . import views

urlpatterns = [
    path('productivity-guide/', views.ProductivityHomeView.as_view(), name='productivity_guide'),
    path('productivity-guide/topic/<slug:slug>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('productivity-guide/article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
]
