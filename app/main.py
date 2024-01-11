from fastapi import Depends, FastAPI, HTTPException,Response,status
from dotenv import load_dotenv
from pydantic import BaseModel
from .database import SessionLocal, engine
from . import models
from sqlalchemy.orm import Session
from .test import test_conn
from .connection import connect
models.Base.metadata.create_all(bind=engine)
load_dotenv()
app = FastAPI()
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class Post(BaseModel):
    title:str
    content:str
    published:bool=True
#jab bhi test karna ho to try and except use karna 
test_conn()
conn, cursor = connect()
#instead using an database i have created an my_data array which will have data stored in memory 
my_data=[{"title":"Hello world","content":"hi","published":True,"rating":4,"id":1},
         {"title":"Hello!!!","content":"what","published":True,"rating":3,"id":4},
         {"title":"Hello!!!","content":"what","published":True,"rating":3,"id":7}]    
def find_data(id): #note here we will take the data using the id as argument 
    for i,p  in  enumerate(my_data):
        if p["id"]==id:
            print(f"Debug: Found post {p} at index {i}")
            return p,i
    return None,None    


def delete_post_id(id):
    for i, p in enumerate(my_data):
        if p["id"]==id:
            return i

#jo bhi path hai vho ("/") path will check the frist one only next will be removed 
@app.get("/")
async def root():
    return {"message": "Hello World"}
@app.get("/posts")
async def posts(db: Session = Depends(get_db)):
    #cursor.execute("""SELECT id AS post , title FROM post""")
    #posts=cursor.fetchall()
    posts=db.query(models.Post).all()

    return {"data":posts}
@app.get("/sqlalchemy")
async def test_post(db: Session = Depends(get_db)):
    posts=db.query(models.Post).all()
    return{"success":posts}
@app.post("/posts",status_code=status.HTTP_201_CREATED)
async def create(post:Post,db:Session =Depends(get_db)):
    #cursor.execute("""
    #    INSERT INTO post (title, content, published)
     #   VALUES (%s, %s, %s)
      #  RETURNING *;
    #""", (post.title, post.content, post.published))


    new_post=models.Post(title=post.title,content=post.content,published=post.published)
    db.add(new_post)

    db.commit()
    db.refresh(new_post)

    return {"data" : new_post} 
@app.get("/posts/{id}")
async def get_post(id:str,response:Response,db:Session =Depends(get_db)):
    #print(type(id))#here we will print  the i
    #cursor.execute("""
     #              SELECT * from post WHERE id=%s

      #             """,(str(id)))
    #post=cursor.fetchone()
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"the id {id} does not exist")
        #note aha pe deatil hoga detais nahi 
    return {"post_detail":post}#yaha pe vho post ko call karega post ko jho find_data ka use karega 
   # return{"post details":posts}
@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)#note posts hai waha pe post nahi wording pe dhiyan rakhna 
async def delete_post(id:int,db:Session =Depends(get_db)):
    #cursor.execute("""
     #               DELETE FROM post WHERE id=%s  returning*
     #              """,(str(id)),)
    #delete_post_Id=cursor.fetchone()
    #conn.commit()
    #delete_post_Id=db.query(models.Post.id==id)
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exist")
    post.delete(synchronize_session=False) 
    db.commit()   
    return Response(status_code=status.HTTP_204_NO_CONTENT)#note reponse type bhejna hai to {} nahi karna hai 

@app.put("/posts/{id}")
async def post_query_id(id: int, updated_post: Post,db:Session =Depends(get_db)):
    #cursor.execute("""
     #               UPDATE post SET title=%s,content=%s,published=%s WHERE id=%s RETURNING *""",
      #              (post.title,post.content,post.published,str(id)))
    #post_query_Id=cursor.fetchone()
    post_query=db.query(models.Post).filter(models.Post.id == id)
    post=post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id : {id} does not exist")
    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()
    return {"data": post_query.first()} 







