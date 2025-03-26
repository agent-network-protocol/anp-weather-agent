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

# Define exempt paths
# EXEMPT_PATHS = ["/agents/travel/weather/api/weather_info", "/agents/travel/weather/ad.json", "/agents/travel/weather/api_files/weather-info.yaml"]
EXEMPT_PATHS = [
    "/agents/travel/hotel/api/hotel/create_order/ph",
    "/agents/travel/hotel/api/cancel_order/ph",
    "/agents/travel/hotel/api/get_order_detail/ph",
    "/.well-known/agent-descriptions", 
    "/",
    "/favicon.ico"
]

# Timestamp expiration time (minutes)
TIMESTAMP_EXPIRATION_MINUTES = 5

# Nonce expiration time (minutes)
NONCE_EXPIRATION_MINUTES = 6

# Add a global variable to store used nonces
USED_NONCES: Dict[str, Dict[str, datetime]] = {}

# Add a global variable to record the last cleanup time
LAST_CLEANUP_TIME: datetime = datetime.now(timezone.utc)

# Cleanup interval (seconds)
CLEANUP_INTERVAL_SECONDS = 60

# Define list of allowed server domains
WBA_SERVER_DOMAINS = ["localhost", "127.0.0.1", "did.agent-connect.com", "service.agent-network-protocol.com"]

def verify_timestamp(timestamp_str: str) -> bool:
    """
    Verify if the timestamp is within the valid period
    
    Args:
        timestamp_str: ISO format timestamp string
        
    Returns:
        bool: Whether the timestamp is valid
    """
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        current_time = datetime.now(timezone.utc)
        time_diff = current_time - timestamp
        
        # Check if timestamp is in the future
        if timestamp > current_time:
            logging.error("Timestamp is in the future")
            return False
            
        # Check if timestamp is expired
        if time_diff > timedelta(minutes=TIMESTAMP_EXPIRATION_MINUTES):
            logging.error(f"Timestamp expired. Diff: {time_diff}")
            return False
            
        return True
    except ValueError as e:
        logging.error(f"Invalid timestamp format: {e}")
        return False

def get_and_validate_domain(request: Request) -> str:
    """
    Get domain from request and validate if it's in the allowed list
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Validated domain
        
    Raises:
        HTTPException: When domain is not in the allowed list
    """
    try:
        host = request.headers.get('host', '')
        # Extract domain from host (remove port number)
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
    """Clean up expired nonce records"""
    try:
        current_time = datetime.now(timezone.utc)
        
        # Clean up expired used nonces
        cleaned_count = 0
        for did in list(USED_NONCES.keys()):
            expired_did_nonces = [n for n, t in USED_NONCES[did].items() 
                                if current_time - t > timedelta(minutes=NONCE_EXPIRATION_MINUTES)]
            for expired_nonce in expired_did_nonces:
                USED_NONCES[did].pop(expired_nonce)
                cleaned_count += 1
                
            # If all nonces for a DID are expired, remove the entire DID entry
            if not USED_NONCES[did]:
                USED_NONCES.pop(did)
        
        # Database cleanup operations (commented out)
        """
        cleanup_query = '''
            DELETE FROM nonces 
            WHERE created_at < %s
        '''
        execute_query(cleanup_query, expiration_time)
        """
        
        if cleaned_count > 0:
            logging.info(f"Cleaned up {cleaned_count} expired nonces")
            
        # Update last cleanup time
        global LAST_CLEANUP_TIME
        LAST_CLEANUP_TIME = current_time
        
    except Exception as e:
        logging.error(f"Error during nonce cleanup: {e}")
        logging.error("Stack trace:")
        traceback.print_exc()

async def check_and_cleanup_if_needed():
    """Check if cleanup of expired nonces is needed, and clean up if necessary"""
    current_time = datetime.now(timezone.utc)
    global LAST_CLEANUP_TIME
    
    # If more time than the cleanup interval has passed since the last cleanup, perform cleanup
    if (current_time - LAST_CLEANUP_TIME).total_seconds() > CLEANUP_INTERVAL_SECONDS:
        await cleanup_expired_nonces()

