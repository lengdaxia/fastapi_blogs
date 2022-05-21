from fastapi import APIRouter, Depends, status, HTTPException
from app import database, schemas, oauth2, models
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/vote',
    tags=['Vote'] 
)

@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {vote.post_id} does not exist")
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'user already voted on Post with id: {vote.post_id}')
        
        new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message":"successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Vote with post_id : {vote.post_id} not Found')
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message":"successfully deleted vote"}