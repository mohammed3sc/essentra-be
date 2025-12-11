from celery import Celery

app = Celery('celery_worker',
             broker='amqp://guest:guest@rabbitmq:5672/',
             backend='rpc://')

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
