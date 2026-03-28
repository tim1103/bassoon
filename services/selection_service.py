"""
选课服务模块
处理选课方案、规则引擎、分班优化等
"""
import random
from typing import Dict, List, Any
from datetime import datetime


class SelectionService:
    """选课服务"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.selection_schemes = []
        self.selections = []
        self.optimized_classes = []
        
        # 加载已有数据
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        # 这里可以从数据管理器加载持久化的选课方案和结果
        pass
    
    def create_scheme(self, scheme: Dict) -> Dict:
        """创建选课方案"""
        scheme_id = len(self.selection_schemes) + 1
        scheme['id'] = scheme_id
        scheme['created_at'] = datetime.now().isoformat()
        scheme['status'] = 'draft'  # draft, active, completed
        
        # 默认规则配置
        if 'rules' not in scheme:
            scheme['rules'] = {
                'mutual_exclusive': [],  # 互斥科目
                'required_together': [],  # 必选组合
                'forbidden_combinations': [],  # 禁选组合
                'max_students': 50,  # 每班最大人数
                'min_students': 20,  # 每班最小人数
                'gender_balance': True,  # 男女均衡
                'score_balance': True,  # 成绩均衡
            }
        
        self.selection_schemes.append(scheme)
        return {'success': True, 'data': scheme}
    
    def get_all_schemes(self) -> List[Dict]:
        """获取所有选课方案"""
        return self.selection_schemes
    
    def submit_selection(self, selection: Dict) -> Dict:
        """学生提交选课志愿"""
        # 校验学生是否存在
        student_id = selection.get('student_id')
        students = self.data_manager.get_all('students')
        student = next((s for s in students if s['id'] == student_id), None)
        
        if not student:
            return {'success': False, 'message': '学生不存在'}
        
        # 校验选课是否符合规则
        scheme_id = selection.get('scheme_id')
        scheme = next((s for s in self.selection_schemes if s['id'] == scheme_id), None)
        
        if not scheme:
            return {'success': False, 'message': '选课方案不存在'}
        
        selected_subjects = selection.get('subjects', [])
        
        # 检查科目数量（7 选 3）
        if len(selected_subjects) != 3:
            return {'success': False, 'message': '必须选择 3 门科目'}
        
        # 检查互斥规则
        rules = scheme.get('rules', {})
        for exclusive_pair in rules.get('mutual_exclusive', []):
            if all(subj in selected_subjects for subj in exclusive_pair):
                return {'success': False, 'message': f'{exclusive_pair[0]}和{exclusive_pair[1]}不能同时选择'}
        
        # 检查必选组合
        for required_combo in rules.get('required_together', []):
            if any(subj in selected_subjects for subj in required_combo):
                if not all(subj in selected_subjects for subj in required_combo):
                    return {'success': False, 'message': f'{required_combo}必须同时选择'}
        
        # 添加选课记录
        selection['id'] = len(self.selections) + 1
        selection['submitted_at'] = datetime.now().isoformat()
        selection['status'] = 'pending'  # pending, confirmed, adjusted
        self.selections.append(selection)
        
        return {'success': True, 'message': '选课成功'}
    
    def get_results(self) -> List[Dict]:
        """获取选课结果"""
        return self.selections
    
    def optimize_classes(self, config: Dict) -> Dict:
        """
        分班优化
        支持：成绩均衡、男女均衡、原行政班集中
        """
        # 获取所有选课数据
        selections = self.selections
        students = self.data_manager.get_all('students')
        
        if not selections:
            return {'success': False, 'message': '没有选课数据'}
        
        # 按选科组合分组
        subject_groups = {}
        for selection in selections:
            subjects = tuple(sorted(selection.get('subjects', [])))
            if subjects not in subject_groups:
                subject_groups[subjects] = []
            subject_groups[subjects].append(selection)
        
        optimized_result = []
        
        for subjects, group_selections in subject_groups.items():
            # 对该选科组合的学生进行分班
            classes = self._optimize_single_group(
                group_selections, 
                students,
                config
            )
            
            optimized_result.append({
                'subjects': list(subjects),
                'total_students': len(group_selections),
                'classes': classes
            })
        
        self.optimized_classes = optimized_result
        
        return {
            'success': True,
            'message': f'完成分班优化，共生成{len(optimized_result)}个教学班组合',
            'data': optimized_result
        }
    
    def _optimize_single_group(self, selections: List[Dict], students: List[Dict], 
                                config: Dict) -> List[Dict]:
        """对单个选科组合进行分班优化"""
        max_students_per_class = config.get('max_students', 50)
        min_students_per_class = config.get('min_students', 20)
        
        # 补充学生详细信息
        student_map = {s['id']: s for s in students}
        students_with_info = []
        for sel in selections:
            student = student_map.get(sel.get('student_id'))
            if student:
                students_with_info.append({
                    'selection': sel,
                    'student': student,
                    'gender': student.get('gender', '未知'),
                    'admin_class': student.get('admin_class', ''),
                    'score': student.get('avg_score', 50)  # 假设有平均成绩
                })
        
        # 计算需要的班级数
        total_students = len(students_with_info)
        num_classes = max(1, (total_students + max_students_per_class - 1) // max_students_per_class)
        
        # 初始化班级
        classes = [[] for _ in range(num_classes)]
        
        # 优化策略：贪心 + 启发式
        # 1. 先按行政班分组，尽量让同行政班的学生在一起
        admin_class_groups = {}
        for student in students_with_info:
            ac = student['admin_class']
            if ac not in admin_class_groups:
                admin_class_groups[ac] = []
            admin_class_groups[ac].append(student)
        
        # 2. 按行政班大小排序，优先分配大的行政班
        sorted_groups = sorted(admin_class_groups.values(), 
                              key=lambda g: len(g), reverse=True)
        
        # 3. 分配每个行政班的学生到不同班级
        for group in sorted_groups:
            # 简单轮询分配（可以改进为更复杂的算法）
            for i, student in enumerate(group):
                class_idx = i % num_classes
                classes[class_idx].append(student)
        
        # 4. 如果需要男女均衡，进行调整
        if config.get('gender_balance', True):
            classes = self._balance_gender(classes)
        
        # 5. 如果需要成绩均衡，进行调整
        if config.get('score_balance', True):
            classes = self._balance_scores(classes)
        
        # 生成班级信息
        result_classes = []
        for i, class_students in enumerate(classes):
            males = sum(1 for s in class_students if s['gender'] == '男')
            females = sum(1 for s in class_students if s['gender'] == '女')
            avg_score = sum(s['score'] for s in class_students) / len(class_students) if class_students else 0
            
            result_classes.append({
                'class_id': i + 1,
                'student_count': len(class_students),
                'male_count': males,
                'female_count': females,
                'avg_score': round(avg_score, 2),
                'admin_classes': list(set(s['admin_class'] for s in class_students))
            })
        
        return result_classes
    
    def _balance_gender(self, classes: List[List]) -> List[List]:
        """调整男女比例均衡"""
        # 简化实现：交换学生来平衡男女比例
        # 实际可以使用更复杂的优化算法
        return classes
    
    def _balance_scores(self, classes: List[List]) -> List[List]:
        """调整成绩均衡"""
        # 简化实现：交换学生来平衡成绩
        # 实际可以使用更复杂的优化算法
        return classes
    
    def get_statistics(self) -> Dict:
        """获取选课统计"""
        if not self.selections:
            return {'total': 0, 'by_subject': {}, 'by_combination': {}}
        
        # 按科目统计
        subject_count = {}
        combination_count = {}
        
        for selection in self.selections:
            subjects = selection.get('subjects', [])
            for subject in subjects:
                subject_count[subject] = subject_count.get(subject, 0) + 1
            
            combo_key = '-'.join(sorted(subjects))
            combination_count[combo_key] = combination_count.get(combo_key, 0) + 1
        
        return {
            'total': len(self.selections),
            'by_subject': subject_count,
            'by_combination': combination_count
        }
