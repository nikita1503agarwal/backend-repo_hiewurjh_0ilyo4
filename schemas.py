"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, List

# Portfolio-specific schemas

class ContactMessage(BaseModel):
    name: str = Field(..., description="Sender name", min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Sender email")
    subject: str = Field(..., description="Message subject", min_length=1, max_length=150)
    message: str = Field(..., description="Message body", min_length=1, max_length=2000)

class Project(BaseModel):
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Short description")
    tags: List[str] = Field(default_factory=list, description="Tech tags")
    repo_url: Optional[HttpUrl] = Field(None, description="GitHub/Repo URL")
    live_url: Optional[HttpUrl] = Field(None, description="Live demo URL")
    image: Optional[HttpUrl] = Field(None, description="Screenshot or cover image")

class Profile(BaseModel):
    name: str
    title: str
    location: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[HttpUrl] = None
    socials: Optional[dict] = None

# Example schemas kept for reference (not used by the portfolio app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
