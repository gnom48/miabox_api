from fastapi import HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from minio import Minio
from datetime import timedelta
from minio.error import S3Error
from app.toml_helper import load_data_from_toml
from io import BytesIO


class MinioClient:
    def __init__(self, endpoint, access_key, secret_key, secure=False):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def upload_file(self, bucket_name: str, file: UploadFile):
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)

            file_data = file.file.read()
            self.client.put_object(
                bucket_name, file.filename, BytesIO(file_data), len(file_data))

            return {"message": f"File {file.filename} uploaded successfully to {bucket_name} bucket."}
        except S3Error as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    def download_file(self, bucket_name: str, file_name: str):
        try:
            data = self.client.get_object(bucket_name, file_name)
            return StreamingResponse(data.stream(), media_type="application/octet-stream")
        except S3Error as err:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(err))

    def get_presigned_url(self, bucket_name: str, file_name: str, expires: timedelta = timedelta(days=7)):
        try:
            url = self.client.presigned_get_object(
                bucket_name, file_name, expires=expires)
            return {"url": url}
        except S3Error as err:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(err))

    def delete_file(self, bucket_name: str, file_name: str):
        try:
            self.client.remove_object(bucket_name, file_name)
            return "Ok"
        except S3Error as err:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(err))

    @staticmethod
    def minio_client_factory():
        config = load_data_from_toml()["services"]
        return MinioClient(
            endpoint=f"minio:{config["minio_api_port"]}",
            access_key=config["minio_access_key"],
            secret_key=config["minio_secret_key"]
        )
