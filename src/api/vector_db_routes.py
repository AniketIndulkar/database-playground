from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vector_db.vector_client import VectorDBClient

router = APIRouter(prefix="/vector-db", tags=["Vector Database"])
vector_db = VectorDBClient()

class DocumentInput(BaseModel):
    doc_id: str
    text: str
    metadata: dict = {}

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

@router.post("/add-document")
def add_document(doc: DocumentInput):
    """Add a document to vector database"""
    try:
        vector_db.add_document(doc.doc_id, doc.text, doc.metadata)
        return {"success": True, "doc_id": doc.doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
def search_similar(query: SearchQuery):
    """Search for similar documents"""
    try:
        results = vector_db.search_similar(query.query, query.top_k)
        return {
            "documents": results['documents'][0],
            "distances": results['distances'][0],
            "metadatas": results['metadatas'][0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_stats():
    """Get collection statistics"""
    return vector_db.get_collection_stats()

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    metadata_filter: dict = None

@router.post("/search")
def search_similar(query: SearchQuery):
    """Search for similar documents with optional metadata filtering"""
    try:
        results = vector_db.search_similar(query.query, query.top_k, query.metadata_filter)
        return {
            "documents": results['documents'][0],
            "distances": results['distances'][0],
            "metadatas": results['metadatas'][0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))