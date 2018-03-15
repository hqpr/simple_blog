from django.conf.urls import url

from apps.blog import views

urlpatterns = [
    url(r'^$', views.MainBlogView.as_view()),
    url(r'^(?P<pk>\d*)/$', views.SingleBlogPostView.as_view(), name='single_blog_post'),
    url(r'^add/$', views.AddBlogPostView.as_view(), name='add_blog_post'),
    url(r'^edit/(?P<pk>\d*)/$', views.EditBlogPostView.as_view(), name='edit_blog_post'),
    url(r'^author/(?P<pk>\d*)/$', views.BlogPostByAuthorView.as_view(), name='by_author'),
    url(r'^category/(?P<pk>\d*)/$', views.BlogPostByCategoryView.as_view(), name='by_category'),

    url(r'^search/$', views.SimplerBlogSearchView.as_view(), name='simple_blog_search'),

    url(r'^load_more/$', views.load_more, name='load_more'),

]
