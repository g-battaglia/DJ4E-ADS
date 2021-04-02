from django.urls import path, reverse_lazy
from .views import *
from . import views

app_name='ads'
urlpatterns = [
    path('', views.adListView.as_view(), name='all'),
    path('ad/<int:pk>', views.adDetailView.as_view(), name='ad_detail'),
    path('ad/create', 
        views.adCreateView.as_view(success_url=reverse_lazy('ads:all')), name='ad_create'),
    path('ad/<int:pk>/update', 
        views.adUpdateView.as_view(success_url=reverse_lazy('ads:all')), name='ad_update'),
    path('ad/<int:pk>/delete', 
        views.adDeleteView.as_view(success_url=reverse_lazy('ads:all')), name='ad_delete'),
    
    #Comments:
    path('ad/<int:pk>/comment', 
        views.CommentCreateView.as_view(), name='ad_comment_create'),
    path('ad/<int:pk>/delete_comment', 
        views.CommentDeleteView.as_view(success_url=reverse_lazy('ad:all')), name='ad_comment_delete'),
    
    # Favorites:
    path('ad/<int:pk>/favorite',
    views.AddFavoriteView.as_view(), name='ad_favorite'),
    path('ad/<int:pk>/unfavorite',
    views.DeleteFavoriteView.as_view(), name='ad_unfavorite'),
]

# We use reverse_lazy in urls.py to delay looking up the view until all the paths are defined