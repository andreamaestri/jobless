from django.contrib.auth import get_user_model
from django.test import Client
from jobs.models import Application
from datetime import date, timedelta

User = get_user_model()
user, _ = User.objects.get_or_create(username='ci_test_user', defaults={'email':'ci@example.com'})
app = Application.objects.create(user=user, applied_on=date.today(), employer_name='ACME', job_title='Tester')
client = Client()
client.force_login(user)
# test updating result
url = f'/jobs/nachweis/application/{app.pk}/inline-update/'
resp = client.post(url, {'result': app.result}, SERVER_NAME='localhost', HTTP_HOST='localhost', secure=True)
print('POST_STATUS:'+str(resp.status_code))
print('POST_CONTENT:'+resp.content.decode('utf-8'))
# test updating applied_on (change by +1 day)
new_date = (date.today() - timedelta(days=1)).isoformat()
resp2 = client.post(url, {'applied_on': new_date}, SERVER_NAME='localhost', HTTP_HOST='localhost', secure=True)
print('POST2_STATUS:'+str(resp2.status_code))
print('POST2_CONTENT:'+resp2.content.decode('utf-8'))
