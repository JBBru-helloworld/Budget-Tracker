from motor.motor_asyncio import AsyncIOMotorClient
from ..config.settings import settings

async def get_database():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    return client[settings.MONGODB_DB_NAME] 