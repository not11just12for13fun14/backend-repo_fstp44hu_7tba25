import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Property

from bson import ObjectId

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db as _db
        
        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            try:
                collections = _db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# -------------------- Properties API --------------------

class PropertyCreate(BaseModel):
    title: str
    type: str
    location: str
    price: float
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    building_area_sqm: Optional[float] = None
    land_area_sqm: Optional[float] = None
    images: Optional[List[str]] = []
    description: Optional[str] = None
    featured: bool = False

@app.post("/api/properties")
def add_property(payload: PropertyCreate):
    """Create a property document"""
    from schemas import Property as PropertySchema
    prop = PropertySchema(**payload.model_dump())
    inserted_id = create_document("property", prop)
    return {"id": inserted_id, "status": "created"}

@app.get("/api/properties")
def list_properties(
    q: Optional[str] = Query(None, description="Search keyword for title/location"),
    type: Optional[str] = Query(None, description="house | shophouse | kavling"),
    location: Optional[str] = Query(None, description="Filter by location"),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    bedrooms: Optional[int] = Query(None),
    featured: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """List properties with filters"""
    filter_dict = {}
    if type:
        filter_dict["type"] = type
    if location:
        filter_dict["location"] = {"$regex": location, "$options": "i"}
    if bedrooms is not None:
        filter_dict["bedrooms"] = bedrooms
    if featured is not None:
        filter_dict["featured"] = featured
    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        filter_dict["price"] = price_filter
    if q:
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"location": {"$regex": q, "$options": "i"}},
            {"type": {"$regex": q, "$options": "i"}},
        ]

    docs = get_documents("property", filter_dict, limit)
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
        if "created_at" in d:
            try:
                d["created_at"] = d["created_at"].isoformat()
            except Exception:
                pass
        if "updated_at" in d:
            try:
                d["updated_at"] = d["updated_at"].isoformat()
            except Exception:
                pass
    return {"items": docs}

@app.get("/api/properties/{property_id}")
def get_property(property_id: str):
    """Get single property by id"""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        oid = ObjectId(property_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid property id")
    doc = db["property"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Property not found")
    doc["id"] = str(doc.pop("_id"))
    if "created_at" in doc:
        try:
            doc["created_at"] = doc["created_at"].isoformat()
        except Exception:
            pass
    if "updated_at" in doc:
        try:
            doc["updated_at"] = doc["updated_at"].isoformat()
        except Exception:
            pass
    return doc

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
