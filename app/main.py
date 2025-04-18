from fastapi import FastAPI, HTTPException, Response, status
from typing import List
import time
from datetime import datetime
from fastapi.logger import logger
from .database import collection
from . import schemas

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

@app.get("/posts", response_model=List[schemas.Post])
def get_all_posts():
    posts = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's internal _id
    return posts

# Create post and set the status code
@app.post(
    "/posts",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post
)
def create_post(posts: schemas.PostBase):
    try:
        data = posts.dict()
        data['created_at'] = datetime.utcnow()
        result = collection.insert_one(data)
        # Retrieve the inserted document
        inserted_post = collection.find_one(
            {"_id": result.inserted_id},
            {"_id": 0}
        )
        return inserted_post
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/posts/latest")
def get_latest_post():
    post = collection.find_one(sort=[("id", -1)], projection={"_id": 0})  # Exclude MongoDB's internal _id
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")

    return post

# get post by id
# Handling the ids that are not found
@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, response: Response):
    post = collection.find_one({"id": id}, {"_id": 0})  # Exclude MongoDB's internal _id
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )

    return post

@app.delete("/posts/delete_null_id", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts_with_null_id():
    result = collection.delete_many({"id": None})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts with null id found"
        )
    return {"deleted_count": result.deleted_count}
    

# delete post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    result = collection.delete_one({"id": id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update request
@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostBase):
    post_dict = post.dict()
    result = collection.update_one({"id": id}, {"$set": post_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    return post_dict


@app.post("/posts/insert_many")
def insert_many_posts(posts: List[schemas.PostBase]):
    try:
        data = [post.dict() for post in posts]
        for post in data:
            post['created_at'] = datetime.utcnow()
        result = collection.insert_many(data)
        return {"inserted_ids": [str(id) for id in result.inserted_ids]}
    except Exception as e:
        logger.error(f"Error inserting multiple posts: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

