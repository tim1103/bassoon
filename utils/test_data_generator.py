"""
测试数据生成器
用于生成随机的学生和班级数据
"""
import random
from datetime import datetime
from typing import List, Dict, Any


class TestDataGenerator:
    """测试数据生成器"""
    
    # 常见中文姓氏
    SURNAMES = [
        '赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈',
        '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许',
        '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏',
        '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦', '章',
        '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦'
    ]
    
    # 常见名字
    GIVEN_NAMES_MALE = [
        '伟', '刚', '勇', '毅', '俊', '峰', '强', '军', '平', '保',
        '东', '文', '辉', '力', '明', '永', '健', '世', '广', '志',
        '义', '兴', '良', '海', '山', '仁', '波', '宁', '贵', '福',
        '生', '龙', '元', '全', '国', '胜', '学', '祥', '才', '发',
        '武', '新', '利', '清', '飞', '彬', '富', '顺', '信', '子',
        '杰', '涛', '昌', '成', '康', '星', '光', '天', '达', '安',
        '岩', '中', '茂', '进', '林', '有', '坚', '和', '彪', '博',
        '诚', '先', '敬', '震', '振', '壮', '会', '思', '群', '豪',
        '心', '邦', '承', '乐', '绍', '功', '松', '善', '厚', '庆'
    ]
    
    GIVEN_NAMES_FEMALE = [
        '秀', '娟', '英', '华', '慧', '巧', '美', '娜', '静', '淑',
        '惠', '珠', '翠', '雅', '芝', '玉', '萍', '红', '娥', '玲',
        '芬', '芳', '燕', '彩', '春', '菊', '兰', '凤', '洁', '梅',
        '琳', '素', '云', '莲', '真', '环', '雪', '荣', '爱', '妹',
        '霞', '香', '月', '莺', '媛', '艳', '瑞', '凡', '佳', '嘉',
        '琼', '勤', '珍', '贞', '莉', '桂', '娣', '叶', '璧', '璐',
        '娅', '琦', '晶', '妍', '茜', '秋', '珊', '莎', '锦', '黛',
        '青', '倩', '婷', '姣', '婉', '娴', '瑾', '颖', '露', '瑶',
        '怡', '婵', '雁', '蓓', '纨', '仪', '荷', '丹', '蓉', '眉',
        '君', '琴', '蕊', '薇', '菁', '梦', '岚', '苑', '婕', '馨'
    ]
    
    def __init__(self):
        self.random = random.Random()
    
    def generate_name(self, gender: str) -> str:
        """生成随机姓名"""
        surname = self.random.choice(self.SURNAMES)
        if gender == '男':
            given_name = self.random.choice(self.GIVEN_NAMES_MALE)
        else:
            given_name = self.random.choice(self.GIVEN_NAMES_FEMALE)
        
        # 70% 概率生成双字名
        if self.random.random() < 0.7:
            if gender == '男':
                given_name += self.random.choice(self.GIVEN_NAMES_MALE)
            else:
                given_name += self.random.choice(self.GIVEN_NAMES_FEMALE)
        
        return surname + given_name
    
    def generate_student_id(self, grade: int, class_num: int, seq: int) -> str:
        """生成学号：年级 (4 位) + 班级 (2 位) + 序号 (3 位)"""
        return f"{grade}{class_num:02d}{seq:03d}"
    
    def generate_phone(self) -> str:
        """生成随机手机号"""
        prefix = self.random.choice(['138', '139', '150', '151', '152', '158', '159', '188', '187', '186'])
        suffix = ''.join([str(self.random.randint(0, 9)) for _ in range(8)])
        return f"{prefix}{suffix}"
    
    def generate_students_and_classes(
        self, 
        total_students: int = 3000, 
        total_classes: int = 60,
        start_grade: int = 2023
    ) -> Dict[str, List[Dict]]:
        """
        生成学生和班级数据
        
        Args:
            total_students: 学生总数
            total_classes: 班级总数
            start_grade: 起始年级
            
        Returns:
            包含 students 和 classes 的字典
        """
        # 计算每个班级的学生数（尽量平均分配）
        base_count = total_students // total_classes
        remainder = total_students % total_classes
        
        classes = []
        students = []
        student_seq = 1
        
        # 生成班级
        for i in range(total_classes):
            class_num = i + 1
            grade = start_grade + (i // 20)  # 每 20 个班一个年级
            class_in_grade = (i % 20) + 1
            
            # 班级名称
            class_name = f"{grade}级{class_in_grade}班"
            
            # 该班学生数
            class_size = base_count + (1 if i < remainder else 0)
            
            class_data = {
                'name': class_name,
                'grade': str(grade),
                'type': '行政班',
                'head_teacher': f'老师{class_num}',
                'student_count': class_size,
                'remark': f'自动生成的测试班级{class_num}'
            }
            classes.append(class_data)
            
            # 生成该班学生
            for j in range(class_size):
                gender = '男' if self.random.random() < 0.5 else '女'
                name = self.generate_name(gender)
                student_id = self.generate_student_id(grade, class_in_grade, student_seq)
                
                student_data = {
                    'student_id': student_id,
                    'name': name,
                    'gender': gender,
                    'admin_class': class_name,
                    'phone': self.generate_phone(),
                    'remark': f'测试学生{student_seq}'
                }
                students.append(student_data)
                student_seq += 1
        
        return {
            'classes': classes,
            'students': students
        }
    
    def generate_with_existing_data(
        self, 
        existing_classes: List[Dict], 
        existing_students: List[Dict],
        target_students: int = 3000,
        target_classes: int = 60
    ) -> Dict[str, List[Dict]]:
        """
        基于现有数据生成补充数据
        
        Args:
            existing_classes: 现有班级列表
            existing_students: 现有学生列表
            target_students: 目标学生总数
            target_classes: 目标班级总数
            
        Returns:
            需要新增的 students 和 classes 数据
        """
        current_class_count = len(existing_classes)
        current_student_count = len(existing_students)
        
        # 计算需要新增的数量
        new_classes_needed = max(0, target_classes - current_class_count)
        new_students_needed = max(0, target_students - current_student_count)
        
        if new_classes_needed == 0 and new_students_needed == 0:
            return {'classes': [], 'students': []}
        
        # 如果需要新班级，生成完整的班级和学生
        if new_classes_needed > 0:
            result = self.generate_students_and_classes(
                total_students=new_students_needed,
                total_classes=new_classes_needed,
                start_grade=2024  # 新班级从 2024 级开始
            )
            return result
        else:
            # 只需要添加学生到现有班级
            students_to_add = []
            for i in range(new_students_needed):
                # 随机分配到一个现有班级
                target_class = self.random.choice(existing_classes)
                class_name = target_class['name']
                
                # 从班级名解析年级和班级号
                try:
                    grade = int(class_name.replace('级', '').split('级')[0])
                    class_num = int(class_name.split('级')[1].replace('班', ''))
                except:
                    grade = 2024
                    class_num = 1
                
                gender = '男' if self.random.random() < 0.5 else '女'
                name = self.generate_name(gender)
                student_seq = current_student_count + i + 1
                student_id = self.generate_student_id(grade, class_num, student_seq)
                
                student_data = {
                    'student_id': student_id,
                    'name': name,
                    'gender': gender,
                    'admin_class': class_name,
                    'phone': self.generate_phone(),
                    'remark': f'测试学生{student_seq}'
                }
                students_to_add.append(student_data)
            
            return {'classes': [], 'students': students_to_add}
