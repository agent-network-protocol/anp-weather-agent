from datetime import datetime, timezone, timedelta
import jwt
import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Tuple, Dict


from agent_connect.authentication import (
    verify_auth_header_signature,
    resolve_did_wba_document,
    extract_auth_header_parts
)
from api_router.jwt_config import get_jwt_private_key, get_jwt_public_key

# 定义豁免路径
# EXEMPT_PATHS = ["/agents/travel/weather/api/weather_info", "/agents/travel/weather/ad.json", "/agents/travel/weather/api_files/weather-info.yaml"]
EXEMPT_PATHS = [
    "/agents/travel/hotel/api/hotel/create_order/ph",
    "/agents/travel/hotel/api/cancel_order/ph",
    "/agents/travel/hotel/api/get_order_detail/ph",
    "/.well-known/agent-descriptions", 
    "/",
    "/favicon.ico"
]

# 时间戳过期时间（分钟）
TIMESTAMP_EXPIRATION_MINUTES = 5

# nonce 过期时间（分钟）
NONCE_EXPIRATION_MINUTES = 6

# 添加全局变量来存储已使用的 nonce
USED_NONCES: Dict[str, Dict[str, datetime]] = {}

# 添加全局变量记录上次清理时间
LAST_CLEANUP_TIME: datetime = datetime.now(timezone.utc)

# 清理间隔（秒）
CLEANUP_INTERVAL_SECONDS = 60

# 定义允许的服务器域名列表
WBA_SERVER_DOMAINS = ["localhost", "127.0.0.1", "did.agent-connect.com", "service.agent-network-protocol.com"]

def verify_timestamp(timestamp_str: str) -> bool:
    """
    验证时间戳是否在有效期内
    
    Args:
        timestamp_str: ISO格式的时间戳字符串
        
    Returns:
        bool: 时间戳是否有效
    """
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        current_time = datetime.now(timezone.utc)
        time_diff = current_time - timestamp
        
        # 检查时间戳是否在未来
        if timestamp > current_time:
            logging.error("Timestamp is in the future")
            return False
            
        # 检查时间戳是否过期
        if time_diff > timedelta(minutes=TIMESTAMP_EXPIRATION_MINUTES):
            logging.error(f"Timestamp expired. Diff: {time_diff}")
            return False
            
        return True
    except ValueError as e:
        logging.error(f"Invalid timestamp format: {e}")
        return False

def get_and_validate_domain(request: Request) -> str:
    """
    从请求中获取域名并验证是否在允许列表中
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        str: 验证通过的域名
        
    Raises:
        HTTPException: 当域名不在允许列表中时
    """
    try:
        host = request.headers.get('host', '')
        # 从host中提取域名（去除端口号）
        domain = host.split(':')[0]
        
        # if domain not in WBA_SERVER_DOMAINS:
            #     logging.error(f"Domain {domain} not in allowed list: {WBA_SERVER_DOMAINS}")
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Invalid domain for DID operation"
        #     )
        
        return domain
    except Exception as e:
        logging.error(f"Error validating domain: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid domain"
        )

async def cleanup_expired_nonces():
    """清理过期的 nonce 记录"""
    try:
        current_time = datetime.now(timezone.utc)
        
        # 清理已使用的过期 nonce
        cleaned_count = 0
        for did in list(USED_NONCES.keys()):
            expired_did_nonces = [n for n, t in USED_NONCES[did].items() 
                                if current_time - t > timedelta(minutes=NONCE_EXPIRATION_MINUTES)]
            for expired_nonce in expired_did_nonces:
                USED_NONCES[did].pop(expired_nonce)
                cleaned_count += 1
                
            # 如果 DID 的所有 nonce 都已过期，删除整个 DID 条目
            if not USED_NONCES[did]:
                USED_NONCES.pop(did)
        
        # 数据库清理操作（注释掉）
        """
        cleanup_query = '''
            DELETE FROM nonces 
            WHERE created_at < %s
        '''
        execute_query(cleanup_query, expiration_time)
        """
        
        if cleaned_count > 0:
            logging.info(f"Cleaned up {cleaned_count} expired nonces")
            
        # 更新上次清理时间
        global LAST_CLEANUP_TIME
        LAST_CLEANUP_TIME = current_time
        
    except Exception as e:
        logging.error(f"Error during nonce cleanup: {e}")
        logging.error("Stack trace:")
        traceback.print_exc()

