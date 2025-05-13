# 【服务端日志】
## Log file:  /var/log/anp_weather_agent\anp_weather_agent_20250513.log
## Log file:  /var/log/anp_weather_agent\anp_weather_agent_20250513.log
## ?[92m2025-05-13 06:32:27,516 - INFO - anp_weather_agent.py:76 - Starting
server on port: 9870
## ?[0m
## ?[32mINFO?[0m:     Started server process [?[36m116328?[0m]
## ?[32mINFO?[0m:     Waiting for application startup.
## ?[32mINFO?[0m:     Application startup complete.
## ?[32mINFO?[0m:     Uvicorn running on ?[1mhttp://127.0.0.1:9870?[0m (Pres
s CTRL+C to quit)
## ?[92m2025-05-13 06:32:39,544 - INFO - did_auth_middleware.py:443 - Proces
sing request to /
## ?[0m
## ?[92m2025-05-13 06:32:39,547 - INFO - did_auth_middleware.py:353 - Path /
 is in EXEMPT_PATHS, skipping authentication
## ?[0m
## ?[92m2025-05-13 06:32:39,551 - INFO - router.py:68 - Received root path r
equest for host: 127.0.0.1
## ?[0m
## ?[92m2025-05-13 06:32:39,554 - INFO - did_auth_middleware.py:460 - No tok
en generated, not adding to response headers
## ?[0m
## ?[32mINFO?[0m:     127.0.0.1:64429 - "?[1mGET / HTTP/1.1?[0m" ?[32m200 OK
## ?[0m
## ?[92m2025-05-13 06:32:42,592 - INFO - did_auth_middleware.py:443 - Proces
sing request to /weather
## ?[0m
## ?[92m2025-05-13 06:32:42,595 - INFO - did_auth_middleware.py:370 - Author
ization type: DIDwba
## ?[0m
## ?[92m2025-05-13 06:32:42,598 - INFO - did_auth_middleware.py:376 - Valida
ted domain: 127.0.0.1
## ?[0m
## ?[92m2025-05-13 06:32:42,602 - INFO - did_auth_middleware.py:380 - Proces
sing DID authentication
## ?[0m
## ?[92m2025-05-13 06:32:42,606 - INFO - did_auth_middleware.py:383 - Extrac
ted DID: did:wba:agent-did.com:test:public, nonce: 09d6b7a709708c66f1c020
d769c2cdb0, timestamp: 2025-05-12T22:32:39Z
## ?[0m
## ?[92m2025-05-13 06:32:42,607 - INFO - did_auth_middleware.py:393 - Timest
amp verification successful
## ?[0m
## ?[92m2025-05-13 06:32:42,612 - INFO - did_auth_middleware.py:397 - Nonce
verification and recording successful
## ?[0m
## ?[92m2025-05-13 06:32:42,624 - INFO - did_wba.py:172 - Resolving DID docu
ment for: did:wba:agent-did.com:test:public
## ?[0m
## ?[92m2025-05-13 06:32:43,556 - INFO - did_wba.py:220 - Successfully resol
ved DID document for: did:wba:agent-did.com:test:public
## ?[0m
## ?[92m2025-05-13 06:32:43,608 - INFO - did_auth_middleware.py:268 - Resolv
ed DID document: {'@context': ['https://www.w3.org/ns/did/v1', 'https://w
3id.org/security/suites/jws-2020/v1', 'https://w3id.org/security/suites/s
ecp256k1-2019/v1'], 'id': 'did:wba:agent-did.com:test:public', 'verificat
ionMethod': [{'id': 'did:wba:agent-did.com:test:public#key-1', 'type': 'E
cdsaSecp256k1VerificationKey2019', 'controller': 'did:wba:agent-did.com:t
est:public', 'publicKeyJwk': {'kty': 'EC', 'crv': 'secp256k1', 'x': 'kNcf
Vufb4qxUpTC7kT6V56zSFEXbyo3nTDUFxqaZbKs', 'y': 'upHpNoIm8h6cDRZqNWjb4VXba
niq2zz43yQoiR8Zfqs', 'kid': '4QOVubQtyJL_fzKreUfKDTOjrYAFRsq6XZ4Itqn2jLg'
}}], 'authentication': ['did:wba:agent-did.com:test:public#key-1']}
## ?[0m
## ?[92m2025-05-13 06:32:43,658 - INFO - did_auth_middleware.py:269 - Domain
: 127.0.0.1
## ?[0m
## ?[92m2025-05-13 06:32:43,733 - INFO - did_auth_middleware.py:270 - Author
ization: DIDWba did="did:wba:agent-did.com:test:public", nonce="09d6b7a70
9708c66f1c020d769c2cdb0", timestamp="2025-05-12T22:32:39Z", verification_
method="key-1", signature="fhwnjVRUnT8HwaD_zGSQQGSUW9k9wUcS_HLxtVv7Zncu98
bvecQD1zA5euB7z0X85VMW06yEEJDNbd4nVYcUDw"
## ?[0m
## ?[92m2025-05-13 06:32:43,749 - INFO - did_wba.py:625 - Starting DID authe
ntication header verification
## ?[0m
## ?[92m2025-05-13 06:32:43,822 - INFO - jwt_config.py:34 - Successfully rea
d private key from doc/test_jwt_key/private_key.pem
## ?[0m
## ?[92m2025-05-13 06:32:44,029 - INFO - did_auth_middleware.py:294 - Genera
ted JWT token for DID: did:wba:agent-did.com:test:public
## ?[0m
## ?[92m2025-05-13 06:32:44,082 - INFO - did_auth_middleware.py:401 - Genera
ted token: eyJhbGciOiJSUzI1NiIsInR5cCI6Ik...
## ?[0m
## ?[92m2025-05-13 06:32:44,100 - INFO - did_auth_middleware.py:457 - Adding
 token to response headers: eyJhbGciOiJSUzI1NiIsInR5cCI6Ik...
