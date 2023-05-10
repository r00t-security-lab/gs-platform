from dataclasses import dataclass

import httpx
from sanic import Blueprint, Request, HTTPResponse, response
from sanic_ext import validate
from typing import Optional
from sqlalchemy import select
import re
import string
from flask import jsonify, make_response
import random as rd
import time
import hashlib

from ...store import UserPasswordStore, async_session_maker, MailVerifyCodeStore
from ..auth import auth_response, AuthResponse, AuthError, oauth2_redirect, oauth2_check_state, json_response
from ...state import User
from ...logic import Worker
from ... import secret
from ...mail import send_verify_code
from ..auth import _register_or_login

try:
    from .auth_pku import iaaa_login, iaaa_check
except ImportError:
    print('WARNING: pku auth not implemented')
    async def iaaa_login() -> HTTPResponse:
        return response.text('not implemented')
    async def iaaa_check(req: Request, http_client: httpx.AsyncClient, worker: Worker) -> AuthResponse:
        raise AuthError('not implemented')

bp = Blueprint('auth', url_prefix='/auth')

@bp.route('/logout')
async def auth_logout(_req: Request) -> HTTPResponse:
    res = response.redirect(secret.FRONTEND_PORTAL_URL)
    del res.cookies['auth_token'] # type: ignore
    del res.cookies['admin_2fa'] # type: ignore
    return res

@dataclass
class AuthManualParam:
    identity: str

@bp.route('/manual')
@validate(query=AuthManualParam)
@auth_response
async def auth_manual(_req: Request, query: AuthManualParam, _worker: Worker) -> AuthResponse:
    if not secret.MANUAL_AUTH_ENABLED:
        raise AuthError('手动登录已禁用')

    return f'manual:{query.identity}', {'type': 'manual'}, 'staff'

@dataclass
class AuthSuParam:
    uid: int

@bp.route('/su')
@validate(query=AuthSuParam)
@auth_response
async def auth_su(_req: Request, query: AuthSuParam, worker: Worker, user: Optional[User]) -> AuthResponse:
    if user is None or not secret.IS_ADMIN(user._store):
        raise AuthError('没有权限')
    if worker.game is None:
        raise AuthError('服务暂时不可用')

    su_user = worker.game.users.user_by_id.get(query.uid, None)
    if su_user is None:
        raise AuthError('用户不存在')
    if secret.IS_ADMIN(su_user._store):
        raise AuthError('不能切换到管理员账号')

    return su_user

# 抱歉了, 新增了屎山代码
MAIL_PATTERN=re.compile(re.compile(r'^[a-zA-Z0-9_.+-]+@(r00team\.cc|mail\.dhu\.edu\.cn)$'))

@bp.route('/normal/send_mail', methods=['POST'])
@json_response
async def normal_send_mail(req: Request):
    mail = req.json.get("mail", "")
    if not re.match(MAIL_PATTERN, mail):
        return {'status': 1, 'message': '邮箱格式不正确, 必须为东华大学邮箱'}
    verify_code = ''.join(rd.choices(string.digits, k=6))
    async with async_session_maker() as sess:
        ip = req.headers.get('X-Forwarded-For', req.ip)
        
        last_history = await sess.scalar(select(MailVerifyCodeStore).filter_by(mail=mail).order_by(MailVerifyCodeStore.timestamp.desc()))
        if last_history is not None and last_history.timestamp + 60 > time.time():
            return {'status': 1, 'message': '一分钟内只能发送一次验证码'}
        
        sess.add(MailVerifyCodeStore(mail=mail, verify_code=verify_code, ip=ip))
        if await send_verify_code(verify_code, mail):
            await sess.commit()
            return {'status': 0, 'message': '发送成功'}
        else:
            return {'status': 1, 'message': '发送失败, 请检查邮箱是否正确或与管理员联系'}

@bp.route('/normal/register', methods=['POST'])
@json_response
async def normal_register(req: Request):
    mail: str = req.json.get("mail", "")
    verify_code = req.json.get("verify_code", "")
    password = req.json.get('password', "")

    async with async_session_maker() as sess:
        mail_record = await sess.scalar(
            select(MailVerifyCodeStore).filter_by(mail=mail).order_by(MailVerifyCodeStore.timestamp.desc()))
        if mail_record is None or mail_record.verify_code!=verify_code or mail_record.timestamp + 86400 < time.time():
            return {'status': 1, 'message': '验证码错误'}
        
        up: Optional[UserPasswordStore] = await sess.scalar(
            select(UserPasswordStore).filter_by(uname=mail))
        if up is None:
            salt = ''.join(rd.choices(string.ascii_letters + string.digits, k=16))
            hashed_password = hashlib.sha512((salt + password).encode('utf-8')).hexdigest()
            sess.add(UserPasswordStore(uname=mail, salt=salt, passw=hashed_password))
            await sess.commit()
            
            worker = req.app.ctx.worker
            try:
                return await _register_or_login(
                    req, worker, f'normal:{mail}', 
                    {
                        'type': 'normal',
                        'info': {},
                        'access_token': ""
                    }, 'staff' if mail.endswith('r00team.cc') else 'other')
            
            except AuthError as e:
                return {'status': 1, 'message': e.message}
        else:
            return {'status': 1, 'message': '邮箱已被注册'}

