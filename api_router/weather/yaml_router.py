from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pathlib import Path
import logging

# Modified route prefix, removed agents/travel/weather
router = APIRouter()

@router.get("/api_files/{yaml_file}")
async def get_yaml_file(yaml_file: str):
    """
    Get weather agent YAML files
    
    Args:
        yaml_file: YAML filename
        
    Returns:
        YAML file content
    """
    try:
        # Get current file directory
        current_dir = Path(__file__).parent
        # Build YAML file path
        yaml_file_path = current_dir / "api" / yaml_file
        
        logging.info(f"Requested YAML file: {yaml_file_path}")
        
        # Check if file exists
        if not yaml_file_path.exists():
            logging.error(f"YAML file does not exist: {yaml_file_path}")
            raise HTTPException(status_code=404, detail=f"YAML file {yaml_file} does not exist")
        
        # Read YAML file content
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()
        
        logging.info(f"Successfully read YAML file: {yaml_file}")
        return PlainTextResponse(content=yaml_content, media_type="application/x-yaml")
    
    except Exception as e:
        logging.error(f"Error getting YAML file: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error getting YAML file: {str(e)}")
