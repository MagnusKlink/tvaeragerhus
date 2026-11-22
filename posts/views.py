from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts.html'
    title = 'Opslagstavle'
    context_object_name = "posts"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for post in context["posts"]:

            post.recent_comments = post.comments.order_by('-created_on')[:3]

        return context

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'post_detail.html'

class AddPostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'add_post.html'
    success_url = reverse_lazy('posts')

    # Set the currently logged in user as author
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'add_comment.html'
    success_url = reverse_lazy('posts')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            slug=self.kwargs['slug'],
        )
        return super().form_valid(form)