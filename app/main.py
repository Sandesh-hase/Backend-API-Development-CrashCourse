from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
from pymongo import MongoClient
import time
from datetime import datetime
from fastapi.logger import logger
from .database import collection

app = FastAPI()

retry_count = 0
max_retries = 5

while retry_count < max_retries:
    try:
        print("database connection successful")
        break
    except Exception as e:
        print("Connecting to database failed", e)
        retry_count += 1
        if retry_count < max_retries:
            time.sleep(2)
        else:
            print("Max retries reached. Exiting.")

class Post(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_post = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1},
    {"title": "title of post 2", "content": "content of post 2", "id": 2},
    {"title": "title of post 3", "content": "content of post 3", "id": 3},
    {"title": "title of post 4", "content": "content of post 4", "id": 4},
    {"title": "title of post 5", "content": "content of post 5", "id": 5}
]


def find_post(id):
    for p in my_post:
        if p['id'] == id:
            return p


def find_post_index(id):
    for i, p in enumerate(my_post):
        if p['id'] == id:
            return i

@app.get("/")
def root():
    return {"message": "Welcome to my api"}

@app.get("/posts")
def get_post():
    posts = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's internal _id
    return {"data": posts}

# create post and setting the status code
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(posts: Post):
    try:
        data = posts.dict()
        data['created_at'] = datetime.utcnow()
        result = collection.insert_one(data)
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/posts/latest")
def get_latest_post():
    post = collection.find_one(sort=[("id", -1)], projection={"_id": 0})  # Exclude MongoDB's internal _id
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")

    return {"data": post}

# get post by id
# Handling the ids that are not found
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = collection.find_one({"id": id}, {"_id": 0})  # Exclude MongoDB's internal _id
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    return {"post_detail": post}


# delete post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    result = collection.delete_one({"id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update request
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    post_dict = post.dict()
    result = collection.update_one({"id": id}, {"$set": post_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    return {"data": post_dict}


@app.post("/posts/insert_many")
def insert_many_posts(posts: List[Post]):
    try:
        data = [post.dict() for post in posts]
        for post in data:
            post['created_at'] = datetime.utcnow()
        result = collection.insert_many(data)
        return {"inserted_ids": [str(id) for id in result.inserted_ids]}
    except Exception as e:
        logger.error(f"Error inserting multiple posts: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")