#! /usr/bin/env bash

celery -A core beat --loglevel=info --pidfile=

# Create periodic tasks consumer(worker)
celery -A core worker --loglevel=info