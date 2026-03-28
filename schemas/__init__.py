"""
Marshmallow Schemas for Input Validation
数据校验模式定义
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


# ==================== 基础数据校验 ====================

class CampusSchema(Schema):
    """校区数据校验"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    address = fields.Str(validate=validate.Length(max=200))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TeacherSchema(Schema):
    """教师数据校验"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    gender = fields.Str(validate=validate.OneOf(['男', '女']))
    subject = fields.Str(validate=validate.Length(max=50))
    title = fields.Str(validate=validate.Length(max=50))
    campus_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class StudentSchema(Schema):
    """学生数据校验"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    gender = fields.Str(validate=validate.OneOf(['男', '女']))
    student_number = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    admin_class = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    campus_id = fields.Int(required=True)
    avg_score = fields.Float(validate=validate.Range(min=0, max=100))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ClassSchema(Schema):
    """班级数据校验"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    grade = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    campus_id = fields.Int(required=True)
    student_count = fields.Int(validate=validate.Range(min=0))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ClassroomSchema(Schema):
    """教室数据校验"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    building = fields.Str(validate=validate.Length(max=50))
    floor = fields.Int(validate=validate.Range(min=1, max=20))
    capacity = fields.Int(validate=validate.Range(min=1, max=200))
    type = fields.Str(validate=validate.OneOf(['普通教室', '实验室', '机房', '多媒体教室', '其他']))
    campus_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class CourseSchema(Schema):
    """课程数据校验"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    teacher_id = fields.Int(required=True)
    periods_per_week = fields.Int(required=True, validate=validate.Range(min=1, max=20))
    continuous_periods = fields.Int(validate=validate.Range(min=1, max=4))
    preferred_time = fields.List(fields.Int())
    forbidden_time = fields.List(fields.Int())
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# ==================== 选课相关校验 ====================

class SelectionSchemeSchema(Schema):
    """选课方案校验"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    year_id = fields.Int(required=True)
    subjects = fields.List(fields.Str(), required=True)
    rules = fields.Dict()
    status = fields.Str(validate=validate.OneOf(['draft', 'active', 'completed']))
    created_at = fields.DateTime(dump_only=True)
    
    @validates('subjects')
    def validate_subjects(self, value):
        if len(value) != 7:
            raise ValidationError('必须包含 7 门科目')
        allowed_subjects = ['物理', '化学', '生物', '政治', '历史', '地理', '技术']
        for subject in value:
            if subject not in allowed_subjects:
                raise ValidationError(f'无效的科目：{subject}')


class SelectionSubmitSchema(Schema):
    """学生提交选课校验"""
    student_id = fields.Int(required=True)
    scheme_id = fields.Int(required=True)
    subjects = fields.List(fields.Str(), required=True)
    preferences = fields.List(fields.Int())
    
    @validates('subjects')
    def validate_subjects(self, value):
        if len(value) != 3:
            raise ValidationError('必须选择 3 门科目')


class OptimizeClassConfigSchema(Schema):
    """分班优化配置校验"""
    max_students = fields.Int(validate=validate.Range(min=10, max=100))
    min_students = fields.Int(validate=validate.Range(min=5, max=50))
    gender_balance = fields.Bool()
    score_balance = fields.Bool()
    admin_class_concentrated = fields.Bool()


# ==================== 排课相关校验 ====================

class GenerateScheduleConfigSchema(Schema):
    """生成课表配置校验"""
    scheme_name = fields.Str(validate=validate.Length(min=1, max=100))
    time_slots_per_day = fields.Int(validate=validate.Range(min=4, max=12))
    days_per_week = fields.Int(validate=validate.Range(min=5, max=6))
    max_iterations = fields.Int(validate=validate.Range(min=100, max=10000))
    population_size = fields.Int(validate=validate.Range(min=10, max=200))
    mutation_rate = fields.Float(validate=validate.Range(min=0.01, max=0.5))
    crossover_rate = fields.Float(validate=validate.Range(min=0.5, max=0.95))


# ==================== 通用响应 Schema ====================

class SuccessResponseSchema(Schema):
    """成功响应"""
    success = fields.Bool(dump_default=True)
    message = fields.Str()
    data = fields.Dict()


class ErrorResponseSchema(Schema):
    """错误响应"""
    success = fields.Bool(dump_default=False)
    message = fields.Str(required=True)
    errors = fields.Dict()
