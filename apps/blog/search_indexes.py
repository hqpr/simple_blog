from haystack import indexes
from .models import Blog


class BlogIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    author = indexes.CharField(model_attr='author')
    body = indexes.CharField(model_attr='text')
    category = indexes.MultiValueField(null=True)
    created_at = indexes.DateTimeField(model_attr='created_at')

    def get_model(self):
        return Blog

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(published=True)
