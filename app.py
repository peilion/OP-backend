import os
import sys

from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

import api
import flask_monitoringdashboard as dashboard
from admin import make_admin

# Build paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'extra_apps'))

# init app object
app = Flask(__name__)

# init api dashboard, localhost:5000/dashboard u:admin p:admin.
# disable it in production enviorment.
dashboard.bind(app)

# configuring
app.config.from_pyfile('config.py')

# cross origin resource sharing. Since we use http-proxy in the frontend, this line does not work now.
# when it is necessary to configure cors in back end, add following argument to support cors.
# resources={r"/api/*": {"origins": "*"}}
CORS(app, supports_credentials=True)

# swagger api document based on flassger
swagger = Swagger(app, template_file=os.path.join(os.getcwd(), 'api', 'resources', 'template.yaml'))

# api endpoint register
app.register_blueprint(api.views.blueprint)

# cache initialization, using decorator upon resource classes to support redis cache.
# ie:
# import cache from extensions
# @cache.cached(timeout=50)
# cache.init_app(app)

# Flask admin, url: host/admin/
admin = make_admin(app)

if __name__ == '__main__':
    app.run()
