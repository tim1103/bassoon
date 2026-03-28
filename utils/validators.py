"""
输入验证装饰器
使用 Marshmallow 进行数据校验
"""
from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError


def validate_request(schema_class):
    """
    装饰器：验证请求数据
    
    用法:
        @app.route('/api/users', methods=['POST'])
        @validate_request(UserSchema)
        def create_user():
            # 验证后的数据在 request.validated_data 中
            data = request.validated_data
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            schema = schema_class()
            
            try:
                # 获取请求数据
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict() if request.form else {}
                
                # 验证数据
                validated_data = schema.load(data)
                request.validated_data = validated_data
                
            except ValidationError as err:
                return jsonify({
                    'success': False,
                    'message': '数据验证失败',
                    'errors': err.messages
                }), 400
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'请求解析失败：{str(e)}'
                }), 400
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


def validate_query_params(schema_class):
    """
    装饰器：验证查询参数
    
    用法:
        @app.route('/api/users')
        @validate_query_params(UserQuerySchema)
        def get_users():
            # 验证后的参数在 request.validated_args 中
            args = request.validated_args
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            schema = schema_class()
            
            try:
                # 获取查询参数
                args_data = request.args.to_dict()
                
                # 验证参数
                validated_args = schema.load(args_data)
                request.validated_args = validated_args
                
            except ValidationError as err:
                return jsonify({
                    'success': False,
                    'message': '查询参数验证失败',
                    'errors': err.messages
                }), 400
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'参数解析失败：{str(e)}'
                }), 400
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


def validate_path_params(schema_class):
    """
    装饰器：验证路径参数
    
    用法:
        @app.route('/api/users/<int:user_id>')
        @validate_path_params(UserIdSchema)
        def get_user(user_id):
            # 验证后的参数在 request.validated_view_args 中
            view_args = request.validated_view_args
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            schema = schema_class()
            
            try:
                # 获取路径参数
                view_args = request.view_args or {}
                
                # 验证参数
                validated_view_args = schema.load(view_args)
                request.validated_view_args = validated_view_args
                
            except ValidationError as err:
                return jsonify({
                    'success': False,
                    'message': '路径参数验证失败',
                    'errors': err.messages
                }), 400
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'参数解析失败：{str(e)}'
                }), 400
            
            return f(*args, **kwargs)
        return wrapped
    return decorator
