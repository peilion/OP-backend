from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from tasks.diagnosis_task import expert_system_diagnosis
from tasks.elec_feature_task import cal_elec_feature
from tasks.mset_task import mset_evaluate
from tasks.feature_task import cal_vib_feature

app = Celery(
    "tasks",
    broker=os.getenv("RABBITMQ_URL"),
    # broker='pyamqp://guest:8315814@localhost//',
    # backend='redis://@localhost'
)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=10, timezone="Asia/Shanghai", worker_max_tasks_per_child=100
)

app.conf.beat_schedule = {
    "make_feature_calculation-in-60-seconds": {
        "task": "tasks.celery.make_feature_calculation",
        "schedule": 60.0,
    },
    "make_elec_feature_calculation-in-60-seconds": {
        "task": "tasks.celery.make_elec_feature_calculation",
        "schedule": 60.0,
    },
    "make_mset_estimate-in-60-seconds": {
        "task": "tasks.celery.make_mset_estimate",
        "schedule": 60.0,
    },
    "make_diagnosis-in-60-seconds": {
        "task": "tasks.celery.make_diagnosis",
        "schedule": 60.0,
    },
}


@app.task(ignore_result=True, expires=10)
def make_feature_calculation():
    res = cal_vib_feature()
    print("{0} feature extraction finished.".format(res))


@app.task(ignore_result=True, expires=10)
def make_elec_feature_calculation():
    res = cal_elec_feature()
    print("{0} feature extraction finished.".format(res))


@app.task(ignore_result=True, expires=10)
def make_mset_estimate():
    res = mset_evaluate(3)
    print("{0} estimate finished.".format(res))


@app.task(ignore_result=True, expires=10)
def make_diagnosis():
    res = expert_system_diagnosis()
    print("{0} diagnosis finished.".format(res))
