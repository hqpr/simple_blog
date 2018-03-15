from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .models import Blog, Category

User = get_user_model()


class BlogTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test',
                                        email='test@test.com', is_active=True)
        self.user.set_password('1234567a')
        self.user.save()

        self.author = User.objects.create(username='author',
                                          email='author@test.com', is_active=True)
        self.author.set_password('1234567a')
        self.author.save()

        self.admin = User.objects.create(username='admin',
                                         email='admin@test.com', is_active=True,
                                         is_superuser=True, is_staff=True)
        self.admin.set_password('1234567a')
        self.admin.save()

        self.category = Category.objects.create(title='Music')

        self.published_post = Blog.objects.create(title='Test Post', text='Some Text', published=True,
                                                  author=self.author)
        self.published_post.category.add(self.category)
        self.unpublished_post = Blog.objects.create(title='Hidden Post', text='Another Text', published=False,
                                                    author=self.author)
        self.client = Client()

    def test_main_page_success_open(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_add_post_anonymous_redirect(self):
        response = self.client.get(reverse('add_blog_post'))
        self.assertEqual(response.status_code, 302)

    def test_edit_post_not_owner_forbidden(self):
        self.client.login(username='test', password='1234567a')
        response = self.client.get(reverse('edit_blog_post', kwargs={'pk': self.published_post.id}))
        self.assertEqual(response.status_code, 403)

    def test_edit_post_anonymous_forbidden(self):
        response = self.client.get(reverse('edit_blog_post', kwargs={'pk': self.published_post.id}))
        self.assertEqual(response.status_code, 403)

    def test_post_owner_can_edit(self):
        self.client.login(username='author', password='1234567a')
        response = self.client.get(reverse('edit_blog_post', kwargs={'pk': self.published_post.id}))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_edit(self):
        self.client.login(username='admin', password='1234567a')
        response = self.client.get(reverse('edit_blog_post', kwargs={'pk': self.published_post.id}))
        self.assertEqual(response.status_code, 200)

    def test_unpublished_post_is_hidden(self):
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'Hidden Post')

    def test_published_post_is_visible(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Test Post')

    def test_simple_search_one_word(self):
        url = '{}?q=Test'.format(reverse('simple_blog_search'))
        response = self.client.get(url)
        self.assertContains(response, 'Test Post')

    def test_post_is_in_category_page(self):
        response = self.client.get(reverse('by_category', kwargs={'pk': self.category.id}))
        self.assertContains(response, 'Test Post')

    def test_post_is_not_in_category_page(self):
        self.unpublished_post.published = True
        self.unpublished_post.save()
        response = self.client.get(reverse('by_category', kwargs={'pk': self.category.id}))
        self.assertNotContains(response, 'Hidden Post')
