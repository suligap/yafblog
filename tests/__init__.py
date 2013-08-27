from yafblog import app, db


class TestCase(object):

    def setup_method(self, method):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            'postgresql://localhost/yafblog-test-db'
        self.app = app
        self._ctx = app.test_request_context()
        self._ctx.push()
        self.db = db
        db.create_all()
        self.client = self.app.test_client()

    def teardown_method(self, method):
        db.session.remove()
        db.drop_all()
        self._ctx.pop()

    def assert_status(self, response, status_code):
        assert response.status_code == status_code

    def assert_redirects(self, response, location):
        self.assert_status(response, 302)
        assert response.location == "http://localhost" + location

    def assert_200(self, response):
        self.assert_status(response, 200)

    def assert_404(self, response):
        self.assert_status(response, 404)

    def assert_redirects_to_login(self, response):
        self.assert_status(response, 302)
        assert response.location.startswith(
            'http://localhost/auth/login?next=')
