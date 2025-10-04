from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from object_storage.storage_client import ObjectStorageClient
from api.models import UploadResponse, ListFilesResponse, FileInfo
from utils.benchmarking import benchmark

from pydantic import BaseModel

class VersionedUploadRequest(BaseModel):
    filename: str


router = APIRouter(prefix="/object-storage", tags=["Object Storage"])
storage = ObjectStorageClient()

@benchmark("object_storage", "upload")
@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to object storage"""
    try:
        temp_path = f"data/uploads/{file.filename}"
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        object_name = storage.upload_file(temp_path, file.filename)
        
        if object_name:
            return UploadResponse(
                success=True,
                object_name=object_name,
                message="File uploaded successfully",
                size=len(content)
            )
        else:
            raise HTTPException(status_code=500, detail="Upload failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@benchmark("object_storage", "list")
@router.get("/files", response_model=ListFilesResponse)
def list_files():
    """List all files in storage"""
    files = storage.list_files()
    file_infos = [FileInfo(**f) for f in files]
    return ListFilesResponse(files=file_infos, count=len(file_infos))

@benchmark("object_storage", "download")
@router.get("/download/{filename}")
def download_file(filename: str):
    """Download a file from storage"""
    try:
        download_path = f"data/processed/{filename}"
        result = storage.download_file(filename, download_path)
        
        if result:
            return FileResponse(
                download_path,
                filename=filename,
                media_type="application/octet-stream"
            )
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-versioned", response_model=UploadResponse)
async def upload_file_versioned(file: UploadFile = File(...)):
    """Upload a file with timestamp versioning"""
    try:
        temp_path = f"data/uploads/{file.filename}"
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        versioned_name = storage.upload_file_versioned(temp_path, file.filename)
        
        if versioned_name:
            return UploadResponse(
                success=True,
                object_name=versioned_name,
                message="File uploaded with versioning",
                size=len(content)
            )
        else:
            raise HTTPException(status_code=500, detail="Upload failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/versions/{filename}")
def list_file_versions(filename: str):
    """List all versions of a file"""
    try:
        versions = storage.list_versions(filename)
        return {"filename": filename, "versions": versions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))