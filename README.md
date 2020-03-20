## Start

```shell script
# Start app
python main.py

# Create periodic tasks sender
celery -A tasks beat --loglevel=info

# Create periodic tasks consumer(worker)
celery -A tasks worker --loglevel=info -P eventlet
 
# Run celery Monitoring (Optional)
celery flower
```