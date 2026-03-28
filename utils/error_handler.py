"""
全局错误处理和结构化日志模块
"""
import logging
import json
from datetime import datetime
from functools import wraps
from flask import request, jsonify


# 配置结构化日志
def setup_logging(app):
    """配置应用日志"""
    
    # 创建日志目录
    import os
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 日志格式 - JSON 结构化
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
            }
            
            # 添加额外字段
            if hasattr(record, 'user_id'):
                log_data['user_id'] = record.user_id
            if hasattr(record, 'request_id'):
                log_data['request_id'] = record.request_id
            
            # 添加异常信息
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            return json.dumps(log_data, ensure_ascii=False)
    
    # 文件处理器 - JSON 格式
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    
    # 控制台处理器 - 人类可读格式
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    
    # 配置根日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('app')
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_request_response(func):
    """装饰器：记录请求和响应"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('app')
        
        # 记录请求信息
        logger.info(f"Request: {request.method} {request.path}", extra={
            'request_id': getattr(request, 'request_id', None),
            'method': request.method,
            'path': request.path,
            'args': dict(request.args),
            'remote_addr': request.remote_addr,
        })
        
        # 如果是 POST/PUT，记录请求体（限制大小）
        if request.method in ['POST', 'PUT'] and request.is_json:
            try:
                body = request.get_json(silent=True)
                if body:
                    body_str = json.dumps(body)[:500]  # 限制长度
                    logger.debug(f"Request body: {body_str}")
            except Exception:
                pass
        
        try:
            response = func(*args, **kwargs)
            
            # 记录响应状态
            status_code = response[1] if isinstance(response, tuple) else 200
            logger.info(f"Response: {status_code}")
            
            return response
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    
    return wrapper


class APIError(Exception):
    """API 错误基类"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['success'] = False
        rv['message'] = self.message
        return rv


class ValidationError(APIError):
    """数据验证错误"""
    def __init__(self, message, errors=None):
        super().__init__(message, status_code=400)
        self.errors = errors
    
    def to_dict(self):
        rv = super().to_dict()
        if self.errors:
            rv['errors'] = self.errors
        return rv


class NotFoundError(APIError):
    """资源未找到错误"""
    def __init__(self, message="资源不存在"):
        super().__init__(message, status_code=404)


class UnauthorizedError(APIError):
    """未授权错误"""
    def __init__(self, message="未授权访问"):
        super().__init__(message, status_code=401)


class ServerError(APIError):
    """服务器内部错误"""
    def __init__(self, message="服务器内部错误"):
        super().__init__(message, status_code=500)


def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        logger = logging.getLogger('app')
        logger.warning(f"Validation error: {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = 400
        return response
    
    @app.errorhandler(NotFoundError)
    def handle_not_found(error):
        response = jsonify({'success': False, 'message': error.message})
        response.status_code = 404
        return response
    
    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized(error):
        response = jsonify({'success': False, 'message': error.message})
        response.status_code = 401
        return response
    
    @app.errorhandler(ServerError)
    def handle_server_error(error):
        logger = logging.getLogger('app')
        logger.error(f"Server error: {error.message}", exc_info=True)
        response = jsonify({'success': False, 'message': error.message})
        response.status_code = 500
        return response
    
    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({'success': False, 'message': '接口不存在'}), 404
    
    @app.errorhandler(500)
    def handle_500(error):
        logger = logging.getLogger('app')
        logger.error(f"Internal server error: {str(error)}", exc_info=True)
        return jsonify({'success': False, 'message': '服务器内部错误'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger = logging.getLogger('app')
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return jsonify({'success': False, 'message': '服务器内部错误'}), 500
