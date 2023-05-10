from __future__ import annotations
from sqlalchemy import Column, String, JSON, Integer, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import relationship, validates
import time
import random
import string
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from . import UserProfileStore
from . import Table

class MailVerifyCodeStore(Table):
    __tablename__ = 'mail_verify_code'
    
    mail = Column(String(128), nullable=False)
    verify_code = Column(String(8), nullable=False)
    timestamp = Column(BigInteger, nullable=False, default=lambda: int(time.time()))
    ip = Column(String(64), nullable=False)
