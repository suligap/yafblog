from . import TestCase

from yafblog.auth.models import User


class TestCaseAuth(TestCase):

    def setup_method(self, method):
        super(TestCaseAuth, self).setup_method(method)
        u = User('arthur', 'arthur@roundtable.uk', 'graal')
        self.db.session.add(u)
        self.db.session.commit()

    def login(self, username='arthur', password='graal', url='/auth/login',
              redirect=True):
        return self.client.post(url, data={
            'username': username,
            'password': password
        }, follow_redirects=redirect)


class TestCaseLogin(TestCaseAuth):

    def test_login_get(self):
        r = self.client.get('/auth/login')
        self.assert_200(r)
        assert 'action="/auth/login"' in r.data

    def test_login_post_valid(self):
        r = self.login(redirect=False)
        self.assert_redirects(r, '/')
        r = self.client.get(r.location)
        assert 'Hi arthur!' in r.data

    def test_login_post_valid_next(self):
        r = self.login(url='/auth/login?next=/more-coconuts', redirect=False)
        self.assert_redirects(r, '/more-coconuts')

    def test_login_post_invalid(self):
        r = self.login(password='coconut')
        self.assert_200(r)
        assert 'Wrong username or password' in r.data

    def test_login_post_invalid_next(self):
        r = self.login(
            password='coconut',
            url='/auth/login?next=/more-coconuts',
        )
        self.assert_200(r)
        assert 'Wrong username or password' in r.data
        assert 'action="/auth/login?next=%2Fmore-coconuts"' in r.data

    def test_logout_logged_out(self):
        r = self.client.get('/auth/logout')
        self.assert_redirects(r, '/auth/login?next=%2Fauth%2Flogout')

    def test_logout_logged_in(self):
        self.login()
        r = self.client.get('/auth/logout')
        self.assert_redirects(r, '/')
        r = self.client.get(r.location)
        assert 'You were logged out.' in r.data
