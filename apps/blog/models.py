from django.db import models
from django.urls import reverse
from django.conf import settings


class Category(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return '%s' % self.title


class Blog(models.Model):
    title = models.CharField(max_length=128)
    text = models.TextField(verbose_name=u'Text')
    category = models.ManyToManyField('Category', blank=True)
    preview = models.ImageField(upload_to='page_preview', blank=True, null=True)
    published = models.BooleanField(default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Blog'

    def get_url(self):
        return reverse('single_blog_post', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return self.get_url()

    def __str__(self):
        return '%s' % self.title
