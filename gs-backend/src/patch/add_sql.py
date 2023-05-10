from pitricks import make_parent_top
make_parent_top(2)

import time
import string
import hashlib
import random as rd
import asyncio as ai
from objprint import op

from sqlalchemy import select

from ..store import UserPasswordStore, async_session_maker, MailVerifyCodeStore

async def qwq():
  async with async_session_maker() as sess:
    users = await sess.scalars(select(UserPasswordStore))
    for user in users:
      salt = ''.join(rd.choices(string.ascii_letters + string.digits, k=16))
      hashed_password = hashlib.sha512((salt + user.passw).encode('utf-8')).hexdigest()
      user.salt = salt
      user.passw = hashed_password
    await sess.commit()

ai.get_event_loop().run_until_complete(qwq())
