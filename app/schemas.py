from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


class PostCreate(PostBase):
    pass


# Handling the data staructure getting from response
class Post(PostBase):
    id: Optional[int] = None
    created_at: datetime


    # class Config:
    #     from_attributes = True