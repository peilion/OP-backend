#! /usr/bin/env bash

celery -A core beat --loglevel=info &

# Create periodic tasks consumer(worker)
celery -A core worker --loglevel=info