from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from typing import Optional
from random import randrange
from pymongo import MongoClient
import time

app = FastAPI()

retry_count = 0
max_retries = 5

while retry_count < max_retries:
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client["socialmedia"]
        collection = db["posts"]
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
    post_dict = posts.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_post.append(post_dict)
    return {
            "data": post_dict
    }

@app.get("/posts/latest")
def get_latest_post():
    post = my_post[-1]
    return {"data": post}

# get post by id
# Handling the ids that are not found
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    return {"post_detail": post}


# delete post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # deleting the post
    # find the index of the post
    index = find_post_index(id)
    if not index:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    my_post.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update request
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_post_index(id)
    if not index:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    post_dict = post.dict()
    post_dict['id'] = id
    my_post[index] = post_dict
    return {"data": post_dict}


