import boto3
import json
import os
from datetime import datetime
from typing import Dict, Any

class CloudStorage:
    def __init__(self, bucket_name: str = "lplteam25"):
        self.bucket_name = bucket_name
        # Assumes AWS_ACCESS_KEY_ID etc are in env or ~/.aws/credentials
        self.s3_client = boto3.client('s3')
        print(f"CloudStorage initialized for bucket: {self.bucket_name}")

    def upload_json(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Uploads a JSON dictionary to S3.
        """
        try:
            json_str = json.dumps(data, indent=2, default=str)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_str,
                ContentType='application/json'
            )
            print(f"  [S3] Uploaded: s3://{self.bucket_name}/{key}")
            return True
        except Exception as e:
            print(f"  [S3 Error] Failed to upload {key}: {e}")
            return False

    def upload_raw_serp(self, ticker: str, raw_data: list) -> str:
        """
        Helper for raw data lake structure.
        Key: raw_scans/YYYY-MM-DD/{ticker}_{timestamp}.json
        """
        now_str = datetime.now().strftime("%Y-%m-%d")
        ts_str = datetime.now().strftime("%H%M%S")
        key = f"raw_scans/{now_str}/{ticker}_{ts_str}.json"
        
    def upload_folder_as_zip(self, folder_path: str, s3_key_prefix: str) -> bool:
        """
        Zips a folder and uploads it to S3.
        Useful for backing up ChromaDB.
        """
        import shutil
        import os
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = os.path.basename(folder_path) or "data"
            zip_filename = f"{folder_name}_{timestamp}"
            zip_path = shutil.make_archive(zip_filename, 'zip', folder_path)
            
            s3_key = f"{s3_key_prefix}/{folder_name}_{timestamp}.zip"
            
            self.s3_client.upload_file(zip_path, self.bucket_name, s3_key)
            print(f"  [S3] Uploaded Vector Backup: s3://{self.bucket_name}/{s3_key}")
            
            # Clean up local zip
            os.remove(zip_path)
            return True
        except Exception as e:
            print(f"  [S3 Backup Error] {e}")
            return False