## ?[0m
## ?[32mINFO?[0m:     127.0.0.1:64435 - "?[1mGET /weather HTTP/1.1?[0m" ?[31
m404 Not Found?[0m
## ?[92m2025-05-13 06:32:45,740 - INFO - did_auth_middleware.py:443 - Proces
sing request to /
## ?[0m
## ?[92m2025-05-13 06:32:45,741 - INFO - did_auth_middleware.py:353 - Path /
 is in EXEMPT_PATHS, skipping authentication
## ?[0m
## ?[92m2025-05-13 06:32:45,743 - INFO - router.py:68 - Received root path r
equest for host: 127.0.0.1
## ?[0m
## ?[92m2025-05-13 06:32:45,745 - INFO - did_auth_middleware.py:460 - No tok
en generated, not adding to response headers
## ?[0m
## ?[32mINFO?[0m:     127.0.0.1:64442 - "?[1mGET / HTTP/1.1?[0m" ?[32m200 OK
## ?[0m
## ?[92m2025-05-13 06:32:47,550 - INFO - did_auth_middleware.py:443 - Proces
sing request to /openapi.json
## ?[0m
## ?[92m2025-05-13 06:32:47,551 - INFO - did_auth_middleware.py:370 - Author
ization type: DIDwba
## ?[0m
## ?[92m2025-05-13 06:32:47,552 - INFO - did_auth_middleware.py:376 - Valida
ted domain: 127.0.0.1
## ?[0m
## ?[92m2025-05-13 06:32:47,553 - INFO - did_auth_middleware.py:380 - Proces
sing DID authentication
## ?[0m
## ?[92m2025-05-13 06:32:47,556 - INFO - did_auth_middleware.py:383 - Extrac
ted DID: did:wba:agent-did.com:test:public, nonce: 09d6b7a709708c66f1c020
d769c2cdb0, timestamp: 2025-05-12T22:32:39Z
## ?[0m
## ?[92m2025-05-13 06:32:47,557 - INFO - did_auth_middleware.py:393 - Timest
amp verification successful
## ?[0m
## ?[91m2025-05-13 06:32:47,557 - ERROR - did_auth_middleware.py:184 - Nonce
 09d6b7a709708c66f1c020d769c2cdb0 has already been used for DID did:wba:a
gent-did.com:test:public
## ?[0m
## ?[91m2025-05-13 06:32:47,558 - ERROR - did_auth_middleware.py:465 - Authe
ntication exception: status_code=401, detail=Nonce has already been used
## ?[0m
## ?[32mINFO?[0m:     127.0.0.1:64445 - "?[1mGET /openapi.json HTTP/1.1?[0m"
 ?[31m401 Unauthorized?[0m
## ?[92m2025-05-13 06:32:47,568 - INFO - did_auth_middleware.py:443 - Proces
sing request to /openapi.json
## ?[0m
## ?[92m2025-05-13 06:32:47,569 - INFO - did_auth_middleware.py:370 - Author
ization type: DIDwba
## ?[0m
## ?[92m2025-05-13 06:32:47,570 - INFO - did_auth_middleware.py:376 - Valida
ted domain: 127.0.0.1
## ?[0m
## ?[92m2025-05-13 06:32:47,570 - INFO - did_auth_middleware.py:380 - Proces
sing DID authentication
## ?[0m
## ?[92m2025-05-13 06:32:47,571 - INFO - did_auth_middleware.py:383 - Extrac
ted DID: did:wba:agent-did.com:test:public, nonce: 11569883380c695e991322
3ca4ce87e6, timestamp: 2025-05-12T22:32:47Z
## ?[0m
## ?[92m2025-05-13 06:32:47,572 - INFO - did_auth_middleware.py:393 - Timest
amp verification successful
## ?[0m
## ?[92m2025-05-13 06:32:47,573 - INFO - did_auth_middleware.py:397 - Nonce
verification and recording successful
## ?[0m
## ?[92m2025-05-13 06:32:47,573 - INFO - did_wba.py:172 - Resolving DID docu
ment for: did:wba:agent-did.com:test:public
## ?[0m
## ?[92m2025-05-13 06:32:48,319 - INFO - did_wba.py:220 - Successfully resol
ved DID document for: did:wba:agent-did.com:test:public
## ?[0m
## ?[92m2025-05-13 06:32:48,324 - INFO - did_auth_middleware.py:268 - Resolv
ed DID document: {'@context': ['https://www.w3.org/ns/did/v1', 'https://w
3id.org/security/suites/jws-2020/v1', 'https://w3id.org/security/suites/s
ecp256k1-2019/v1'], 'id': 'did:wba:agent-did.com:test:public', 'verificat
ionMethod': [{'id': 'did:wba:agent-did.com:test:public#key-1', 'type': 'E
cdsaSecp256k1VerificationKey2019', 'controller': 'did:wba:agent-did.com:t
est:public', 'publicKeyJwk': {'kty': 'EC', 'crv': 'secp256k1', 'x': 'kNcf
Vufb4qxUpTC7kT6V56zSFEXbyo3nTDUFxqaZbKs', 'y': 'upHpNoIm8h6cDRZqNWjb4VXba
niq2zz43yQoiR8Zfqs', 'kid': '4QOVubQtyJL_fzKreUfKDTOjrYAFRsq6XZ4Itqn2jLg'
}}], 'authentication': ['did:wba:agent-did.com:test:public#key-1']}
## ?[0m
## ?[92m2025-05-13 06:32:48,328 - INFO - did_auth_middleware.py:269 - Domain
: 127.0.0.1
## ?[0m
## ?[92m2025-05-13 06:32:48,330 - INFO - did_auth_middleware.py:270 - Author
ization: DIDWba did="did:wba:agent-did.com:test:public", nonce="115698833
80c695e9913223ca4ce87e6", timestamp="2025-05-12T22:32:47Z", verification_
method="key-1", signature="6jaedKeUUCABokziwFX3QC5DREySi6JF4jLUGryftnI1mt
dkPSw118pxYnzyq2A9K0JasTxCJbnsQ4E3QpZ-RQ"
## ?[0m
## ?[92m2025-05-13 06:32:48,337 - INFO - did_wba.py:625 - Starting DID authe
ntication header verification
## ?[0m
## ?[92m2025-05-13 06:32:48,342 - INFO - jwt_config.py:34 - Successfully rea
d private key from doc/test_jwt_key/private_key.pem
## ?[0m
## ?[92m2025-05-13 06:32:48,446 - INFO - did_auth_middleware.py:294 - Genera
ted JWT token for DID: did:wba:agent-did.com:test:public
## ?[0m
## ?[92m2025-05-13 06:32:48,449 - INFO - did_auth_middleware.py:401 - Genera
ted token: eyJhbGciOiJSUzI1NiIsInR5cCI6Ik...
## ?[0m
## ?[92m2025-05-13 06:32:48,469 - INFO - did_auth_middleware.py:457 - Adding
 token to response headers: eyJhbGciOiJSUzI1NiIsInR5cCI6Ik...
## ?[0m
## ?[32mINFO?[0m:     127.0.0.1:64446 - "?[1mGET /openapi.json HTTP/1.1?[0m"
 ?[32m200 OK?[0m
## ?[92m2025-05-13 06:32:50,778 - INFO - did_auth_middleware.py:443 - Proces
sing request to /api/weather_info
## ?[0m
## ?[92m2025-05-13 06:32:50,780 - INFO - did_auth_middleware.py:370 - Author
ization type: Bearer
## ?[0m
## ?[92m2025-05-13 06:32:50,782 - INFO - did_auth_middleware.py:376 - Valida
ted domain: 127.0.0.1
## ?[0m
## ?[92m2025-05-13 06:32:50,784 - INFO - did_auth_middleware.py:406 - Proces
sing Bearer token authentication
## ?[0m
## ?[92m2025-05-13 06:32:50,789 - INFO - did_auth_middleware.py:408 - Extrac
ted token: eyJhbGciOiJSUzI1NiIsInR5cCI6Ik...
## ?[0m
## ?[92m2025-05-13 06:32:50,791 - INFO - jwt_config.py:58 - Successfully rea
d public key from doc/test_jwt_key/public_key.pem
## ?[0m
## ?[92m2025-05-13 06:32:50,797 - INFO - did_auth_middleware.py:324 - Bearer
 token verification successful
## ?[0m
## ?[92m2025-05-13 06:32:50,799 - INFO - did_auth_middleware.py:410 - Bearer
 token verification successful
## ?[0m
## ?[92m2025-05-13 06:32:50,806 - INFO - weather_info_router.py:49 - Receive
d weather query parameters: cityName=苏州
## ?[0m
## ?[92m2025-05-13 06:32:51,038 - INFO - weather_info_router.py:79 - Retriev
ed weather data: {
  "status": "1",
  "count": "1",
  "info": "OK",
  "infocode": "10000",
  "forecasts": [
    {
      "city": "\u82cf\u5dde\u5e02",
      "adcode": "320500",
      "province": "\u6c5f\u82cf",
      "reporttime": "2025-05-13 06:01:42",
      "casts": [
        {
          "date": "2025-05-13",
          "week": "2",
          "dayweather": "\u9634",
          "nightweather": "\u9634",
          "daytemp": "29",
          "nighttemp": "19",
          "daywind": "\u4e1c\u5357",
          "nightwind": "\u4e1c\u5357",
          "daypower": "1-3",
          "nightpower": "1-3",
          "daytemp_float": "29.0",
          "nighttemp_float": "19.0"
        },
        {
          "date": "2025-05-14",
          "week": "3",
          "dayweather": "\u9634",
          "nightweather": "\u9634",
          "daytemp": "31",
          "nighttemp": "22",
          "daywind": "\u5357",
          "nightwind": "\u5357",
          "daypower": "1-3",
          "nightpower": "1-3",
          "daytemp_float": "31.0",
          "nighttemp_float": "22.0"
        },
        {
          "date": "2025-05-15",
          "week": "4",
          "dayweather": "\u9634",
          "nightweather": "\u4e2d\u96e8",
          "daytemp": "27",
          "nighttemp": "21",
          "daywind": "\u4e1c\u5357",
          "nightwind": "\u4e1c\u5357",
          "daypower": "1-3",
          "nightpower": "1-3",
          "daytemp_float": "27.0",
          "nighttemp_float": "21.0"
        },
        {
          "date": "2025-05-16",
          "week": "5",
          "dayweather": "\u5c0f\u96e8",
          "nightweather": "\u591a\u4e91",
          "daytemp": "27",
          "nighttemp": "20",
          "daywind": "\u897f\u5357",
          "nightwind": "\u897f\u5357",
          "daypower": "1-3",
          "nightpower": "1-3",
          "daytemp_float": "27.0",
          "nighttemp_float": "20.0"
        }
      ]
    }
  ]
}
## ?[0m
## ?[92m2025-05-13 06:32:51,054 - INFO - did_auth_middleware.py:460 - No tok
en generated, not adding to response headers
## ?[0m
## ?[32mINFO?[0m:     127.0.0.1:64454 - "?[1mGET /api/weather_info?cityName=
%E8%8B%8F%E5%B7%9E HTTP/1.1?[0m" ?[32m200 OK?[0m

# 【客户端日志】
## [2025-05-13 06:16:36] INFO     root: Logging to file: E:\ANP_PROJ\anp-examples\anp_examples\utils\..\..\logs\anp-examples.log
## [2025-05-13 06:16:43] INFO     root: Logging to file: E:\ANP_PROJ\anp-examples\anp_examples\utils\..\..\logs\anp-examples.log
## [2025-05-13 06:16:44] INFO     root: Logging to file: E:\ANP_PROJ\anp-examples\anp_examples\utils\..\..\logs\anp-examples.log
## [2025-05-13 06:32:37] INFO     root: ANPTool initialized - DID path: E:\ANP_PROJ\anp-examples\use_did_test_public\did.json, private key path: E:\ANP_PROJ\anp-examples\use_did_test_public\key-1_private.pem
## [2025-05-13 06:32:37] INFO     root: DIDWbaAuthHeader initialized
## [2025-05-13 06:32:39] INFO     root: ANP request: GET http://127.0.0.1:9870
## [2025-05-13 06:32:39] INFO     root: Loaded DID document: E:\ANP_PROJ\anp-examples\use_did_test_public\did.json
## [2025-05-13 06:32:39] INFO     root: Starting to generate DID authentication header.
## [2025-05-13 06:32:39] INFO     root: Successfully generated DID authentication header.
## [2025-05-13 06:32:39] INFO     root: Generated authentication header for domain 127.0.0.1: DIDWba did="did:wba:agent-did....
## [2025-05-13 06:32:39] INFO     root: Using DID authentication header for domain 127.0.0.1
## [2025-05-13 06:32:39] INFO     root: ANP response: status code 200
## [2025-05-13 06:32:39] INFO     root: Domain: 127.0.0.1 ; auth_header: None
## [2025-05-13 06:32:39] INFO     root: Successfully parsed JSON response
## [2025-05-13 06:32:39] INFO     root: Successfully obtained initial URL: http://127.0.0.1:9870
## [2025-05-13 06:32:39] INFO     root: Starting crawl iteration 1/20
## [2025-05-13 06:32:42] INFO     httpx: HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
## [2025-05-13 06:32:42] INFO     root: Model response: 
## [2025-05-13 06:32:42] INFO     root: Tool calls: [ChatCompletionMessageToolCall(id='call_0333e81756ab4b3e81cbfb', function=Function(arguments='{"url": "http://127.0.0.1:9870/weather", "method": "GET"}', name='anp_tool'), type='function', index=0)]
## [2025-05-13 06:32:42] INFO     root: ANP request: GET http://127.0.0.1:9870/weather
## [2025-05-13 06:32:42] INFO     root: Using DID authentication header for domain 127.0.0.1
## [2025-05-13 06:32:44] INFO     root: ANP response: status code 404
## [2025-05-13 06:32:44] INFO     root: Successfully parsed JSON response
## [2025-05-13 06:32:44] INFO     root: ANPTool response [url: http://127.0.0.1:9870/weather]
## [2025-05-13 06:32:44] INFO     root: Starting crawl iteration 2/20
## [2025-05-13 06:32:45] INFO     httpx: HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
## [2025-05-13 06:32:45] INFO     root: Model response: 
## [2025-05-13 06:32:45] INFO     root: Tool calls: [ChatCompletionMessageToolCall(id='call_88d57396899e41b98331be', function=Function(arguments='{"url": "http://127.0.0.1:9870", "method": "GET"}', name='anp_tool'), type='function', index=0)]
## [2025-05-13 06:32:45] INFO     root: ANP request: GET http://127.0.0.1:9870
## [2025-05-13 06:32:45] INFO     root: Using DID authentication header for domain 127.0.0.1
## [2025-05-13 06:32:45] INFO     root: ANP response: status code 200
## [2025-05-13 06:32:45] INFO     root: Domain: 127.0.0.1 ; auth_header: None
## [2025-05-13 06:32:45] INFO     root: Successfully parsed JSON response
## [2025-05-13 06:32:45] INFO     root: ANPTool response [url: http://127.0.0.1:9870]
## [2025-05-13 06:32:45] INFO     root: Starting crawl iteration 3/20
## [2025-05-13 06:32:47] INFO     httpx: HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
## [2025-05-13 06:32:47] INFO     root: Model response: 
## [2025-05-13 06:32:47] INFO     root: Tool calls: [ChatCompletionMessageToolCall(id='call_69b9099e7e0140b5aa76fe', function=Function(arguments='{"url": "http://127.0.0.1:9870/openapi.json", "method": "GET"}', name='anp_tool'), type='function', index=0)]
## [2025-05-13 06:32:47] INFO     root: ANP request: GET http://127.0.0.1:9870/openapi.json
## [2025-05-13 06:32:47] INFO     root: Using DID authentication header for domain 127.0.0.1
## [2025-05-13 06:32:47] INFO     root: ANP response: status code 401
## [2025-05-13 06:32:47] WARNING  root: Authentication failed (401), trying to get authentication again
## [2025-05-13 06:32:47] INFO     root: Starting to generate DID authentication header.
## [2025-05-13 06:32:47] INFO     root: Successfully generated DID authentication header.
## [2025-05-13 06:32:47] INFO     root: Generated authentication header for domain 127.0.0.1: DIDWba did="did:wba:agent-did....
## [2025-05-13 06:32:47] INFO     root: Using DID authentication header for domain 127.0.0.1
## [2025-05-13 06:32:48] INFO     root: ANP retry response: status code 200
## [2025-05-13 06:32:48] INFO     root: Domain: 127.0.0.1 ; auth_header: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6d2JhOmFnZW50LWRpZC5jb206dGVzdDpwdWJsaWMiLCJleHAiOjE3NDcwODk0NjgsImlhdCI6MTc0NzA4OTE2OH0.XX19S5mPhiGkUnliNtbm9yrF85L6JpcMIe6zyaEzp51f4zDgJdkLIvK6L7CRbc-2uNOAsMNbuUuOov4r4v45F1gL3nwuh8elnFwhZh55shPqmPjWKpWlRufqPCqWMEvSeZomChmfYWTdV27GDy8mrw_nI0c7tGMXkUM1TgtdkP2cLI5QH4Nxu60PV6owlhZDiWYfDy2ZcoetmjbSqgeuJWPDArvA9yZ2ane8xmfjwmyzOO7iyMv-iipDi0skUD719o1NfAoY81Tij4hGYGqq44dPPM4kS8BipxfP5lcpE2CEWPdOPG-EQ2DJYkx8vHFgz3nxYtcrSsicL5wb8belsQ
## [2025-05-13 06:32:48] INFO     root: Updated token for domain 127.0.0.1: eyJhbGciOiJSUzI1NiIsInR5cCI6Ik...
## [2025-05-13 06:32:48] INFO     root: Successfully parsed JSON response
## [2025-05-13 06:32:48] INFO     root: ANPTool response [url: http://127.0.0.1:9870/openapi.json]
## [2025-05-13 06:32:48] INFO     root: Starting crawl iteration 4/20
## [2025-05-13 06:32:50] INFO     httpx: HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
## [2025-05-13 06:32:50] INFO     root: Model response: 
## [2025-05-13 06:32:50] INFO     root: Tool calls: [ChatCompletionMessageToolCall(id='call_e86a5587c4a9491dbf0a0f', function=Function(arguments='{"url": "http://127.0.0.1:9870/api/weather_info?cityName=苏州", "method": "GET"}', name='anp_tool'), type='function', index=0)]
## [2025-05-13 06:32:50] INFO     root: ANP request: GET http://127.0.0.1:9870/api/weather_info?cityName=苏州
## [2025-05-13 06:32:50] INFO     root: Using existing token for domain 127.0.0.1
## [2025-05-13 06:32:51] INFO     root: ANP response: status code 200
## [2025-05-13 06:32:51] INFO     root: Domain: 127.0.0.1 ; auth_header: None
## [2025-05-13 06:32:51] INFO     root: Successfully parsed JSON response
## [2025-05-13 06:32:51] INFO     root: ANPTool response [url: http://127.0.0.1:9870/api/weather_info?cityName=苏州]
## [2025-05-13 06:32:51] INFO     root: Starting crawl iteration 5/20
## [2025-05-13 06:32:54] INFO     httpx: HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
## [2025-05-13 06:32:54] INFO     root: Model response: 明天（2025年5月14日）苏州的天气预报如下：
- 白天天气：阴
- 晚上天气：阴
- 白天最高气温：31°C
- 晚上最低气温：22°C
- 风向：南风
- 风力：1-3级

请注意查看实时天气情况，并做好相应的准备。
[2025-05-13 06:32:54] INFO     root: Tool calls: None
[2025-05-13 06:32:54] INFO     root: The model did not request any tool calls, ending crawl
