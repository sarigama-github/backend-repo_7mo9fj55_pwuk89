import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from database import create_document, get_documents
from schemas import User, Blogpost, Contactmessage

app = FastAPI(title="SaaS Landing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SaaS Landing Backend is running"}

# Auth endpoints (simple demo: signup + login)
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/api/auth/signup")
def signup(payload: SignupRequest):
    # Very basic hashing for demo only; in production use bcrypt/argon2
    import hashlib
    password_hash = hashlib.sha256(payload.password.encode()).hexdigest()
    user = User(name=payload.name, email=payload.email, password_hash=password_hash)
    try:
        inserted_id = create_document("user", user)
        return {"ok": True, "user_id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
def login(payload: LoginRequest):
    # Simple lookup; in real app you would index by email and verify hash
    try:
        users = get_documents("user", {"email": payload.email}, limit=1)
        if not users:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        import hashlib
        input_hash = hashlib.sha256(payload.password.encode()).hexdigest()
        if users[0].get("password_hash") != input_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"ok": True, "user": {"name": users[0].get("name"), "email": users[0].get("email")}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Blog endpoints
@app.get("/api/blogs", response_model=List[Blogpost])
def list_blogs():
    try:
        docs = get_documents("blogpost", {"published": True}, limit=20)
        # Convert Mongo docs to Pydantic-compatible dicts (remove _id)
        items = []
        for d in docs:
            d.pop("_id", None)
            items.append(Blogpost(**d))
        return items
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Contact endpoint
class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

@app.post("/api/contact")
def contact(payload: ContactRequest):
    try:
        doc = Contactmessage(name=payload.name, email=payload.email, message=payload.message)
        inserted_id = create_document("contactmessage", doc)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
