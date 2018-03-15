import operator
from functools import reduce

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.template import loader
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .models import Blog, Category
from .forms import BlogForm

User = get_user_model()


class MainBlogView(ListView):
    model = Blog
    paginate_by = 3
    queryset = Blog.objects.filter(published=True).order_by('-created_at')


class SingleBlogPostView(DetailView):
    model = Blog
    template_name = 'blog/blog_item.html'
    context_object_name = 'blog'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        is_owner = False
        if self.request.user == obj.author:
            is_owner = True
        context['is_owner'] = is_owner
        return context


class AddBlogPostView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm

    def get_success_url(self, **kwargs):
        return reverse('index')

    def get_initial(self):
        initial_data = super(AddBlogPostView, self).get_initial()
        initial_data['author'] = self.request.user
        return initial_data

    def get_form_kwargs(self):
        kwargs = super(AddBlogPostView, self).get_form_kwargs()
        kwargs.update(
            {'initial':
                 {'author': self.request.user}
             }
        )
        return kwargs


class BlogPostByAuthorView(ListView):
    model = Blog
    paginate_by = 3

    def get_queryset(self, **kwargs):
        super().get_queryset()
        return Blog.objects.filter(author_id=self.kwargs.get('pk')).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = User.objects.get(pk=self.kwargs.get('pk'))
        context['title'] = 'Blog Posts By {}'.format(author)
        return context


class BlogPostByCategoryView(ListView):
    model = Blog
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = Category.objects.get(pk=self.kwargs.get('pk'))
        context['title'] = 'Blog Posts in {}'.format(author)
        return context

    def get_queryset(self, **kwargs):
        super().get_queryset()
        return Blog.objects.filter(category__in=self.kwargs.get('pk')).order_by('-created_at')


class EditBlogPostView(LoginRequiredMixin, UpdateView):
    model = Blog
    form_class = BlogForm

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user or not self.request.user.is_superuser:
            return HttpResponseForbidden()
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse('index')


class SimplerBlogSearchView(ListView):
    model = Blog
    paginate_by = 3

    def get_queryset(self):
        result = super(SimplerBlogSearchView, self).get_queryset()

        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(title__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(text__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(author__username__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(category__title__icontains=q) for q in query_list))
            )

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Search'
        return context


@csrf_exempt
def load_more(request):
    page = request.POST.get('page')
    posts = Blog.objects.filter(published=True)[:3]
    results_per_page = 3
    paginator = Paginator(posts, results_per_page)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(2)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    posts_html = loader.render_to_string('blog/posts.html', {'posts': posts})
    output_data = {
        'posts_html': posts_html,
        'has_next': posts.has_next()
    }
    return JsonResponse(output_data)