@bp.route('/normal/login', methods=['POST'])
@json_response
async def auth_normal_res(req: Request):
    mail = req.json.get('mail', None)
    password = req.json.get('password', None)
    if not (mail and password):
        return {'status': 1, 'message': '用户名或密码为空'}
    
    async with async_session_maker() as sess:
        up: Optional[UserPasswordStore] = await sess.scalar(
            select(UserPasswordStore).filter_by(uname=mail))
        if up is None or up.passw != hashlib.sha512((up.salt + password).encode('utf-8')).hexdigest():
            return {'status': 1, 'message': '用户名或密码错误, 也可能是今天你左脚先进的门'}
    
    worker = req.app.ctx.worker
    try:
        return await _register_or_login(
            req, worker, f'normal:{mail}', 
            {
                'type': 'normal',
                'info': {},
                'access_token': ""
            }, 'other')
    except AuthError as e:
        return {'status': 1, 'message': e.message}


@bp.route('/github/login')
async def auth_github_req(req: Request) -> HTTPResponse:
    return oauth2_redirect(
        'https://github.com/login/oauth/authorize',
        {
            'client_id': secret.GITHUB_APP_ID,
        },
        secret.BUILD_OAUTH_CALLBACK_URL(
            req.app.url_for('auth.auth_github_res', _external=True, _scheme=secret.BACKEND_SCHEME, _server=secret.BACKEND_HOSTNAME)
        ),
    )

@bp.route('/github/login/callback')
@auth_response
async def auth_github_res(req: Request, http_client: httpx.AsyncClient, worker: Worker) -> AuthResponse:
    oauth_code = req.args.get('code', None)
    if not oauth_code:
        raise AuthError('OAuth登录失败')

    oauth2_check_state(req)

    token_res = await http_client.post('https://github.com/login/oauth/access_token', params={
        'client_id': secret.GITHUB_APP_ID,
        'client_secret': secret.GITHUB_APP_SECRET,
        'code': oauth_code,
    }, headers={
        'Accept': 'application/json',
    })
    token = token_res.json().get('access_token', None)
    if token is None:
        worker.log('warning', 'api.auth.github', f'get access_token failed:\n{token_res.json()}')
        raise AuthError('GitHub Token不存在')

    info_res = await http_client.get('https://api.github.com/user', headers={
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    })
    info = info_res.json()

    uid = info.get('id', None)
    if uid is None:
        worker.log('warning', 'api.auth.github', f'get user failed:\n{info}')
        raise AuthError('GitHub UID不存在')

    return f'github:{uid}', {
        'type': 'github',
        'info': info,
        'access_token': token
    }, 'other'

@bp.route('/microsoft/login')
async def auth_ms_req(req: Request) -> HTTPResponse:
    return oauth2_redirect(
        'https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize',
        {
            'client_id': secret.MS_APP_ID,
            'response_type': 'code',
            'response_mode': 'query',
            'scope': 'User.Read',
        },
        secret.BUILD_OAUTH_CALLBACK_URL(
            req.app.url_for('auth.auth_ms_res', _external=True, _scheme=secret.BACKEND_SCHEME, _server=secret.BACKEND_HOSTNAME)
        ),
    )

@bp.route('/microsoft/login/callback')
@auth_response
async def auth_ms_res(req: Request, http_client: httpx.AsyncClient, worker: Worker) -> AuthResponse:
    oauth_code = req.args.get('code', None)
    if not oauth_code:
        raise AuthError('OAuth登录失败')

    oauth2_check_state(req)

    token_res = await http_client.post('https://login.microsoftonline.com/consumers/oauth2/v2.0/token', data={
        'client_id': secret.MS_APP_ID,
        'client_secret': secret.MS_APP_SECRET,
        'code': oauth_code,
        'grant_type': 'authorization_code',
        'scope': 'User.Read',
        'redirect_uri': secret.BUILD_OAUTH_CALLBACK_URL(
            req.app.url_for('auth.auth_ms_res', _external=True, _scheme=secret.BACKEND_SCHEME, _server=secret.BACKEND_HOSTNAME)
        ),
    })
    token_json = token_res.json()
    token = token_json.get('access_token', None)
    if token is None:
        worker.log('warning', 'api.auth.ms', f'get access_token failed:\n{token_json}')
        raise AuthError('MS Token不存在')

    info_res = await http_client.get('https://graph.microsoft.com/v1.0/me', headers={
        'Authorization': f'Bearer {token}',
    })
    info = info_res.json()

    uid = info.get('id', None)
    if uid is None:
        worker.log('warning', 'api.auth.ms', f'get user failed:\n{info}')
        raise AuthError('MS UID不存在')

    return f'ms:{uid}', {
        'type': 'microsoft',
        'info': info,
        'access_token': token,
    }, 'other'

@bp.route('/pku/redirect')
async def auth_pku_req(req: Request) -> HTTPResponse:
    return await iaaa_login()

@bp.route('/pku/login')
@auth_response
async def auth_pku_res(req: Request, http_client: httpx.AsyncClient, worker: Worker) -> AuthResponse:
    return await iaaa_check(req, http_client, worker)