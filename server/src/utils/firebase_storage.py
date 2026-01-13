import firebase_admin
from firebase_admin import credentials, storage
import os
from datetime import timedelta
import logging
from typing import Optional
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "../../.")

class FirebaseStorage:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseStorage, cls).__new__(cls)
        return cls._instance

    def __init__(self, credentials_path: str = 'firebase-credentials.json', 
                 bucket_name: str = 'cvs'):
        if not FirebaseStorage._initialized:
            self.credentials_path = os.path.join(config_path, credentials_path)
            print("PATH::",self.credentials_path)
            self.bucket_name = bucket_name
            self.local_cache_dir = os.path.join(BASE_DIR, "../data")
            self.initialize_firebase()
            FirebaseStorage._initialized = True

    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Firebase credentials file not found at {self.credentials_path}")

            cred = credentials.Certificate(self.credentials_path)
            firebase_admin.initialize_app(cred, {'storageBucket': self.bucket_name})
            
            self.bucket = storage.bucket()
            logger.info("Firebase Storage initialized successfully")
            
            # Create local cache directory if it doesn't exist
            if not os.path.exists(self.local_cache_dir):
                os.makedirs(self.local_cache_dir)
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise

    def upload_file(self, file_path: str, storage_folder: str = "files") -> dict:
        """
        Upload file to Firebase Storage
        
        Args:
            file_path: Local path to the file
            storage_folder: Folder in Firebase Storage (default: "files")
            
        Returns:
            dict: Contains file_id, file_path, download_url
        """
        print("FILE:::",file_path)
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1]
            
            # Create storage path
            storage_path = f"{storage_folder}/{file_id}{file_extension}"
            
            # Create blob and upload
            blob = self.bucket.blob(storage_path)
            blob.upload_from_filename(file_path)
            
            # Generate signed URL (valid for 7 days)
            download_url = blob.generate_signed_url(
                version="v4",
                method="GET"
            )
            
            logger.info(f"File uploaded successfully: {storage_path}")
            
            return {
                "file_id": file_id,
                "file_name": file_name,
                "storage_path": storage_path,
                "download_url": download_url
            }
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")

    def download_file(self, storage_path: str, local_path: Optional[str] = None) -> str:
        """
        Download file from Firebase Storage
        If file exists locally, return local path. Otherwise download and save.
        
        Args:
            storage_path: Path in Firebase Storage (e.g., "files/abc-123.pdf")
            local_path: Optional custom local path. If None, saves to cache directory
            
        Returns:
            str: Path to the downloaded file
        """
        try:
            # Determine local file path
            if local_path is None:
                file_name = os.path.basename(storage_path)
                local_path = os.path.join(self.local_cache_dir, file_name)
            
            # Check if file already exists locally
            if os.path.exists(local_path):
                logger.info(f"File already exists locally: {local_path}")
                return local_path
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download from Firebase
            blob = self.bucket.blob(storage_path)
            
            if not blob.exists():
                raise FileNotFoundError(f"File not found in Firebase Storage: {storage_path}")
            
            blob.download_to_filename(local_path)
            logger.info(f"File downloaded successfully: {local_path}")
            
            return local_path
            
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise Exception(f"Failed to download file: {str(e)}")


# Singleton instance
firebase_storage = FirebaseStorage()