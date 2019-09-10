## Start

```bash
# Start flask app
flask run

# Create periodic tasks sender
celery -A core beat --loglevel=info

# Create periodic tasks consumer(worker)
celery -A core worker --loglevel=info -P eventlet
 
# Run celery Monitoring (Optional)
celery flower
```