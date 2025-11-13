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

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password_hash: str = Field(..., description="Password hash (server-side only)")
    avatar: Optional[str] = Field(None, description="Avatar URL")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

class Blogpost(BaseModel):
    """Blog posts collection schema (collection name: blogpost)"""
    title: str = Field(...)
    slug: str = Field(..., description="URL-friendly identifier")
    excerpt: Optional[str] = None
    content: str = Field(...)
    author: str = Field(...)
    tags: List[str] = Field(default_factory=list)
    published: bool = Field(True)

class Contactmessage(BaseModel):
    """Contact messages collection schema (collection name: contactmessage)"""
    name: str = Field(...)
    email: EmailStr = Field(...)
    message: str = Field(..., min_length=3)

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
