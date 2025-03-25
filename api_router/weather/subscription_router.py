from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
import json
import uuid
from datetime import datetime, timedelta

# 创建路由
router = APIRouter()

# 模拟数据存储
subscriptions_db = {}

@router.post("/api/subscribe")
async def create_weather_subscription(request: Request):
    """
    创建天气信息订阅
    """
    # 返回白名单用户需要申请的信息
    return JSONResponse(
        status_code=200,
        content={
            "success": False,
            "msg": "天气信息订阅服务现阶段仅对白名单用户开放，请联系管理员申请白名单资格。",
            "data": {
                "contactEmail": "chgaowei@gmail.com",
            }
        }
    )
    
    """
    # 原有实现（已注释）
    try:
        # 解析请求体
        request_data = await request.json()
        
        # 记录请求
        logging.info(f"收到订阅请求: {request_data}")
        
        # 必填字段校验
        required_fields = ["customerOrderNo", "subscriptionType", "subscriberDID", "contactName", "contactMobile"]
        for field in required_fields:
            if field not in request_data:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "msg": f"缺少必填字段: {field}",
                        "data": None
                    }
                )
        
        # 生成订阅ID
        subscription_id = str(uuid.uuid4())
        
        # 根据订阅类型设置金额和过期时间
        amount = 10 if request_data["subscriptionType"] == "monthly" else 100
        expiry_date = datetime.now() + timedelta(days=30 if request_data["subscriptionType"] == "monthly" else 365)
        
        # 创建订阅记录
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
        
        # 保存订阅信息
        subscriptions_db[subscription_id] = subscription
        
        # 生成支付URL和签名
        payment_url = f"https://pay.agent-weather.xyz/pay?orderId={subscription_id}&amount={amount}"
        signature = f"sign_{subscription_id}_{int(datetime.now().timestamp())}"
        
        # 返回成功响应
        return JSONResponse(
            content={
                "success": True,
                "msg": "订阅创建成功",
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
                "msg": "无效的JSON格式",
                "data": None
            }
        )
    except Exception as e:
        logging.error(f"创建订阅时发生错误: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "msg": f"服务器内部错误: {str(e)}",
                "data": None
            }
        )
    """

@router.get("/api/subscription/status")
async def get_subscription_status(
    subscriptionId: str = Query(..., description="订阅ID"),
    subscriberDID: str = Query(..., description="订阅者DID")
):
    """
    查询天气信息订阅状态
    """
    # 返回白名单用户需要申请的信息
    return JSONResponse(
        status_code=200,
        content={
            "success": False,
            "msg": "天气信息订阅状态查询服务现阶段仅对白名单用户开放，请联系管理员申请白名单资格。",
            "data": {
                "contactEmail": "chgaowei@gmail.com",
                "subscriberDID": subscriberDID,
                "requestedSubscriptionId": subscriptionId
            }
        }
    )
    
    """
    # 原有实现（已注释）
    try:
        # 记录请求
        logging.info(f"收到订阅状态查询请求: subscriptionId={subscriptionId}, subscriberDID={subscriberDID}")
        
        # 检查订阅是否存在
        if subscriptionId not in subscriptions_db:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "msg": "订阅不存在",
                    "data": None
                }
            )
        
        # 获取订阅信息
        subscription = subscriptions_db[subscriptionId]
        
        # 验证DID
        if subscription["subscriberDID"] != subscriberDID:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "msg": "DID验证失败，无权访问此订阅",
                    "data": None
                }
            )
        
        # 计算剩余天数
        expiry_date = datetime.fromisoformat(subscription["expiryDate"])
        remaining_days = (expiry_date - datetime.now()).days
        
        # 构建响应
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
        
        # 返回成功响应
        return JSONResponse(
            content={
                "success": True,
                "msg": "查询成功",
                "data": response_data
            }
        )
        
    except Exception as e:
        logging.error(f"查询订阅状态时发生错误: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "msg": f"服务器内部错误: {str(e)}",
                "data": None
            }
        )
    """ 