async def check_and_cleanup_if_needed():
    """检查是否需要清理过期的 nonce，如果需要则清理"""
    current_time = datetime.now(timezone.utc)
    global LAST_CLEANUP_TIME
    
    # 如果距离上次清理时间超过了清理间隔，则执行清理
    if (current_time - LAST_CLEANUP_TIME).total_seconds() > CLEANUP_INTERVAL_SECONDS:
        await cleanup_expired_nonces()

async def verify_and_record_nonce(did: str, nonce: str) -> bool:
    """
    验证 nonce 是否有效并记录到本地字典
    
    Args:
        did: DID 标识符
        nonce: 需要验证的 nonce 值
        
    Returns:
        bool: nonce 是否有效
        
    Raises:
        HTTPException: 当 nonce 无效或操作失败时
    """
    try:
        # 检查 nonce 是否已被使用
        if did in USED_NONCES and nonce in USED_NONCES[did]:
            logging.error(f"Nonce {nonce} has already been used for DID {did}")
            raise HTTPException(
                status_code=401, 
                detail="Nonce has already been used"
            )
            
        # 记录新的 nonce
        current_time = datetime.now(timezone.utc)
        
        # 如果 DID 不在字典中，创建一个新的条目
        if did not in USED_NONCES:
            USED_NONCES[did] = {}
            
        # 记录 nonce 使用情况
        USED_NONCES[did][nonce] = current_time
        
        # 数据库操作（注释掉）
        """
        # 检查 nonce 是否已存在
        check_query = '''
            SELECT timestamp, created_at 
            FROM nonces 
            WHERE did = %s AND nonce = %s
        '''
        result = execute_query(check_query, did, nonce)
        
        if result:
            # nonce 已被使用
            logging.error(f"Nonce {nonce} has already been used for DID {did}")
            raise HTTPException(
                status_code=401, 
                detail="Nonce has already been used"
            )
            
        # 记录新的 nonce
        current_time = datetime.now(timezone.utc)
        insert_query = '''
            INSERT INTO nonces 
            (did, nonce, timestamp, created_at) 
            VALUES (%s, %s, %s, %s)
        '''
        execute_insert(
            insert_query, 
            did, 
            nonce, 
            current_time,
            current_time
        )
        """
        
        return True
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Error verifying/recording nonce: {e}")
        logging.error("Stack trace:")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail="Error processing nonce"
        )

async def generate_did_auth_token(authorization: str, domain: str) -> str:
    """
    处理 DID 认证并生成 JWT token
    
    Args:
        authorization: DID 认证头
        domain: 服务器域名
        
    Returns:
        str: 生成的 JWT token
        
    Raises:
        HTTPException: 当认证失败时
    """
    try:
        did, _, _, _, _ = extract_auth_header_parts(authorization)

        if not did:
            logging.error("DID not found in authorization header")
            raise HTTPException(status_code=401, detail="DID not found in authorization")
        
        # 解析DID文档
        did_doc = await resolve_did_wba_document(did)

        logging.info(f"Resolved DID document: {did_doc}")
        logging.info(f"Domain: {domain}")
        logging.info(f"Authorization: {authorization}")
        
        # 验证签名
        is_valid, message = verify_auth_header_signature(authorization, did_doc, domain)
        if not is_valid:
            logging.error(f"Signature verification failed: {message}")
            raise HTTPException(status_code=403, detail="Authentication failed")
        
        # 生成 JWT token
        current_time = datetime.now(timezone.utc)
        payload = {
            "sub": did,
            "exp": current_time + timedelta(seconds=300),  # Token 5分钟后过期
            "iat": current_time
        }

        # 使用jwt_config模块获取私钥
        private_key = get_jwt_private_key()
        if not private_key:
            logging.error("JWT private key not found")
            raise HTTPException(status_code=500, detail="Server configuration error")
        
        token = jwt.encode(payload, private_key, algorithm="RS256")
        logging.info(f"Generated JWT token for DID: {did}")
        return token
        
    except Exception as e:
        logging.error(f"Error in DID authentication: {e}")
        raise

