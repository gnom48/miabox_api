import os
from minio import Minio
from minio.error import S3Error
import logging


TMP_PATH = r"./tmp"


class MinioClient:
    def __init__(self, endpoint, access_key, secret_key, secure=False):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    async def download_file_to_temp(self, bucket_name, object_name, file_path: str) -> str:
        """
        Загружает файл из Minio на диск

        Args:
            ...

        Returns: 
            str: путь к файлу
        """
        try:
            data = self.client.get_object(bucket_name, object_name)
            file_path = os.path.join(TMP_PATH, object_name)
            os.makedirs(TMP_PATH, exist_ok=True)
            with open(file_path, 'wb') as file_data:
                for d in data.stream(32*1024):
                    file_data.write(d)
                file_data.seek(0)
            return file_path
        except S3Error as e:
            logging.error(msg="Ошибка при загрузке файла", extra=e)
        except IOError:
            logging.error(msg="Ошибка при работе с файлом на диске", extra=e)
