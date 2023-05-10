from __future__ import annotations
import OpenSSL.crypto
import pathlib
from typing import TYPE_CHECKING, List

from .api_secret import *

if TYPE_CHECKING:
    from .store import UserStore
    from . import utils

##
# SECRET KEYS
##

# SIGNING KEYS

# openssl ecparam -name secp256k1 -genkey -noout -out token.priv
# openssl req -x509 -key token.priv -out token.pub -days 365
with open('/gs-backend/token/token.priv') as f:
    TOKEN_SIGNING_KEY = OpenSSL.crypto.load_privatekey(
        OpenSSL.crypto.FILETYPE_PEM, f.read())

##
# DEPLOYMENT CONFIG
##

# FS PATHS

BACKEND_PATH = pathlib.Path('/gs-backend/')
STROAGE_PATH = BACKEND_PATH/'stroage'
TEMPLATE_PATH = (STROAGE_PATH/"template").resolve()
WRITEUP_PATH = (STROAGE_PATH/"writeup").resolve()
ATTACHMENT_PATH = (STROAGE_PATH/"attachment").resolve()
MEDIA_PATH = (STROAGE_PATH/"media").resolve()
SYBIL_LOG_PATH = (STROAGE_PATH/"anticheat_log").resolve()

# INTERNAL PORTS

GLITTER_ACTION_SOCKET_ADDR = 'ipc:///var/www/action.sock'
GLITTER_EVENT_SOCKET_ADDR = 'ipc:///var/www/event.sock'

N_WORKERS = 3


def WORKER_API_SERVER_KWARGS(idx0): return {  # will be passed to `Sanic.run`
    'host': '127.0.0.1',
    'port': 8010+idx0,
    'debug': False,
    # nginx already does this. disabling sanic access log makes it faster.
    'access_log': False,
}


REDUCER_ADMIN_SERVER_ADDR = ('127.0.0.1', 5000)

# FUNCTIONS

WRITEUP_MAX_SIZE_MB = 20
WS_PUSH_ENABLED = True
POLICE_ENABLED = True
ANTICHEAT_RECEIVER_ENABLED = False

STDOUT_LOG_LEVEL: List[utils.LogLevel] = [
    'debug', 'info', 'warning', 'error', 'critical', 'success']
DB_LOG_LEVEL: List[utils.LogLevel] = [
    'info', 'warning', 'error', 'critical', 'success']
PUSH_LOG_LEVEL: List[utils.LogLevel] = ['error', 'critical']

# URLS

# redirected to this after (successful or failed) login
FRONTEND_PORTAL_URL = '/'
ADMIN_URL = '/admin'  # prefix of all admin urls
# or `None` to opt-out X-Accel-Redirect
ATTACHMENT_URL = '/_internal_attachments'

BACKEND_HOSTNAME = '127.0.0.1'  # used for oauth redirects
BACKEND_SCHEME = 'http'  # used for oauth redirects

OAUTH_HTTP_PROXIES = {  # will be passed to `httpx.AsyncClient`, see https://www.python-httpx.org/advanced/#http-proxying
    'all://*github.com': None,  # 'http://127.0.0.1:xxxx',
}


def BUILD_OAUTH_CALLBACK_URL(url: str) -> str:
    return url  # change this if you want to rewrite the oauth callback url

##
# PERMISSION
##


MANUAL_AUTH_ENABLED = False  # it should be disabled in production after setting up


def IS_ADMIN(user: UserStore) -> bool:
    # ADMIN_UIDS = [1]
    return (
        user is not None
        and user.group == 'staff'
        # and user.id in ADMIN_UIDS
    )
