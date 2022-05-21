from jose import JWSError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from app import database, models, schemas
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import setting
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# scret key
# algorithm
# exporiation time

SECRET_KEY = setting.secret_key
ALGORITHM = setting.algorithm
ACCESS_TOKEN_EXPIRE_MINUTE = setting.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expired = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)
    to_encode.update({'exp': expired})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credential_exception):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get('user_id')
        if id is None:
            raise credential_exception

        token_data = schemas.TokenData(id=id)
    except JWSError:

        raise credential_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    if user == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"User {token.id} not login")

    return user
