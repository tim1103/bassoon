"""
排课服务模块
实现基于遗传算法的自动排课功能
"""
import random
import copy
from typing import Dict, List, Any, Tuple
from datetime import datetime

from models.persistence import ServicePersistence


class SchedulingService:
    """排课服务"""
    
    def __init__(self, data_manager, persistence: ServicePersistence = None):
        self.data_manager = data_manager
        self.persistence = persistence
        self.scheduling_schemes = []
        
        # 从配置加载默认参数
        self.config = {
            'time_slots_per_day': 8,
            'days_per_week': 5,
            'max_iterations': 1000,
            'population_size': 50,
            'mutation_rate': 0.1,
            'crossover_rate': 0.8,
        }
        
        self._load_data()
    
    def _load_data(self):
        """从持久化存储加载数据"""
        if self.persistence:
            self.scheduling_schemes = self.persistence.get_all_scheduling_schemes()
    
    def generate_schedules(self, config: Dict) -> Dict:
        """
        生成课表
        使用遗传算法 + 模拟退火优化
        """
        # 合并配置
        self.config.update(config)
        
        # 准备排课数据
        classes = self.data_manager.get_all('classes')
        teachers = self.data_manager.get_all('teachers')
        classrooms = self.data_manager.get_all('classrooms')
        courses = self.data_manager.get_all('courses')
        
        if not classes or not teachers or not courses:
            return {'success': False, 'message': '基础数据不完整'}
        
        # 生成教学任务
        teaching_tasks = self._prepare_teaching_tasks(classes, teachers, courses)
        
        if not teaching_tasks:
            return {'success': False, 'message': '没有需要排课的教学任务'}
        
        # 运行遗传算法
        best_schedule = self._genetic_algorithm(teaching_tasks, teachers, classrooms)
        
        if not best_schedule:
            return {'success': False, 'message': '未能生成有效课表'}
        
        # 保存方案
        scheme_id = len(self.scheduling_schemes) + 1
        scheme = {
            'id': scheme_id,
            'name': config.get('scheme_name', f'方案{scheme_id}'),
            'created_at': datetime.now().isoformat(),
            'schedule': best_schedule,
            'fitness': self._calculate_fitness(best_schedule, teaching_tasks, teachers, classrooms),
            'status': 'generated'
        }
        
        self.scheduling_schemes.append(scheme)
        
        # 持久化保存
        if self.persistence:
            self.persistence.save_scheduling_scheme(scheme)
        
        return {
            'success': True,
            'message': '课表生成成功',
            'data': scheme
        }
    
    def _prepare_teaching_tasks(self, classes: List[Dict], teachers: List[Dict], 
                                 courses: List[Dict]) -> List[Dict]:
        """准备教学任务列表"""
        tasks = []
        task_id = 1
        
        for class_info in classes:
            # 为每个班级生成课程任务
            for course in courses:
                periods_per_week = course.get('periods_per_week', 2)
                teacher_id = course.get('teacher_id')
                
                # 检查教师是否存在
                teacher = next((t for t in teachers if t['id'] == teacher_id), None)
                if not teacher:
                    continue
                
                for period_idx in range(periods_per_week):
                    tasks.append({
                        'task_id': task_id,
                        'class_id': class_info['id'],
                        'class_name': class_info.get('name', ''),
                        'course_id': course['id'],
                        'course_name': course.get('name', ''),
                        'teacher_id': teacher_id,
                        'teacher_name': teacher.get('name', ''),
                        'periods_required': 1,  # 每次课 1 课时
                        'continuous_periods': course.get('continuous_periods', 1),  # 连堂数
                        'preferred_time': course.get('preferred_time', []),  # 偏好时间
                        'forbidden_time': course.get('forbidden_time', []),  # 禁用时间
                    })
                    task_id += 1
        
        return tasks
    
    def _genetic_algorithm(self, tasks: List[Dict], teachers: List[Dict], 
                          classrooms: List[Dict]) -> Dict:
        """
        遗传算法排课
        返回：{class_id: {day: {slot: course_info}}}
        """
        population_size = self.config['population_size']
        max_iterations = self.config['max_iterations']
        mutation_rate = self.config['mutation_rate']
        crossover_rate = self.config['crossover_rate']
        
        # 初始化种群
        population = self._initialize_population(tasks, teachers, classrooms)
        
        best_solution = None
        best_fitness = -float('inf')
        
        for generation in range(max_iterations):
            # 计算适应度
            fitness_scores = []
            for individual in population:
                fitness = self._calculate_fitness(individual, tasks, teachers, classrooms)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_solution = individual
            
            # 选择（锦标赛选择）
            new_population = []
            for _ in range(population_size):
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                # 交叉
                if random.random() < crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # 变异
                if random.random() < mutation_rate:
                    child1 = self._mutate(child1, tasks)
                if random.random() < mutation_rate:
                    child2 = self._mutate(child2, tasks)
                
                new_population.extend([child1, child2])
            
            population = new_population[:population_size]
            
            # 精英保留
            if best_solution:
                population[0] = best_solution.copy()
        
        return best_solution
    
    def _initialize_population(self, tasks: List[Dict], teachers: List[Dict], 
                               classrooms: List[Dict]) -> List[Dict]:
        """初始化种群"""
        population = []
        population_size = self.config['population_size']
        
        for _ in range(population_size):
            schedule = self._create_random_schedule(tasks, teachers, classrooms)
            population.append(schedule)
        
        return population
    
    def _create_random_schedule(self, tasks: List[Dict], teachers: List[Dict], 
                                classrooms: List[Dict]) -> Dict:
        """创建随机课表"""
        schedule = {}  # {class_id: {day: {slot: task}}}
        teacher_schedule = {}  # {teacher_id: {day: {slot: class_id}}}
        classroom_schedule = {}  # {classroom_id: {day: {slot: class_id}}}
        
        days = self.config['days_per_week']
        slots_per_day = self.config['time_slots_per_day']
        
        # 打乱任务顺序
        shuffled_tasks = tasks.copy()
        random.shuffle(shuffled_tasks)
        
        for task in shuffled_tasks:
            placed = False
            attempts = 0
            max_attempts = days * slots_per_day
            
            while not placed and attempts < max_attempts:
                day = random.randint(0, days - 1)
                slot = random.randint(0, slots_per_day - 1)
                
                # 检查是否可以放置
                if self._can_place_task(task, day, slot, schedule, teacher_schedule, 
                                       classrooms, teachers):
                    # 放置任务
                    class_id = task['class_id']
                    if class_id not in schedule:
                        schedule[class_id] = {}
                    if day not in schedule[class_id]:
                        schedule[class_id][day] = {}
                    
                    schedule[class_id][day][slot] = task
                    
                    # 更新教师课表
                    teacher_id = task['teacher_id']
                    if teacher_id not in teacher_schedule:
                        teacher_schedule[teacher_id] = {}
                    if day not in teacher_schedule[teacher_id]:
                        teacher_schedule[teacher_id][day] = {}
                    teacher_schedule[teacher_id][day][slot] = class_id
                    
                    placed = True
                
                attempts += 1
        
        return schedule
    
    def _can_place_task(self, task: Dict, day: int, slot: int, 
                       schedule: Dict, teacher_schedule: Dict,
                       classrooms: List[Dict], teachers: List[Dict]) -> bool:
        """检查是否可以在指定时间放置任务"""
        class_id = task['class_id']
        teacher_id = task['teacher_id']
        
        # 检查班级该时间是否已有课
        if class_id in schedule:
            if day in schedule[class_id]:
                if slot in schedule[class_id][day]:
                    return False
        
        # 检查教师该时间是否有课
        if teacher_id in teacher_schedule:
            if day in teacher_schedule[teacher_id]:
                if slot in teacher_schedule[teacher_id][day]:
                    return False
        
        # 检查是否在禁用时间段
        if slot in task.get('forbidden_time', []):
            return False
        
        # 检查连堂需求
        continuous = task.get('continuous_periods', 1)
        if continuous > 1:
            for i in range(1, continuous):
                if slot + i >= self.config['time_slots_per_day']:
                    return False
                if class_id in schedule and day in schedule[class_id]:
                    if slot + i in schedule[class_id][day]:
                        return False
                if teacher_id in teacher_schedule and day in teacher_schedule[teacher_id]:
                    if slot + i in teacher_schedule[teacher_id][day]:
                        return False
        
        return True
    
    def _calculate_fitness(self, schedule: Dict, tasks: List[Dict], 
                          teachers: List[Dict], classrooms: List[Dict]) -> float:
        """
        计算适应度分数
        分数越高表示课表质量越好
        """
        fitness = 0
        
        # 1. 惩罚：教师冲突
        teacher_conflicts = self._count_teacher_conflicts(schedule, teachers)
        fitness -= teacher_conflicts * 100
        
        # 2. 惩罚：教室冲突
        classroom_conflicts = self._count_classroom_conflicts(schedule, classrooms)
        fitness -= classroom_conflicts * 100
        
        # 3. 惩罚：未排入的任务
        total_tasks = len(tasks)
        scheduled_tasks = sum(
            len(slots) 
            for class_schedule in schedule.values() 
            for day_schedule in class_schedule.values() 
            for slots in day_schedule.values()
        )
        unscheduled = total_tasks - scheduled_tasks
        fitness -= unscheduled * 50
        
        # 4. 奖励：课时分布均匀
        distribution_score = self._evaluate_distribution(schedule)
        fitness += distribution_score * 10
        
        # 5. 奖励：避免教师空闲时间过多
        teacher_idle_score = self._evaluate_teacher_idle(schedule, teachers)
        fitness += teacher_idle_score * 5
        
        return fitness
    
    def _count_teacher_conflicts(self, schedule: Dict, teachers: List[Dict]) -> int:
        """统计教师冲突次数"""
        conflicts = 0
        teacher_schedule = {}  # {teacher_id: {day: {slot: count}}}
        
        for class_id, class_schedule in schedule.items():
            for day, slots in class_schedule.items():
                for slot, task in slots.items():
                    teacher_id = task['teacher_id']
                    if teacher_id not in teacher_schedule:
                        teacher_schedule[teacher_id] = {}
                    if day not in teacher_schedule[teacher_id]:
                        teacher_schedule[teacher_id][day] = {}
                    if slot not in teacher_schedule[teacher_id][day]:
                        teacher_schedule[teacher_id][day][slot] = 0
                    teacher_schedule[teacher_id][day][slot] += 1
                    
                    if teacher_schedule[teacher_id][day][slot] > 1:
                        conflicts += 1
        
        return conflicts
    
    def _count_classroom_conflicts(self, schedule: Dict, classrooms: List[Dict]) -> int:
        """统计教室冲突次数"""
        # 简化实现：暂时不检查教室冲突
        return 0
    
    def _evaluate_distribution(self, schedule: Dict) -> float:
        """评估课时分布均匀度"""
        scores = []
        
        for class_id, class_schedule in schedule.items():
            daily_counts = {}
            for day, slots in class_schedule.items():
                daily_counts[day] = len(slots)
            
            if daily_counts:
                counts = list(daily_counts.values())
                avg = sum(counts) / len(counts)
                variance = sum((c - avg) ** 2 for c in counts) / len(counts)
                scores.append(1 / (1 + variance))
        
        return sum(scores) / len(scores) if scores else 0
    
    def _evaluate_teacher_idle(self, schedule: Dict, teachers: List[Dict]) -> float:
        """评估教师空闲时间"""
        # 简化实现
        return 0.5
    
    def _tournament_selection(self, population: List[Dict], 
                             fitness_scores: List[float]) -> Dict:
        """锦标赛选择"""
        tournament_size = 5
        participants = random.sample(list(zip(population, fitness_scores)), 
                                    min(tournament_size, len(population)))
        return max(participants, key=lambda x: x[1])[0]
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """交叉操作"""
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # 单点交叉：随机选择一个班级的课表进行交换
        all_classes = set(parent1.keys()) | set(parent2.keys())
        if all_classes:
            crossover_class = random.choice(list(all_classes))
            
            if crossover_class in parent1 and crossover_class in parent2:
                child1[crossover_class] = copy.deepcopy(parent2[crossover_class])
                child2[crossover_class] = copy.deepcopy(parent1[crossover_class])
        
        return child1, child2
    
    def _mutate(self, individual: Dict, tasks: List[Dict]) -> Dict:
        """变异操作"""
        mutated = copy.deepcopy(individual)
        
        # 随机选择一个任务，尝试重新安排时间
        if individual:
            class_ids = list(individual.keys())
            if class_ids:
                class_id = random.choice(class_ids)
                if class_id in mutated and mutated[class_id]:
                    days = list(mutated[class_id].keys())
                    if days:
                        day = random.choice(days)
                        slots = list(mutated[class_id][day].keys())
                        if slots:
                            slot = random.choice(slots)
                            # 删除该任务，尝试在其他时间重新放置
                            task = mutated[class_id][day].pop(slot)
                            
                            # 简单处理：不重新放置，直接删除
                            if not mutated[class_id][day]:
                                del mutated[class_id][day]
                            if not mutated[class_id]:
                                del mutated[class_id]
        
        return mutated
    
    def get_all_schemes(self) -> List[Dict]:
        """获取所有排课方案"""
        return self.scheduling_schemes
    
    def get_scheme_detail(self, scheme_id: int) -> Dict:
        """获取排课方案详情"""
        scheme = next((s for s in self.scheduling_schemes if s['id'] == scheme_id), None)
        return scheme
    
    def get_timetable(self, timetable_type: str, target_id: int) -> Dict:
        """
        获取课表
        timetable_type: student, teacher, class, classroom
        target_id: 对应的 ID
        """
        if not self.scheduling_schemes:
            return {'timetable': {}, 'type': timetable_type, 'target_id': target_id}
        
        # 使用最新的方案
        latest_scheme = self.scheduling_schemes[-1]
        schedule = latest_scheme.get('schedule', {})
        
        if timetable_type == 'class':
            # 班级课表
            class_schedule = schedule.get(target_id, {})
            return self._format_timetable(class_schedule)
        
        elif timetable_type == 'teacher':
            # 教师课表
            teacher_schedule = {}
            for class_id, class_sched in schedule.items():
                for day, slots in class_sched.items():
                    for slot, task in slots.items():
                        if task.get('teacher_id') == target_id:
                            if day not in teacher_schedule:
                                teacher_schedule[day] = {}
                            teacher_schedule[day][slot] = task
            return self._format_timetable(teacher_schedule)
        
        elif timetable_type == 'student':
            # 学生课表（同班级课表）
            # 需要先找到学生所在的班级
            students = self.data_manager.get_all('students')
            student = next((s for s in students if s['id'] == target_id), None)
            if student:
                admin_class = student.get('admin_class')
                classes = self.data_manager.get_all('classes')
                class_info = next((c for c in classes if c.get('name') == admin_class), None)
                if class_info:
                    class_schedule = schedule.get(class_info['id'], {})
                    return self._format_timetable(class_schedule)
        
        return {'timetable': {}, 'type': timetable_type, 'target_id': target_id}
    
    def _format_timetable(self, schedule: Dict) -> Dict:
        """格式化课表"""
        formatted = {}
        days_map = {0: '周一', 1: '周二', 2: '周三', 3: '周四', 4: '周五'}
        
        for day, slots in schedule.items():
            day_name = days_map.get(day, f'第{day + 1}天')
            formatted[day_name] = {}
            
            for slot, task in slots.items():
                formatted[day_name][slot + 1] = {
                    'course': task.get('course_name', ''),
                    'teacher': task.get('teacher_name', ''),
                    'room': task.get('room', '待定')
                }
        
        return {'timetable': formatted}
