from random import randrange
import time #is ka use hota hai to create randrange ko use karne ke liye 
from typing import Optional #pyandantic me optional ka use karne ke liye 
from fastapi import FastAPI, HTTPException,Response,status
from fastapi.params import Body
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
app = FastAPI()

load_dotenv()


class Post(BaseModel):
    title:str
    content:str
    published:bool=True
#jab bhi test karna ho to try and except use karna 
while True:
    try:
        conn=psycopg2.connect(host='localhost',database='fastapi' ,user='postgres',password= os.getenv("PASSWORD"),cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("successfully connected to database")
        break
    except Exception as error: 
        print("failed to connect with database") 
        print("Error:",error) 
        time.sleep(2)    
    
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
async def posts():
    cursor.execute("""SELECT id AS post , title FROM post""")
    posts=cursor.fetchall()

    return {"data":posts}
@app.post("/posts")
async def create(post:Post):
    cursor.execute("""
        INSERT INTO post (title, content, published)
        VALUES (%s, %s, %s)
        RETURNING *;
    """, (post.title, post.content, post.published))

    new_post = cursor.fetchone()

    # Commit the changes to the database
    conn.commit()

    return {"data" : new_post} 
@app.get("/posts/{id}")
async def get_post(id:str,response:Response):
    print(type(id))#here we will print  the i
    cursor.execute("""
                   SELECT * from post WHERE id=%s

                   """,(str(id)))
    post=cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"the id {id} does not exist")
        #note aha pe deatil hoga detais nahi 
    return {"post_detail":post}#yaha pe vho post ko call karega post ko jho find_data ka use karega 
   # return{"post details":posts}
@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)#note posts hai waha pe post nahi wording pe dhiyan rakhna 
async def delete_post(id:int):
    cursor.execute("""
                    DELETE FROM post WHERE id=%s  returning*
                   """,(str(id)),)
    delete_post_Id=cursor.fetchone()
    conn.commit()
    if delete_post_Id is None:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail=f"post with id :{id} does not exist ")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)#note reponse type bhejna hai to {} nahi karna hai 

@app.put("/posts/{id}")
async def update_post_id(id: int, post: Post):
    cursor.execute("""
                    UPDATE post SET title=%s,content=%s,published=%s WHERE id=%s RETURNING *""",
                    (post.title,post.content,post.published,str(id)))
    update_post_Id=cursor.fetchone()
    conn.commit()
   
    
    if update_post_Id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")

    
    
    return {"data": update_post_Id}







