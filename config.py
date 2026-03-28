"""
系统配置文件
"""
import os

class Config:
    # 基础配置
    SECRET_KEY = os.urandom(24)
    DEBUG = True
    
    # 路径配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # 数据文件路径
    DATA_FILES = {
        'campuses': os.path.join(DATA_DIR, 'campuses.json'),  # 校区
        'years': os.path.join(DATA_DIR, 'years.json'),  # 学年学期
        'classes': os.path.join(DATA_DIR, 'classes.json'),  # 班级
        'teachers': os.path.join(DATA_DIR, 'teachers.json'),  # 教师
        'students': os.path.join(DATA_DIR, 'students.json'),  # 学生
        'classrooms': os.path.join(DATA_DIR, 'classrooms.json'),  # 教室
        'courses': os.path.join(DATA_DIR, 'courses.json'),  # 课程
        'selections': os.path.join(DATA_DIR, 'selections.json'),  # 选课结果
        'schedules': os.path.join(DATA_DIR, 'schedules.json'),  # 课表
    }
    
    # 排课配置
    SCHEDULING_CONFIG = {
        'time_slots_per_day': 8,  # 每天课时数
        'days_per_week': 5,  # 每周天数
        'max_iterations': 1000,  # 最大迭代次数
        'population_size': 50,  # 种群大小（遗传算法）
        'mutation_rate': 0.1,  # 变异率
        'crossover_rate': 0.8,  # 交叉率
    }
    
    # 课时时间定义
    TIME_SLOTS = {
        1: '08:00-08:45',
        2: '08:55-09:40',
        3: '10:00-10:45',
        4: '10:55-11:40',
        5: '14:00-14:45',
        6: '14:55-15:40',
        7: '16:00-16:45',
        8: '16:55-17:40',
    }
    
    # 语数英分层教学配置
    LAYERED_SUBJECTS = ['语文', '数学', '英语']
    
    # 选科组合（7 选 3）
    SUBJECT_CHOICES = ['物理', '化学', '生物', '政治', '历史', '地理', '技术']
