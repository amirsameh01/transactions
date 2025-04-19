from celery import Celery

app = Celery('transactions')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

#TODO: delete this one
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')