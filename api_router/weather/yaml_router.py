from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
import os
from pathlib import Path
import logging

router = APIRouter(prefix="/agents")

@router.get("/travel/weather/api_files/{yaml_file}")
async def get_yaml_file(yaml_file: str):
    """
    获取天气智能体的YAML文件
    
    Args:
        yaml_file: YAML文件名
        
    Returns:
        YAML文件内容
    """
    try:
        # 获取当前文件所在目录
        current_dir = Path(__file__).parent
        # 构建YAML文件路径
        yaml_file_path = current_dir / "api" / yaml_file
        
        logging.info(f"请求YAML文件: {yaml_file_path}")
        
        # 检查文件是否存在
        if not yaml_file_path.exists():
            logging.error(f"YAML文件不存在: {yaml_file_path}")
            raise HTTPException(status_code=404, detail=f"YAML文件 {yaml_file} 不存在")
        
        # 读取YAML文件内容
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()
        
        logging.info(f"成功读取YAML文件: {yaml_file}")
        return PlainTextResponse(content=yaml_content, media_type="application/x-yaml")
    
    except Exception as e:
        logging.error(f"获取YAML文件时出错: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取YAML文件时出错: {str(e)}")
