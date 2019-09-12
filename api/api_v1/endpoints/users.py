from fastapi import APIRouter

from model.msg import Msg
from model.token import Token

router = APIRouter()

userMap = {
    'admin': {
        'roles': ['admin'],
        'token': 'admin',
        'introduction': 'This is superuser',
        'avatar': 'https://ss0.bdstatic.com/70cFvHSh_Q1YnxGkpoWK1HF6hhy/it/u=2720094078,3198972262&fm=26&gp=0.jpg',
        'name': 'Super admin'
    }
}


@router.post('/login/', tags=["login"], response_model=Token)
def login():
    return userMap['admin']


@router.get('/login/', tags=["login"], response_model=Token)
def login():
    return userMap['admin']

@router.get('/info/', tags=["login"], response_model=Token)
def login():
    return userMap['admin']


@router.post('/logout/', tags=["login"], response_model=Msg)
def login():
    return {"msg": "Logout Success"}
