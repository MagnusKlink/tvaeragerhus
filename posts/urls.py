from django.urls import path
from .views import PostListView, PostDetailView, AddPostView, AddCommentView

urlpatterns = [
    path('', PostListView.as_view(), name='posts'),
    path('add-post/', AddPostView.as_view(), name='add_post'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/add-comment', AddCommentView.as_view(), name='add_comment'),
]