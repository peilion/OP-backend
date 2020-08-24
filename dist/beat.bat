@echo off
C:
cd C:\Users\fpl11\Desktop\OP-Backend-prod-merge-database\dist
celery -A tasks beat --loglevel=info --pidfile=
pause