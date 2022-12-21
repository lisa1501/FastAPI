from multiprocessing import synchronize
from pydoc import ModuleScanner
from sqlite3 import Cursor
from typing import Optional, List
from unittest.main import MODULE_EXAMPLES
from fastapi import FastAPI, Response,status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session 
from . import models, schemas
from . database import engine, get_db

models.Base.metadata.create_all(bind=engine)


app = FastAPI()




while True:
    try:
        conn = psycopg2.connect(host='localhost',database='fastapi',user='postgres',
                                password='password123',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was succesfull!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id":1}, 
            {"title": "My favorite food", "content": "Sushi", "id":2}]

def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post

def find_index_post(id):
    for i,post in enumerate(my_posts):
        if post['id'] == id:
            return i
            
@app.get("/")
def root():
    return {"message": "Hello World!"}



@app.get("/posts",response_model=List[schemas.Post]) 
def get_posts(db:Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()
    posts= db.query(models.Post).all()
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db:Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                                     (post.title, post.content, post.published ))
    # new_post = cursor.fetchone()
    # conn.commit()
    

    # print(post.dict())
    # print(**post.dict())
    # new_post=models.Post(**post.dict())
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db:Session = Depends(get_db)):
    # cursor.execute("""SELECT * from posts WHERE id = %s""",(str(id),))
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post wiht id: {id} was not found")
    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db:Session = Depends(get_db)):

    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exists")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}",response_model=schemas.Post)
def update_post(id:int, updated_post:schemas.PostCreate, db:Session = Depends(get_db)):
    
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                                     (post.title, post.content, post.published, str(id)))

    # updated_post = cursor.fetchone()
    # conn.commit()
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    print(post)
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exists")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


@app.post("/users",status_code=status.HTTP_201_CREATED)
def create_user(user:schemas.UserCreate, db:Session = Depends(get_db)):
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
    
