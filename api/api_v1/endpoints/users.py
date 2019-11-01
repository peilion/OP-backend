from fastapi import APIRouter

from model.others import TokenSchema, MsgSchema

router = APIRouter()

userMap = {
    "admin": {
        "roles": ["admin"],
        "token": "admin",
        "introduction": "This is superuser",
        "avatar": "https://ss0.bdstatic.com/70cFvHSh_Q1YnxGkpoWK1HF6hhy/it/u=2720094078,3198972262&fm=26&gp=0.jpg",
        "name": "Super admin",
    }
}


@router.post("/login/", response_model=TokenSchema)
def login():
    return userMap["admin"]


@router.get("/login/", response_model=TokenSchema)
def get_login():
    return userMap["admin"]


@router.get("/info/", response_model=TokenSchema)
def read_user_info():
    return userMap["admin"]


@router.post("/logout/", response_model=MsgSchema)
def logout():
    return {"msg": "Logout Success"}
