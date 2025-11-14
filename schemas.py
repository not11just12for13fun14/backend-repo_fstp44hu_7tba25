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

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
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

# Real Estate Property schema (used by the app)
class Property(BaseModel):
    """
    Real estate properties
    Collection name: "property"
    """
    title: str = Field(..., description="Listing title")
    type: str = Field(..., description="Type of property: house | shophouse | kavling")
    location: str = Field(..., description="City/Area name")
    price: float = Field(..., ge=0, description="Price in local currency")
    bedrooms: Optional[int] = Field(None, ge=0, description="Number of bedrooms (if applicable)")
    bathrooms: Optional[int] = Field(None, ge=0, description="Number of bathrooms (if applicable)")
    building_area_sqm: Optional[float] = Field(None, ge=0, description="Building area in sqm")
    land_area_sqm: Optional[float] = Field(None, ge=0, description="Land area in sqm")
    images: Optional[List[str]] = Field(default_factory=list, description="Image URLs")
    description: Optional[str] = Field(None, description="Short description")
    featured: bool = Field(False, description="Show in featured section")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
