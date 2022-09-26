try:
    from flask import Flask
    from celery import Celery
    from datetime import timedelta
    from celery.schedules import crontab
except Exception as e:
    print("Error : {} ".format(e))

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


app = Flask(__name__)
app.config['CELERY_BACKEND'] = "redis://redis:6379/0"
app.config['CELERY_BROKER_URL'] = "redis://redis:6379/0"
app.config['CELERY_TIMEZONE'] = 'UTC'
celery_app = make_celery(app)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5.0, test.s('five'), name='add every 5')

    sender.add_periodic_task(10.0, test.s('ten'), name='add every 10')

    sender.add_periodic_task(
        crontab(hour=14, minute=0),
        test.s('Happy Monday!'),
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=0),
        test.s('Happy Monday!'),
    )

    sender.add_periodic_task(
        crontab(hour=0, minute=30, day_of_week=7),
        test.s('Happy Monday!'),
    )

@celery_app.task
def test(arg):
    print(arg)

@app.task
def add(x, y):
    z = x + y
    print(z)