async def verify_and_record_nonce(did: str, nonce: str) -> bool:
    """
    Verify if nonce is valid and record it in the local dictionary
    
    Args:
        did: DID identifier
        nonce: nonce value to verify
        
    Returns:
        bool: Whether nonce is valid
        
    Raises:
        HTTPException: When nonce is invalid or operation fails
    """
    try:
        # Check if nonce has already been used
        if did in USED_NONCES and nonce in USED_NONCES[did]:
            logging.error(f"Nonce {nonce} has already been used for DID {did}")
            raise HTTPException(
                status_code=401, 
                detail="Nonce has already been used"
            )
            
        # Record new nonce
        current_time = datetime.now(timezone.utc)
        
        # If DID is not in the dictionary, create a new entry
        if did not in USED_NONCES:
            USED_NONCES[did] = {}
            
        # Record nonce usage
        USED_NONCES[did][nonce] = current_time
        
        # Database operations (commented out)
        """
        # Check if nonce already exists
        check_query = '''
            SELECT timestamp, created_at 
            FROM nonces 
            WHERE did = %s AND nonce = %s
        '''
        result = execute_query(check_query, did, nonce)
        
        if result:
            # nonce has been used
            logging.error(f"Nonce {nonce} has already been used for DID {did}")
            raise HTTPException(
                status_code=401, 
                detail="Nonce has already been used"
            )
            
        # Record new nonce
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
    Process DID authentication and generate JWT token
    
    Args:
        authorization: DID authentication header
        domain: Server domain
        
    Returns:
        str: Generated JWT token
        
    Raises:
        HTTPException: When authentication fails
    """
    try:
        did, _, _, _, _ = extract_auth_header_parts(authorization)

        if not did:
            logging.error("DID not found in authorization header")
            raise HTTPException(status_code=401, detail="DID not found in authorization")
        
        # Parse DID document
        did_doc = await resolve_did_wba_document(did)

        logging.info(f"Resolved DID document: {did_doc}")
        logging.info(f"Domain: {domain}")
        logging.info(f"Authorization: {authorization}")
        
        # Verify signature
        is_valid, message = verify_auth_header_signature(authorization, did_doc, domain)
        if not is_valid:
            logging.error(f"Signature verification failed: {message}")
            raise HTTPException(status_code=403, detail="Authentication failed")
        
        # Generate JWT token
        current_time = datetime.now(timezone.utc)
        payload = {
            "sub": did,
            "exp": current_time + timedelta(seconds=300),  # Token 5 minutes later expires
            "iat": current_time
        }

        # Use jwt_config module to get private key
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
    Verify Bearer token
    
    Args:
        token: JWT token
        
    Returns:
        bool: Whether token is valid
        
    Raises:
        HTTPException: When token is invalid or expired
    """
    try:
        # Use jwt_config module to get public key
        public_key = get_jwt_public_key()
        if not public_key:
            logging.error("JWT public key not found")
            raise HTTPException(status_code=500, detail="Server configuration error")
            
        # Verify JWT token
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
    Verify DID request
    
    Args:
        request: FastAPI request object
        authorization: Authentication header (optional)
        
    Returns:
        Tuple[bool, Optional[str]]: (Whether authentication succeeded, Generated token)
        
    Raises:
        HTTPException: When authentication fails
    """
    try:
        # Check if path is exempt
        if request.url.path in EXEMPT_PATHS:
            logging.info(f"Path {request.url.path} is in EXEMPT_PATHS, skipping authentication")
            return True, None
            
        # If authorization is not provided, try to get it from request headers
        if not authorization:
            authorization = request.headers.get("Authorization")
            
        if not authorization:
            logging.error("Authorization header missing")
            raise HTTPException(status_code=401, detail="Authorization header missing, you can use tool https://service.agent-network-protocol.com/anp-explorer/ to access the URL")
        
        auth_lower = authorization.lower()
        logging.info(f"Authorization type: {'DIDwba' if 'didwba ' in auth_lower else 'Bearer' if 'bearer ' in auth_lower else 'Unknown'}")
        
        # Get and validate domain
        domain = get_and_validate_domain(request)
        logging.info(f"Validated domain: {domain}")
        
        # Process DID authentication
        if "didwba " in auth_lower:
            logging.info("Processing DID authentication")
            # Extract DID, nonce, and timestamp
            did, nonce, timestamp, _, _ = extract_auth_header_parts(authorization)
            logging.info(f"Extracted DID: {did}, nonce: {nonce}, timestamp: {timestamp}")
            
            # Verify timestamp
            if not timestamp or not verify_timestamp(timestamp):
                logging.error(f"Invalid or expired timestamp: {timestamp}")
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid or expired timestamp"
                )
            logging.info("Timestamp verification successful")
            
            # Verify and record nonce
            await verify_and_record_nonce(did, nonce)
            logging.info("Nonce verification and recording successful")
            
            # Generate token
            token = await generate_did_auth_token(authorization, domain)
            logging.info(f"Generated token: {token[:30]}...")
            return True, token
        
        # Process Bearer token authentication
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
    DID authentication middleware
    
    Args:
        request: FastAPI request object
        call_next: Next middleware or route handler function
        
    Returns:
        Response: Response object
    """
    # Check if cleanup of expired nonces is needed
    await check_and_cleanup_if_needed()
    
    try:
        logging.info(f"Processing request to {request.url.path}")
        is_authenticated, token = await authenticate_did_request(request)
        
        if not is_authenticated:
            logging.error(f"Authentication failed: path={request.url.path}")
            return JSONResponse(status_code=401, content={"detail": "Authentication failed"})
            
        # If a new token is generated, add it to response headers
        response = await call_next(request)
        
        if token:
            # Modify response headers, add token
            logging.info(f"Adding token to response headers: {token[:30]}...")
            response.headers["Authorization"] = f"Bearer {token}"
        else:
            logging.info("No token generated, not adding to response headers")
            
        return response
        
    except HTTPException as exc:
        logging.error(f"Authentication exception: status_code={exc.status_code}, detail={exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}) 