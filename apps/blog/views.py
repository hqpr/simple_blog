import operator
from functools import reduce

import re
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
        if self.request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        obj = self.get_object()
        if obj.author != self.request.user:
            return HttpResponseForbidden()
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse('index')


def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    """
    Splits the query string in invidual keywords, getting rid of unecessary spaces
    and grouping quoted words together.
    Example:
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    """
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):

    """
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
    """
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


class SimplerBlogSearchView(ListView):
    model = Blog
    template_name = 'blog/blog_list.html'
    paginate_by = 3

    def get_queryset(self):
        queryset = super(SimplerBlogSearchView, self).get_queryset()

        found_entries = None
        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']

            entry_query = get_query(query_string, ['title', 'text', ])

            found_entries = queryset.filter(entry_query)

        return found_entries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Search'
        return context


@csrf_exempt
def load_more(request):
    page = request.POST.get('page')
    url = request.POST.get('url')

    posts = Blog.objects.filter(published=True).order_by('-created_at')

    try:
        item_id = url.split('/')[-2]
        page_type = url.split('/')[-3]

        if all([url, item_id, page_type]):
            if page_type == 'author':
                posts = Blog.objects.filter(published=True, author_id=item_id).order_by('-created_at')
            elif page_type == 'category':
                posts = Blog.objects.filter(published=True, category__in=item_id).order_by('-created_at')
    except IndexError:
        pass

    paginator = Paginator(posts, 3)
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
