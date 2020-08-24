@echo off
C:
cd C:\Users\fpl11\Desktop\OP-Backend-prod-merge-database\dist
celery -A tasks worker --loglevel=info -P eventlet
pause