# import cloudinary.uploader
# from fastapi import UploadFile
# from typing import List

# async def upload_image(file: UploadFile) -> str:
#     result = cloudinary.uploader.upload(file.file)
#     return result['secure_url']

# async def upload_multiple_images(files: List[UploadFile]) -> List[str]:
#     urls = []
#     for file in files:
#         result = cloudinary.uploader.upload(file.file)
#         urls.append(result['secure_url'])
#     return urls

# from app.core.supabase_client import supabase
# from fastapi import UploadFile
# from typing import List
# import uuid

# async def upload_image(file: UploadFile) -> str:
#     file_extension = file.filename.split(".")[-1]
#     file_name = f"{uuid.uuid4()}.{file_extension}"
#     file_path = f"product_images/{file_name}"
    
#     await supabase.storage.from_("product_images").upload(file_path, file.file.read())
    
#     return supabase.storage.from_("product_images").get_public_url(file_path)

# async def upload_multiple_images(files: List[UploadFile]) -> List[str]:
#     urls = []
#     for file in files:
#         url = await upload_image(file)
#         urls.append(url)
#     return urls


from fastapi import UploadFile
from typing import List
import os
import uuid
import shutil

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def upload_image(file: UploadFile) -> str:
    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # Save file to local directory
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return relative path that will be stored in database
    return f"/products/{file_name}"


async def upload_multiple_images(files: List[UploadFile]) -> List[str]:
    urls = []
    for file in files:
        url = await upload_image(file)
        urls.append(url)

    # Return list relative paths that will be stored in database
    return urls