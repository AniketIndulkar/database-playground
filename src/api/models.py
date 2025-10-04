from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UploadResponse(BaseModel):
    """Response after uploading a file"""
    success: bool
    object_name: str
    message: str
    size: Optional[int] = None

class FileInfo(BaseModel):
    """Information about a stored file"""
    name: str
    size: int
    last_modified: datetime

class ListFilesResponse(BaseModel):
    """Response with list of files"""
    files: list[FileInfo]
    count: int