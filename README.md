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

# Code Obfuscating with Pyarmor
pyarmor obfuscate --platform windows.x86_64 --src="."  -r --output=./dist main.py

# Obfuscete celery entry
pyarmor obfuscate --platform windows.x86_64 --no-runtime -O dist/tasks --exact tasks/__init__.py

# Remeber to replace [from .pytransform import pyarmor_runtime] to [from pytransform import pyarmor_runtime] in __init__.py
```