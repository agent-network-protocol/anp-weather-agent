import logging
import logging.handlers
import os
import sys
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',  # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m',  # Magenta
        'RESET': '\033[0m',  # Reset
    }

    def format(self, record):
        levelname = record.levelname
        message = super().format(record)
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        return color + message + self.COLORS['RESET']

def setup_logging(level=logging.INFO):
    # 获取项目名称
    project_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('-', '_')
    
    # 创建日志目录
    if sys.platform == 'darwin':  # Mac系统
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    else:
        log_dir = f"/var/log/{project_name}"
    try:
        # 如果目录不存在，创建目录并设置权限
        if not os.path.exists(log_dir):
            os.system('sudo mkdir -p ' + log_dir)
            os.system(f'sudo chown -R {os.getenv("USER")}:{os.getenv("USER")} ' + log_dir)
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        print(f"Error setting up log directory: {e}")
        # 如果失败，使用备用的日志目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
    
    # 生成日志文件名（包含日期）
    log_file = os.path.join(log_dir, f"{project_name}_{datetime.now().strftime('%Y%m%d')}.log")
    
    print("Log file: ", log_file)

    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 配置带颜色的控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    colored_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s\n')
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
    
    # 配置文件处理器，使用相同的格式（但不带颜色）
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)
    
    # 防止日志消息向上传播到根日志器
    logger.propagate = False
    
    return logger

# 为了向后兼容，保留set_log_color_level函数，但让它调用setup_logging
def set_log_color_level(level):
    return setup_logging(level)