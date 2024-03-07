from app import app
import unittest
from unittest.mock import patch


class TestFrontendRender(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_widget1(self):
        response = self.client.get('/widget1')
        self.assertEqual(response.status_code, 200)

    def test_widget2(self):
        response = self.client.get('/widget2')
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.client.get('/logoutresult')
        self.assertEqual(response.status_code, 200)

    def test_map(self):
        response = self.client.get('/map')
        self.assertEqual(response.status_code, 200)

    def test_country(self):
        response = self.client.get('/country')
        self.assertEqual(response.status_code, 200)


class TestMock(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    @patch('app.requests.get')
    def test_successful_register(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = 'Registration successful'

        response = self.client.post('/submit_register', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertIn(b'Registration successful', response.data)

    @patch('app.requests.get')
    def test_failed_register(self, mock_get):
        mock_get.return_value.status_code = 400
        mock_get.return_value.text = 'Registration failed'

        response = self.client.post('/submit_register', data=dict(
            username='invaliduser',
            password='weakpassword'
        ), follow_redirects=True)

        self.assertIn(b'Registration failed', response.data)

    @patch('app.requests.get')
    def test_successful_login(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {'Authorization': 'Bearer test_token'}

        response = self.client.post('/submit_login', data={
            'username': 'validUser',
            'password': 'validPassword'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/' in response.headers['Location'])

    @patch('app.requests.get')
    def test_failed_login(self, mock_get):
        mock_get.return_value.status_code = 401
        mock_get.return_value.text = 'Login failed'

        response = self.client.post('/submit_login', data={
            'username': 'invalidUser',
            'password': 'wrongPassword'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login' in response.headers['Location'])

    @patch('app.requests.get')
    def test_logout(self, mock_get):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['auth_token'] = 'existing_token'
                sess['username'] = 'testUser'

        mock_get.return_value.status_code = 200
        mock_get.return_value.text = 'Successfully logged out'

        response = self.client.post('/logout', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/logoutresult' in response.headers['Location'])

    @patch('app.requests.get')
    def test_profile_access_unauthorized(self, mock_get):
        mock_get.return_value.status_code = 401
        mock_get.return_value.json.return_value = {
            'message': 'You are not authorized to view this page.'}

        response = self.client.get('/profile', follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login' in response.headers['Location'])

    @patch('app.requests.get')
    def test_profile_access_authorized(self, mock_get):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['auth_token'] = 'valid_token'
                sess['username'] = 'validUser'

        mock_get.return_value.status_code = 400

        response = self.client.get('/profile', follow_redirects=False)

        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
