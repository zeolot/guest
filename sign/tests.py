from django.test import TestCase
from sign.models import Event, Guest
from django.contrib.auth.models import User


# Create your tests here.
class ModelTest(TestCase):
    def setUp(self):
        Event.objects.create(id=1, name='oneplus 3 event', status=True, limit=200,
                             address='shenzhen', start_time='2016-08-31 14:00:00')
        Guest.objects.create(id=1, event_id=1, realname='allen', phone='13012341234',
                             email='alen@mail.com', sign=False)

    def test_event_models(self):
        result = Event.objects.get(name='oneplus 3 event')
        self.assertEqual(result.address, 'shenzhen')
        self.assertTrue(result.status)

    def test_guest_models(self):
        result = Guest.objects.get(phone='13012341234')
        self.assertEqual(result.realname, 'allen')
        self.assertFalse(result.sign)


class IndexPageTest(TestCase):
    """
    测试index登录首页
    """

    def test_index_page_renders_index_template(self):
        """
        测试index视图
        """
        response = self.client.get('/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class LoginActionTest(TestCase):
    """
    测试登录动作
    """

    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123123')

    def test_add_admin(self):
        """
        测试添加用户
        """
        user = User.objects.get(username='admin')
        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.realname, 'admin@mail.com')

    def test_login_action_username_password_null(self):
        """
        测试用户名密码为空的情况
        """
        test_data = {'username': '',
                     'password': ''}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error!', response.content)

    def test_login_action_username_password_error(self):
        """
        测试用户名密码错误的情况
        """
        test_data = {'username': 'admin',
                     'password': '123'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error!', response.content)

    def test_login_action_success(self):
        """
        登录成功
        """
        test_data = {'username': 'admin',
                     'password': 'admin123123'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 302)


class EventManageTest(TestCase):
    """
    测试发布会管理
    """

    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123123')
        Event.objects.create(id=1, name='xiaomi5', limit=300, address='beijing',
                             status=1, start_time='2017-8-10 12:30:00')
        self.login_user = {'username': 'admin', 'password': 'admin123123'}

    def test_event_manage_success(self):
        """
        测试发布会:xiaomi5
        """
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/event_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'xiaomi5', response.content)
        self.assertIn(b'beijing', response.content)

    def test_event_manage_search_success(self):
        """
        测试发布会搜索
        """
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('search_name', {'name': 'xiaomi5'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'xiaomi5', response.content)
        self.assertIn(b'beijing', response.content)


class GuestManageTest(TestCase):
    """
    测试嘉宾管理
    """

    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123123')
        Event.objects.create(id=1, name='xiaomi5', limit=300, address='beijing',
                             status=1, start_time='2017-8-10 12:30:00')
        Guest.objects.create(realname='allen', phone='13012341234',
                             email='alen@mail.com', sign=0, event_id=1)
        self.login_user = {'username': 'admin', 'password': 'admin123123'}

    def test_guest_manage_success(self):
        """
        测试嘉宾信息:allen
        """
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/guest_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'allen', response.content)
        self.assertIn(b'13012341234', response.content)


class SignIndexActionTest(TestCase):
    """
    测试发布会签到
    """

    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123123')
        Event.objects.create(id=1, name='xiaomi5', limit=300, address='beijing',
                             status=1, start_time='2017-8-10 12:30:00')
        Event.objects.create(id=2, name='oneplus4', limit=200, address='shenzhen',
                             status=1, start_time='2017-6-10 12:30:00')
        Guest.objects.create(realname='allen', phone='13012341234',
                             email='alen@mail.com', sign=0, event_id=1)
        Guest.objects.create(realname='jack', phone='13012341230',
                             email='alen@mail.com', sign=1, event_id=2)
        self.login_user = {'username': 'admin', 'password': 'admin123123'}

    def test_sign_index_action_phone_null(self):
        """
        测试手机号为空的情况
        """
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/1/', {'phone': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'phone error', response.content)

    def test_sign_index_action_phone_or_event_id_error(self):
        """
        手机号或发布会id错误的情况
        """
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {'phone': '13012341234'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'event id or phone error', response.content)

    def test_sign_index_action_user_has_signed(self):
        """
        用户已签到的情况
        """
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {'phone': '13012341230'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'user has sign in.', response.content)

    def test_sign_index_action_sign_success(self):
        """
        签到成功的情况
        """
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/1/', {'phone': '13012341234'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'sign in success!', response.content)
