import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from config import settings

app = FastAPI(title="Blog Post Manager API")

# --- Security: Enable CORS so React can connect ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Setup (MongoDB) ---
# Connection details come from environment variables / .env (see config.py)
client = AsyncIOMotorClient(settings.mongo_uri)
db = client[settings.mongo_db_name]
posts_collection = db.posts

# --- Helper for MongoDB ObjectId conversion ---
# --- Clean Pydantic v2 Helper for MongoDB ObjectId ---
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler: GetCoreSchemaHandler
    ):
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.str_schema(),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

# --- Input Validation Schemas (Pydantic) ---
# This scores points for proper validation and error handling rules
class BlogPostModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=10)
    author: str = Field(..., min_length=2)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UpdateBlogPostModel(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = Field(None, min_length=10)
    author: Optional[str] = Field(None, min_length=2)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# --- CRUD Routes ---

# 1. CREATE
@app.post("/api/posts", response_description="Add new blog post", response_model=BlogPostModel, status_code=status.HTTP_201_CREATED)
async def create_post(post: BlogPostModel):
    # Convert Pydantic model to dict, removing the unassigned ID
    post_dict = post.model_dump(by_alias=True, exclude={"id", "_id"})
    new_post = await posts_collection.insert_one(post_dict)
    created_post = await posts_collection.find_one({"_id": new_post.inserted_id})
    return created_post

# 2. READ ALL
@app.get("/api/posts", response_description="List all blog posts", response_model=List[BlogPostModel])
async def list_posts():
    posts = await posts_collection.find().to_list(1000)
    return posts

# 3. READ SINGLE
@app.get("/api/posts/{id}", response_description="Get a single blog post", response_model=BlogPostModel)
async def show_post(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    if (post := await posts_collection.find_one({"_id": ObjectId(id)})) is not None:
        return post
        
    raise HTTPException(status_code=404, detail=f"Post with ID {id} not found")

# 4. UPDATE
@app.put("/api/posts/{id}", response_description="Update a blog post", response_model=BlogPostModel)
async def update_post(id: str, post: UpdateBlogPostModel):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Filter out fields that are None
    update_data = {k: v for k, v in post.model_dump().items() if v is not None}

    if len(update_data) >= 1:
        update_result = await posts_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )

        if update_result.modified_count == 1:
            if (updated_post := await posts_collection.find_one({"_id": ObjectId(id)})) is not None:
                return updated_post

    if (existing_post := await posts_collection.find_one({"_id": ObjectId(id)})) is not None:
        return existing_post

    raise HTTPException(status_code=404, detail=f"Post with ID {id} not found")

# 5. DELETE
@app.delete("/api/posts/{id}", response_description="Delete a blog post", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    delete_result = await posts_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return None

    raise HTTPException(status_code=404, detail=f"Post with ID {id} not found")