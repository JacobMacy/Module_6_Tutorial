from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Post


class PostListTests(TestCase):
    def test_published_posts_are_ordered_and_drafts_and_future_posts_are_hidden(self):
        author = get_user_model().objects.create_user(username='test-author')
        now = timezone.now()
        later = Post.objects.create(author=author, title='Later post', text='First line\nSecond line <script>', published_date=now - timedelta(days=1))
        earlier = Post.objects.create(author=author, title='Earlier post', text='Hello', published_date=now - timedelta(days=2))
        Post.objects.create(author=author, title='Hidden draft', text='Draft')
        Post.objects.create(author=author, title='Scheduled post', text='Future', published_date=now + timedelta(days=1))
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['posts']), [earlier, later])
        self.assertTemplateUsed(response, 'blog/post_list.html')
        self.assertTemplateUsed(response, 'blog/base.html')
        self.assertContains(response, 'First line<br>Second line &lt;script&gt;')
        self.assertContains(response, '/static/css/blog.css')
        self.assertNotContains(response, 'Hidden draft')
        self.assertNotContains(response, 'Scheduled post')

    def test_empty_blog_renders_shared_header(self):
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Girls Blog')
