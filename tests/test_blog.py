import datetime

from yafblog.blog.models import Post, Tag

from .test_login import TestCaseAuth


class TestCaseBlog(TestCaseAuth):

    def setup_method(self, method):
        super(TestCaseBlog, self).setup_method(method)
        self._add_posts()

    def _add_posts(self):
        for i in xrange(10):
            tag = Tag('Tag-%s' % i)
            self.db.session.add(tag)

        content = u'<p>Content %s</p>'
        added = datetime.date(2000, 1, 1)
        for i in xrange(16):
            p = Post(
                'Title number %s' % i,
                slug='slug-%s-slug' % i,
                content=content % i,
                added=added,
            )
            self.db.session.add(p)

        self.db.session.commit()


class TestCasePostList(TestCaseBlog):

    def test_get(self):
        self.assert_200(self.client.get('/'))
        self.assert_200(self.client.get('/p/2'))
        self.assert_200(self.client.get('/tag/1'))
        self.assert_200(self.client.get('/tag/1/p/1'))

    def test_get_search(self):
        r = self.client.get('/?q=content+search')
        self.assert_200(r)
        assert 'Search results for: <em>content+search</em>'


class TestCasePost(TestCaseBlog):

    def test_show_content_unescaped(self):
        p = Post.query.get(1)
        r = self.client.get(p.url_show)
        self.assert_200(r)
        assert '<p>Content 0</p>' in r.data

    def test_show_200(self):
        r = self.client.get('/2000/1/1/slug-0-slug')
        self.assert_200(r)

    def test_show_404(self):
        r = self.client.get('/2000/10/10/slug-0-slug')
        self.assert_404(r)

    def test_add_unauthorized(self):
        r = self.client.post('/post/add', data={})
        self.assert_redirects_to_login(r)
        r = self.client.get('/post/add')
        self.assert_redirects_to_login(r)

    def test_add_valid(self):
        self.login()

        r = self.client.get('/post/add')
        self.assert_200(r)

        r = self.client.post('/post/add', data={
            'added': '2022-10-20',
            'title': 'New Monkey',
            'slug': 'a-monkey',
            'content': 'banana',
        }, follow_redirects=False)
        self.assert_redirects(r, '/2022/10/20/a-monkey')

        r = self.client.get(r.location)
        self.assert_200(r)

    def test_add_bad_slug(self):
        self.login()
        r = self.client.post('/post/add', data={
            'added': '2022-10-20',
            'title': 'New Monkey',
            'slug': 'bad_monkey',
            'content': 'banana',
        }, follow_redirects=False)
        self.assert_200(r)
        msg = 'Only digits, lower case letters and hyphens are allowed.'
        assert msg in r.data

    def test_edit_unauthorized(self):
        r = self.client.get('/post/1/edit')
        self.assert_redirects_to_login(r)
        r = self.client.post('/post/1/edit', data={})
        self.assert_redirects_to_login(r)

    def test_edit_404(self):
        self.login()
        r = self.client.get('/post/100/edit')
        self.assert_404(r)
        r = self.client.get('/post/post/edit')
        self.assert_404(r)

    def test_edit_200(self):
        self.login()
        r = self.client.get('/post/1/edit')
        self.assert_200(r)

    def test_edit_post(self):
        self.login()
        r = self.client.post('/post/1/edit', data={
            'added': '2012-12-31',
            'title': 'Coconut Hunt',
            'slug': 'a-coconut',
            'content': 'nothing',
        }, follow_redirects=False)
        self.assert_redirects(r, '/2012/12/31/a-coconut')

        r = self.client.get(r.location)
        self.assert_200(r)

    def test_post_delete_unauthorized(self):
        r = self.client.get('/post/1/delete')
        self.assert_redirects_to_login(r)
        r = self.client.post('/post/1/delete')
        self.assert_redirects_to_login(r)

    def test_post_delete_valid(self):
        self.login()
        r = self.client.get('/post/1/delete')
        self.assert_200(r)
        msg = 'Are you sure you want to delete Post: Title number 0?'
        assert msg in r.data
        r = self.client.post('/post/1/delete')
        self.assert_redirects(r, '/')
        assert Post.query.filter(Post.id == 1).first() is None


class TestCaseTag(TestCaseBlog):

    def test_tag_list(self):
        r = self.client.get('/tags')
        self.assert_200(r)
        assert 'Tag-1 (0)' in r.data
        assert 'href="/tag/1"' in r.data

    def test_tag_add_unauthorized(self):
        r = self.client.get('/tag/add')
        self.assert_redirects_to_login(r)

    def test_tag_add_valid(self):
        self.login()
        r = self.client.get('/tag/add')
        self.assert_200(r)
        r = self.client.post('/tag/add', data={'name': 'BlueOrYellow'})
        self.assert_redirects(r, '/tags')
        assert Tag.query.get(11).name == 'BlueOrYellow'

    def test_tag_add_unique_name(self):
        self.login()
        r = self.client.post('/tag/add', data={'name': 'Tag-1'})
        self.assert_200(r)
        assert 'Already exists.' in r.data

    def test_tag_edit_unauthorized(self):
        r = self.client.get('/tag/1/edit')
        self.assert_redirects_to_login(r)
        r = self.client.post('/tag/1/edit')
        self.assert_redirects_to_login(r)

    def test_tag_edit_valid(self):
        self.login()
        r = self.client.get('/tag/1/edit')
        self.assert_200(r)
        r = self.client.post('/tag/1/edit', data={'name': 'Tag-101'})
        self.assert_redirects(r, '/tags')
        assert Tag.query.get(1).name == 'Tag-101'

    def test_tag_delete_unauthorized(self):
        r = self.client.get('/tag/1/delete')
        self.assert_redirects_to_login(r)
        r = self.client.post('/tag/1/delete')
        self.assert_redirects_to_login(r)

    def test_tag_delete_valid(self):
        self.login()
        r = self.client.get('/tag/1/delete')
        self.assert_200(r)
        assert 'Are you sure you want to delete Tag: Tag-0?' in r.data
        r = self.client.post('/tag/1/delete')
        self.assert_redirects(r, '/tags')
        assert Tag.query.filter(Tag.id == 1).first() is None


class TestCasePostTags(TestCaseBlog):

    def test_post_tags_unauthorized(self):
        r = self.client.get('/post/1/tags')
        self.assert_redirects_to_login(r)

    def test_post_tags_add(self):
        self.login()
        r = self.client.get('/post/1/tags')
        self.assert_200(r)
        assert Post.query.get(1).tags == []

        r = self.client.post('/post/1/tags', data={
            'tags': ['1', '3'],
        })
        self.assert_redirects(r, '/2000/1/1/slug-0-slug')
        assert Post.query.get(1).tags == [Tag.query.get(1), Tag.query.get(3)]

    def test_post_tags_remove(self):
        p = Post.query.get(1)
        p.tags = [Tag.query.get(1), Tag.query.get(2)]
        self.db.session.add(p)
        self.db.session.commit()

        self.login()
        r = self.client.post('/post/1/tags', data={
            'tags': [],
        })
        self.assert_redirects(r, '/2000/1/1/slug-0-slug')
        assert Post.query.get(1).tags == []
