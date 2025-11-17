import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import ContactMessage, Project, Profile

app = FastAPI(title="Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Portfolio API running"}

# Health and DB test
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Re-evaluate env flags at the end
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Seed default profile and projects if empty (idempotent)
@app.post("/seed")
def seed_content():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    created = {"profile": False, "projects": 0}
    # Seed profile
    if db["profile"].count_documents({}) == 0:
        profile = Profile(
            name="Alex Johnson",
            title="Software Engineer",
            location="San Francisco, CA",
            bio=(
                "I build reliable web apps with React, TypeScript, and Python. "
                "I care about performance, DX, and pixel-perfect UI."
            ),
            avatar="https://i.pravatar.cc/300?img=5",
            socials={
                "github": "https://github.com/example",
                "linkedin": "https://www.linkedin.com/in/example/",
                "twitter": "https://x.com/example"
            }
        )
        create_document("profile", profile)
        created["profile"] = True

    # Seed projects
    demo_projects = [
        Project(
            title="Realtime Chat",
            description="Socket.io chat with rooms, typing indicators, and message receipts.",
            tags=["React", "Node", "Socket.io", "Tailwind"],
            repo_url="https://github.com/example/realtime-chat",
            live_url="https://chat.example.com",
            image="https://images.unsplash.com/photo-1526358269546-0f5a3aee4c08?q=80&w=1200&auto=format&fit=crop"
        ),
        Project(
            title="AI Markdown Notes",
            description="GPT-assisted markdown editor with embeddings and semantic search.",
            tags=["Next.js", "OpenAI", "Prisma", "Postgres"],
            repo_url="https://github.com/example/ai-notes",
            live_url="https://notes.example.com",
            image="https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=1200&auto=format&fit=crop"
        ),
        Project(
            title="E-commerce Starter",
            description="Headless commerce with Stripe, webhooks, and admin dashboard.",
            tags=["Remix", "Stripe", "Planetscale", "Tailwind"],
            repo_url="https://github.com/example/commerce-starter",
            live_url="https://shop.example.com",
            image="https://images.unsplash.com/photo-1540390769620-2d09bda0e6f3?q=80&w=1200&auto=format&fit=crop"
        ),
    ]

    if db["project"].count_documents({}) == 0:
        for p in demo_projects:
            create_document("project", p)
            created["projects"] += 1

    return {"seeded": created}

# Public endpoints

@app.get("/profile")
def get_profile():
    docs = get_documents("profile", limit=1)
    if not docs:
        # Return a safe default if not seeded
        return {
            "name": "Your Name",
            "title": "Software Engineer",
            "location": "",
            "bio": "Add your bio from the backend seed endpoint.",
            "avatar": "https://i.pravatar.cc/300",
            "socials": {}
        }
    d = docs[0]
    d.pop("_id", None)
    return d

@app.get("/projects")
def list_projects():
    docs = get_documents("project")
    for d in docs:
        d.pop("_id", None)
    return docs

# Contact endpoint stores messages so you can read them later in DB viewer
@app.post("/contact")
def submit_contact(payload: ContactMessage):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    create_document("contactmessage", payload)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
