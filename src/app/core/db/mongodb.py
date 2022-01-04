from motor.motor_asyncio import AsyncIOMotorClient


class DataBase:  # pylint: disable=R0903
    client: AsyncIOMotorClient = None


db = DataBase()
