import datetime

from yafblog.blog.models import Post, Tag

from . import TestCase
from .test_blog import TestCaseBlog


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


class TestCaseTag(TestCaseBlog):

    def test_tag_by_posts_num(self):
        t1 = Tag.query.get(1)
        t2 = Tag.query.get(2)
        for i, p in enumerate(Post.query.all()):
            if i % 2 == 0:
                p.tags = [t1, t2]
            else:
                p.tags = [t1]

            self.db.session.add(p)
        self.db.session.commit()
        tags = Tag.by_posts_num().all()

        assert tags[0][0] == t1
        assert tags[0][1] == 16

        assert tags[1][0] == t2
        assert tags[1][1] == 8

        # test outerjoin
        assert tags[2][1] == 0
