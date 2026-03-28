"""
测试改进功能
"""
import sys
sys.path.insert(0, '/workspace')

from app import app
from schemas import StudentSchema, SelectionSubmitSchema, GenerateScheduleConfigSchema
from marshmallow import ValidationError

def test_schemas():
    """测试数据校验 Schema"""
    print("=== 测试 Marshmallow Schema ===")
    
    # 测试学生 Schema
    student_schema = StudentSchema()
    
    # 有效数据
    valid_student = {
        'name': '张三',
        'gender': '男',
        'student_number': '2024001',
        'admin_class': '高一 (1) 班',
        'campus_id': 1,
        'avg_score': 85.5
    }
    try:
        result = student_schema.load(valid_student)
        print(f"✓ 学生数据验证通过：{result}")
    except ValidationError as e:
        print(f"✗ 学生数据验证失败：{e.messages}")
    
    # 无效数据 - 性别错误
    invalid_student = {
        'name': '李四',
        'gender': '未知性别',
        'student_number': '2024002',
        'admin_class': '高一 (2) 班',
        'campus_id': 1
    }
    try:
        result = student_schema.load(invalid_student)
        print(f"✗ 应该验证失败但通过了")
    except ValidationError as e:
        print(f"✓ 正确捕获验证错误：{e.messages}")
    
    # 测试选课提交 Schema
    selection_schema = SelectionSubmitSchema()
    
    # 有效选课
    valid_selection = {
        'student_id': 1,
        'scheme_id': 1,
        'subjects': ['物理', '化学', '生物']
    }
    try:
        result = selection_schema.load(valid_selection)
        print(f"✓ 选课数据验证通过：{result}")
    except ValidationError as e:
        print(f"✗ 选课数据验证失败：{e.messages}")
    
    # 无效选课 - 科目数量不对
    invalid_selection = {
        'student_id': 1,
        'scheme_id': 1,
        'subjects': ['物理', '化学']  # 只有 2 门
    }
    try:
        result = selection_schema.load(invalid_selection)
        print(f"✗ 应该验证失败但通过了")
    except ValidationError as e:
        print(f"✓ 正确捕获验证错误：{e.messages}")
    
    print()


def test_persistence():
    """测试持久化功能"""
    print("=== 测试服务层持久化 ===")
    
    from models.persistence import ServicePersistence
    from config import Config
    
    persistence = ServicePersistence(Config.DATA_DIR)
    
    # 测试保存和读取选课方案
    test_scheme = {
        'id': 999,
        'name': '测试方案',
        'year_id': 1,
        'subjects': ['物理', '化学', '生物', '政治', '历史', '地理', '技术'],
        'status': 'draft'
    }
    
    persistence.save_selection_scheme(test_scheme)
    schemes = persistence.get_all_selection_schemes()
    
    found = any(s['id'] == 999 for s in schemes)
    if found:
        print("✓ 选课方案持久化成功")
    else:
        print("✗ 选课方案持久化失败")
    
    # 测试保存和读取选课记录
    test_selection = {
        'id': 999,
        'student_id': 1,
        'scheme_id': 999,
        'subjects': ['物理', '化学', '生物'],
        'submitted_at': '2024-01-01T00:00:00'
    }
    
    persistence.save_selection(test_selection)
    selections = persistence.get_all_selections()
    
    found = any(s['id'] == 999 for s in selections)
    if found:
        print("✓ 选课记录持久化成功")
    else:
        print("✗ 选课记录持久化失败")
    
    # 测试保存和读取排课方案
    test_schedule = {
        'id': 999,
        'name': '测试排课方案',
        'schedule': {},
        'fitness': 100,
        'status': 'generated'
    }
    
    persistence.save_scheduling_scheme(test_schedule)
    schedules = persistence.get_all_scheduling_schemes()
    
    found = any(s['id'] == 999 for s in schedules)
    if found:
        print("✓ 排课方案持久化成功")
    else:
        print("✗ 排课方案持久化失败")
    
    print()


def test_error_handlers():
    """测试错误处理"""
    print("=== 测试错误处理 ===")
    
    with app.test_client() as client:
        # 测试 404 错误
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        if not data.get('success'):
            print("✓ 404 错误处理正确")
        else:
            print("✗ 404 错误处理失败")
        
        # 测试正常 API 调用
        response = client.get('/api/stats/overview')
        if response.status_code == 200:
            print("✓ API 正常响应")
        else:
            print("✗ API 响应异常")
    
    print()


if __name__ == '__main__':
    test_schemas()
    test_persistence()
    test_error_handlers()
    print("=== 所有测试完成 ===")
