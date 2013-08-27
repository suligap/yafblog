import datetime

from yafblog.blog.models import Post

from . import TestCase


class TestCasePost(TestCase):

    def setup_method(self, method):
        super(TestCasePost, self).setup_method(method)
        added = datetime.date(2000, 1, 1)
        p = Post('Title', 'a-slug', 'content', added)
        self.db.session.add(p)
        self.db.session.commit()
        self.post = p

    def test_get_by_url(self):
        assert Post.get_by_url(2000, 1, 1, 'a-slug') == self.post
        assert Post.get_by_url(2000, 2, 1, 'a-slug') is None

    def test_url_show(self):
        assert self.post.url_show == '/2000/1/1/a-slug'
