from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    hashed_password = pwd_context.hash(password)
    return hashed_password

hashed = hash_password("r")
print(hashed)

gener_uuid = uuid.uuid4()
print(gener_uuid)