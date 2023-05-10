from typing import Callable

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .. import secret

engine=create_async_engine(secret.ASYNC_DB_CONNECTOR, echo=False, future=True)
async_session_maker: Callable[[], AsyncSession] = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
