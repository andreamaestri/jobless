from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()
username = 'ci_test_user'
email = 'ci@example.com'
user, created = User.objects.get_or_create(username=username, defaults={'email': email})
client = Client()
client.force_login(user)
resp = client.get('/jobs/', SERVER_NAME='localhost', HTTP_HOST='localhost', secure=True)
html = resp.content.decode('utf-8')
print('STATUS:'+str(resp.status_code))
print('HAS_EDIT_DRAWER:'+str('Edit (drawer)' in html))
print('HAS_ADD_DRAWER:'+str('Add (drawer)' in html))
print('HAS_PLAN_DRAWER_URL:'+str('/nachweis/plan/drawer/' in html))