async def verify_bearer_token(token: str) -> bool:
    """
    验证 Bearer token
    
    Args:
        token: JWT token
        
    Returns:
        bool: token 是否有效
        
    Raises:
        HTTPException: 当 token 无效或过期时
    """
    try:
        # 使用jwt_config模块获取公钥
        public_key = get_jwt_public_key()
        if not public_key:
            logging.error("JWT public key not found")
            raise HTTPException(status_code=500, detail="Server configuration error")
            
        # 验证 JWT token
        jwt.decode(token, public_key, algorithms=["RS256"])
        logging.info("Bearer token verification successful")
        return True
    except jwt.ExpiredSignatureError:
        logging.error("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        logging.error("Invalid token")
        raise HTTPException(status_code=403, detail="Invalid token")

async def authenticate_did_request(request: Request, authorization: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    验证 DID 请求
    
    Args:
        request: FastAPI 请求对象
        authorization: 认证头（可选）
        
    Returns:
        Tuple[bool, Optional[str]]: (是否认证成功, 生成的 token)
        
    Raises:
        HTTPException: 当认证失败时
    """
    try:
        # 检查路径是否豁免
        if request.url.path in EXEMPT_PATHS:
            logging.info(f"Path {request.url.path} is in EXEMPT_PATHS, skipping authentication")
            return True, None
            
        # 如果未提供 authorization，尝试从请求头获取
        if not authorization:
            authorization = request.headers.get("Authorization")
            
        if not authorization:
            logging.error("Authorization header missing")
            raise HTTPException(status_code=401, detail="Authorization header missing, you can use tool https://service.agent-network-protocol.com/anp-explorer/ to access the URL")
        
        auth_lower = authorization.lower()
        logging.info(f"Authorization type: {'DIDwba' if 'didwba ' in auth_lower else 'Bearer' if 'bearer ' in auth_lower else 'Unknown'}")
        
        # 获取并验证域名
        domain = get_and_validate_domain(request)
        logging.info(f"Validated domain: {domain}")
        
        # 处理 DID 认证
        if "didwba " in auth_lower:
            logging.info("Processing DID authentication")
            # 提取 DID、nonce 和 timestamp
            did, nonce, timestamp, _, _ = extract_auth_header_parts(authorization)
            logging.info(f"Extracted DID: {did}, nonce: {nonce}, timestamp: {timestamp}")
            
            # 验证 timestamp
            if not timestamp or not verify_timestamp(timestamp):
                logging.error(f"Invalid or expired timestamp: {timestamp}")
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid or expired timestamp"
                )
            logging.info("Timestamp verification successful")
            
            # 验证并记录 nonce
            await verify_and_record_nonce(did, nonce)
            logging.info("Nonce verification and recording successful")
            
            # 生成 token
            token = await generate_did_auth_token(authorization, domain)
            logging.info(f"Generated token: {token[:30]}...")
            return True, token
        
        # 处理 Bearer token 认证
        elif "bearer " in auth_lower:
            logging.info("Processing Bearer token authentication")
            token = authorization[authorization.lower().find("bearer ") + 7:]
            logging.info(f"Extracted token: {token[:30]}...")
            if await verify_bearer_token(token):
                logging.info("Bearer token verification successful")
                return True, None
        
        else:
            logging.error("Unsupported authorization type")
            raise HTTPException(status_code=401, detail="Unsupported authorization type")
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error during authentication: {e}")
        logging.error("Stack trace:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

async def did_auth_middleware(request: Request, call_next):
    """
    DID 认证中间件
    
    Args:
        request: FastAPI 请求对象
        call_next: 下一个中间件或路由处理函数
        
    Returns:
        Response: 响应对象
    """
    # 检查是否需要清理过期的 nonce
    await check_and_cleanup_if_needed()
    
    try:
        logging.info(f"Processing request to {request.url.path}")
        is_authenticated, token = await authenticate_did_request(request)
        
        if not is_authenticated:
            logging.error(f"Authentication failed: path={request.url.path}")
            return JSONResponse(status_code=401, content={"detail": "Authentication failed"})
            
        # 如果生成了新 token，添加到响应头
        response = await call_next(request)
        
        if token:
            # 修改响应头，添加 token
            logging.info(f"Adding token to response headers: {token[:30]}...")
            response.headers["Authorization"] = f"Bearer {token}"
        else:
            logging.info("No token generated, not adding to response headers")
            
        return response
        
    except HTTPException as exc:
        logging.error(f"Authentication exception: status_code={exc.status_code}, detail={exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}) 