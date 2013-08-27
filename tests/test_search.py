from yafblog.blog.models import Post, Tag
from yafblog.blog.views import search

from . import TestCase


class TestCaseSearch(TestCase):

    def _add_green_posts(self):
        p1 = Post(
            title='Postgres is the new King',
            slug='postgres-is-king',
            content='Let Postgres rule througout green lands',
        )
        p2 = Post(
            title='Green Vegetables',
            slug='green',
            content='Greens rules',
        )
        self.db.session.add_all([p1, p2])
        self.db.session.commit()

    def test_basic_full_text_search(self):
        self._add_green_posts()
        q = search('Kings of greens')
        assert q.count() == 1

        q = search('greens')
        assert q.count() == 2

    def test_all_post_fields(self):
        p = Post(
            title='cats',
            slug='fats',
            content='rats'
        )
        self.db.session.add(p)
        self.db.session.commit()
        q = search('fat rat cat')
        assert q.count() == 1

    def test_all_post_fields_and_tags(self):
        t1 = Tag('Python')
        t2 = Tag('Make')
        p = Post(
            title='cats',
            slug='fats',
            content='rats'
        )
        p.tags = [t1, t2]
        self.db.session.add_all([p, t1, t2])
        self.db.session.commit()

        p.slug += '-hey'
        self.db.session.add(p)
        self.db.session.commit()

        q = search('fat rat cat makes pythons')
        assert q.count() == 1

    def test_ranking(self):
        self._add_green_posts()
        q = search('GREEN')
        assert q.count() == 2
        first, second = q.all()
        assert first.title == 'Green Vegetables'
        assert second.title == 'Postgres is the new King'

        q = search('rule')
        assert q.count() == 2
        first, second = q.all()
        assert second.title == 'Green Vegetables'
        assert first.title == 'Postgres is the new King'
