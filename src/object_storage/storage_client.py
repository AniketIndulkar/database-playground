from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ObjectStorageClient:
    """Client for interacting with MinIO object storage"""
    
    def __init__(self):
        self.client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=os.getenv("MINIO_SECURE", "False") == "True"
        )
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME")
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"✅ Bucket '{self.bucket_name}' created")
            else:
                print(f"✅ Bucket '{self.bucket_name}' already exists")
        except S3Error as e:
            print(f"❌ Error creating bucket: {e}")
    
    def upload_file(self, file_path: str, object_name: str = None):
        """Upload a file to object storage"""
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        try:
            self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=file_path
            )
            print(f"✅ Uploaded '{file_path}' as '{object_name}'")
            return object_name
        except S3Error as e:
            print(f"❌ Error uploading file: {e}")
            return None
        
    def download_file(self, object_name: str, download_path: str):
        """Download a file from object storage"""
        try:
            self.client.fget_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=download_path
            )
            print(f"✅ Downloaded '{object_name}' to '{download_path}'")
            return download_path
        except S3Error as e:
            print(f"❌ Error downloading file: {e}")
            return None

    def list_files(self):
        """List all files in the bucket"""
        try:
            objects = self.client.list_objects(self.bucket_name)
            files = []
            for obj in objects:
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified
                })
                print(f"📄 {obj.object_name} ({obj.size} bytes)")
            return files
        except S3Error as e:
            print(f"❌ Error listing files: {e}")
            return []

if __name__ == "__main__":
    storage = ObjectStorageClient()
    
    # Upload
    storage.upload_file("data/uploads/test.txt", "my-first-upload.txt")
    
    # List all files
    print("\n📋 Files in storage:")
    storage.list_files()
    
    # Download
    storage.download_file("my-first-upload.txt", "data/processed/downloaded.txt")
    
    print("\n🎉 Object storage operations completed!")