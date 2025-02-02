from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile

class SearchRequest(BaseModel):
    text_query: Optional[str] = None
    # Note: image will be handled separately as UploadFile

class SearchResponse(BaseModel):
    message: str
    data: list
    
    class Config:
        from_attributes = True