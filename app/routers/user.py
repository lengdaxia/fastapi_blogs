
from fastapi import Depends, FastAPI, Response, status, HTTPException, APIRouter
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import engine, get_db
from app import database, oauth2

router = APIRouter(
    prefix="/users",
    tags=["User"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    check_user = db.query(models.User).filter(models.User.email == user.email)
    if check_user.first() != None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User  {user.email} already exist")

    hashed_pwd = utils.hash(user.password)
    user.password = hashed_pwd

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user id: {id} not found")

    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def get_user(id: int, db: Session = Depends(get_db), current_user: Session = Depends(oauth2.get_current_user)):

    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user id: {id} not found")
    if id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="action not allowed")
    user_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
