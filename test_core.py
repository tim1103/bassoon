"""
选课排课系统 - 核心功能测试脚本
用于在不启动 Web 服务器的情况下测试核心算法
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_data_manager():
    """测试数据管理器"""
    print("=" * 50)
    print("测试 1: 数据管理器")
    print("=" * 50)
    
    from models.data_manager import DataManager
    
    # 创建临时数据文件配置
    test_files = {
        'teachers': 'data/test_teachers.json',
        'students': 'data/test_students.json',
        'classes': 'data/test_classes.json',
    }
    
    dm = DataManager(test_files)
    
    # 测试添加数据
    print("\n[测试] 添加教师数据...")
    result = dm.add('teachers', {
        'name': '张老师',
        'gender': '男',
        'subjects': ['数学', '物理']
    })
    print(f"添加结果：{result}")
    
    result = dm.add('teachers', {
        'name': '李老师',
        'gender': '女',
        'subjects': ['语文', '英语']
    })
    print(f"添加结果：{result}")
    
    # 测试获取数据
    print("\n[测试] 获取所有教师...")
    teachers = dm.get_all('teachers')
    print(f"教师数量：{len(teachers)}")
    for t in teachers:
        print(f"  - {t['name']} ({t['gender']}): {t['subjects']}")
    
    # 测试批量添加
    print("\n[测试] 批量添加学生...")
    students = [
        {'student_id': '2024001', 'name': '学生 A', 'gender': '男'},
        {'student_id': '2024002', 'name': '学生 B', 'gender': '女'},
        {'student_id': '2024003', 'name': '学生 C', 'gender': '男'},
    ]
    result = dm.batch_add('students', students)
    print(f"批量添加结果：{result}")
    
    print("\n✓ 数据管理器测试通过\n")
    return dm


def test_selection_service(dm):
    """测试选课服务"""
    print("=" * 50)
    print("测试 2: 选课服务")
    print("=" * 50)
    
    from services.selection_service import SelectionService
    
    ss = SelectionService(dm)
    
    # 创建选课方案
    print("\n[测试] 创建选课方案...")
    scheme = {
        'name': '2024 级高一选课方案',
        'grade': '高一',
        'description': '7 选 3 标准方案',
        'rules': {
            'mutual_exclusive': [['物理', '历史']],  # 物理和历史互斥
            'max_students': 50,
            'min_students': 20,
        }
    }
    result = ss.create_scheme(scheme)
    print(f"方案创建：{result['success']}")
    
    # 学生提交选课
    print("\n[测试] 学生提交选课...")
    selections = [
        {'student_id': 1, 'scheme_id': 1, 'subjects': ['物理', '化学', '生物']},
        {'student_id': 2, 'scheme_id': 1, 'subjects': ['物理', '化学', '地理']},
        {'student_id': 3, 'scheme_id': 1, 'subjects': ['历史', '政治', '地理']},
        {'student_id': 4, 'scheme_id': 1, 'subjects': ['物理', '化学', '技术']},
        {'student_id': 5, 'scheme_id': 1, 'subjects': ['生物', '政治', '历史']},
    ]
    
    for sel in selections:
        result = ss.submit_selection(sel)
        print(f"  学生{sel['student_id']}选课：{result['success']} - {sel['subjects']}")
    
    # 获取统计
    print("\n[测试] 选课统计...")
    stats = ss.get_statistics()
    print(f"总选课数：{stats['total']}")
    print(f"按科目统计：{stats['by_subject']}")
    print(f"按组合统计：{stats['by_combination']}")
    
    # 分班优化
    print("\n[测试] 分班优化...")
    config = {
        'max_students': 3,
        'min_students': 1,
        'gender_balance': True,
        'score_balance': True,
    }
    result = ss.optimize_classes(config)
    print(f"优化结果：{result['success']}")
    if result['success'] and result.get('data'):
        for group in result['data']:
            print(f"\n  选科组合：{group['subjects']}")
            print(f"  学生总数：{group['total_students']}")
            for cls in group['classes']:
                print(f"    教学{cls['class_id']}班：{cls['student_count']}人 "
                      f"(男{cls['male_count']}/女{cls['female_count']}, 均分{cls['avg_score']})")
    
    print("\n✓ 选课服务测试通过\n")
    return ss


def test_scheduling_service(dm):
    """测试排课服务"""
    print("=" * 50)
    print("测试 3: 排课服务")
    print("=" * 50)
    
    from services.scheduling_service import SchedulingService
    
    sched = SchedulingService(dm)
    
    # 准备测试数据
    print("\n[准备] 添加测试课程...")
    courses = [
        {'name': '语文', 'teacher_id': 2, 'periods_per_week': 5, 'continuous_periods': 1},
        {'name': '数学', 'teacher_id': 1, 'periods_per_week': 5, 'continuous_periods': 1},
        {'name': '英语', 'teacher_id': 2, 'periods_per_week': 4, 'continuous_periods': 1},
        {'name': '物理', 'teacher_id': 1, 'periods_per_week': 3, 'continuous_periods': 1},
        {'name': '化学', 'teacher_id': 1, 'periods_per_week': 2, 'continuous_periods': 1},
    ]
    
    for course in courses:
        dm.add('courses', course)
    print(f"添加了{len(courses)}门课程")
    
    # 添加班级
    print("\n[准备] 添加测试班级...")
    dm.add('classes', {'name': '高一 (1) 班', 'grade': '高一', 'type': '行政班'})
    dm.add('classes', {'name': '高一 (2) 班', 'grade': '高一', 'type': '行政班'})
    
    # 生成课表
    print("\n[测试] 生成课表...")
    config = {
        'scheme_name': '测试课表',
        'time_slots_per_day': 8,
        'days_per_week': 5,
        'max_iterations': 500,  # 减少迭代次数以加快测试
        'population_size': 20,
    }
    
    result = sched.generate_schedules(config)
    print(f"生成结果：{result['success']}")
    print(f"消息：{result.get('message', '')}")
    
    if result['success']:
        print(f"适应度分数：{result['data'].get('fitness', 'N/A')}")
        
        # 查看课表
        print("\n[测试] 查看班级课表...")
        timetable_result = sched.get_timetable('class', 1)
        timetable = timetable_result.get('timetable', {})
        
        if timetable:
            print("\n高一 (1) 班 课表预览:")
            print("-" * 60)
            for day, slots in list(timetable.items())[:3]:  # 只显示前 3 天
                print(f"\n{day}:")
                for slot, course in sorted(slots.items()):
                    print(f"  第{slot}节：{course.get('course', '未知')} "
                          f"({course.get('teacher', '未知')})")
    
    print("\n✓ 排课服务测试通过\n")
    return sched


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("       浙江省新高考选课排课系统 - 核心功能测试")
    print("=" * 60 + "\n")
    
    try:
        # 确保数据目录存在
        os.makedirs('data', exist_ok=True)
        
        # 运行测试
        dm = test_data_manager()
        ss = test_selection_service(dm)
        sched = test_scheduling_service(dm)
        
        print("\n" + "=" * 60)
        print("                    所有测试通过!")
        print("=" * 60)
        print("\n提示：现在可以运行 'python app.py' 启动 Web 服务器")
        print("访问地址：http://localhost:8080\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
