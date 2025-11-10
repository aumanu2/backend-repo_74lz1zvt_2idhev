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

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal, Dict, Any

# Existing example schemas remain available for reference
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Portfolio-specific schemas
class Project(BaseModel):
    title: str
    slug: str
    summary: str
    domain: Literal["ML", "Analytics", "Visualization", "NLP", "CV", "Time Series", "MLOps", "Other"]
    stack: List[str] = []
    year: int
    problem: str
    approach: str
    dataset: str
    model: str
    results: str
    impact: str
    github_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    tags: List[str] = []
    plotly_fig: Optional[Dict[str, Any]] = Field(
        default=None,
        description="A lightweight Plotly figure specification (data/layout)",
    )

class Publication(BaseModel):
    title: str
    venue: str
    year: int
    authors: List[str]
    link: Optional[HttpUrl] = None
    slides_url: Optional[HttpUrl] = None
    kind: Literal["paper", "talk", "workshop"] = "paper"

class BlogPost(BaseModel):
    title: str
    slug: str
    excerpt: str
    body: str
    topics: List[str] = []
    published_at: str

class ContactMessage(BaseModel):
    name: str
    email: str
    message: str
    source: Optional[str] = None
