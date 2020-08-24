#! /usr/bin/env bash

celery -A tasks beat --loglevel=info --pidfile=

# Create periodic tasks consumer(worker)
celery -A tasks worker --loglevel=info