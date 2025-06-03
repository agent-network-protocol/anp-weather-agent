from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse


# Create router
router = APIRouter()

# Mock data storage
subscriptions_db = {}


@router.post("/api/subscribe")
async def create_weather_subscription(request: Request):
    """
    Create weather information subscription
    """
    # Return information for whitelist application
    return JSONResponse(
        status_code=200,
        content={
            "success": False,
            "msg": "Weather information subscription service is currently only available to whitelisted users. Please contact the administrator to apply for whitelist qualification.",
            "data": {
                "contactEmail": "chgaowei@gmail.com",
            },
        },
    )

    """
    # Original implementation (commented out)
    try:
        # Parse request body
        request_data = await request.json()
        
        # Log request
        logging.info(f"Received subscription request: {request_data}")
        
        # Required fields validation
        required_fields = ["customerOrderNo", "subscriptionType", "subscriberDID", "contactName", "contactMobile"]
        for field in required_fields:
            if field not in request_data:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "msg": f"Missing required field: {field}",
                        "data": None
                    }
                )
        
        # Generate subscription ID
        subscription_id = str(uuid.uuid4())
        
        # Set amount and expiry date based on subscription type
        amount = 10 if request_data["subscriptionType"] == "monthly" else 100
        expiry_date = datetime.now() + timedelta(days=30 if request_data["subscriptionType"] == "monthly" else 365)
        
        # Create subscription record
        subscription = {
            "subscriptionId": subscription_id,
            "customerOrderNo": request_data["customerOrderNo"],
            "subscriberDID": request_data["subscriberDID"],
            "type": request_data["subscriptionType"],
            "status": "pending",
            "paymentStatus": "pending",
            "amount": amount,
            "createTime": datetime.now().isoformat(),
            "startDate": datetime.now().isoformat(),
            "expiryDate": expiry_date.isoformat(),
            "contactName": request_data["contactName"],
            "contactMobile": request_data["contactMobile"],
            "contactEmail": request_data.get("contactEmail", ""),
            "regions": request_data.get("regions", []),
            "customFeatures": request_data.get("customFeatures", [])
        }
        
        # Save subscription information
        subscriptions_db[subscription_id] = subscription
        
        # Generate payment URL and signature
        payment_url = f"https://pay.agent-weather.xyz/pay?orderId={subscription_id}&amount={amount}"
        signature = f"sign_{subscription_id}_{int(datetime.now().timestamp())}"
        
        # Return success response
        return JSONResponse(
            content={
                "success": True,
                "msg": "Subscription created successfully",
                "data": {
                    "orderNo": subscription["customerOrderNo"],
                    "subscriptionId": subscription_id,
                    "amount": amount,
                    "paymentUrl": payment_url,
                    "signature": signature,
                    "expiryDate": subscription["expiryDate"]
                }
            }
        )
        
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "msg": "Invalid JSON format",
                "data": None
            }
        )
    except Exception as e:
        logging.error(f"Error creating subscription: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "msg": f"Internal server error: {str(e)}",
                "data": None
            }
        )
    """


@router.get("/api/subscription/status")
async def get_subscription_status(
    subscriptionId: str = Query(..., description="Subscription ID"),
    subscriberDID: str = Query(..., description="Subscriber DID"),
):
    """
    Query weather information subscription status
    """
    # Return information for whitelist application
    return JSONResponse(
        status_code=200,
        content={
            "success": False,
            "msg": "Weather information subscription status query service is currently only available to whitelisted users. Please contact the administrator to apply for whitelist qualification.",
            "data": {
                "contactEmail": "chgaowei@gmail.com",
                "subscriberDID": subscriberDID,
                "requestedSubscriptionId": subscriptionId,
            },
        },
    )

    """
    # Original implementation (commented out)
    try:
        # Log request
        logging.info(f"Received subscription status query request: subscriptionId={subscriptionId}, subscriberDID={subscriberDID}")
        
        # Check if subscription exists
        if subscriptionId not in subscriptions_db:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "msg": "Subscription does not exist",
                    "data": None
                }
            )
        
        # Get subscription information
        subscription = subscriptions_db[subscriptionId]
        
        # Verify DID
        if subscription["subscriberDID"] != subscriberDID:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "msg": "DID verification failed, no permission to access this subscription",
                    "data": None
                }
            )
        
        # Calculate remaining days
        expiry_date = datetime.fromisoformat(subscription["expiryDate"])
        remaining_days = (expiry_date - datetime.now()).days
        
        # Build response
        response_data = {
            "subscriptionId": subscription["subscriptionId"],
            "status": subscription["status"],
            "type": subscription["type"],
            "startDate": subscription["startDate"],
            "expiryDate": subscription["expiryDate"],
            "remainingDays": max(0, remaining_days),
            "paymentStatus": subscription["paymentStatus"],
            "regions": subscription.get("regions", []),
            "features": subscription.get("customFeatures", [])
        }
        
        # Return success response
        return JSONResponse(
            content={
                "success": True,
                "msg": "Query successful",
                "data": response_data
            }
        )
        
    except Exception as e:
        logging.error(f"Error querying subscription status: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "msg": f"Internal server error: {str(e)}",
                "data": None
            }
        )
    """
