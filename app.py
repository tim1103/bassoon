"""
浙江省新高考选课排课系统
主应用入口
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime

from config import Config
from models.data_manager import DataManager
from models.persistence import ServicePersistence
from services.selection_service import SelectionService
from services.scheduling_service import SchedulingService
from utils.excel_handler import ExcelHandler

app = Flask(__name__)
app.config.from_object(Config)

# 初始化日志系统
from utils.error_handler import setup_logging, register_error_handlers
logger = setup_logging(app)
register_error_handlers(app)

# 初始化服务
data_manager = DataManager()
persistence = ServicePersistence(Config.DATA_DIR)
selection_service = SelectionService(data_manager, persistence)
scheduling_service = SchedulingService(data_manager, persistence)
excel_handler = ExcelHandler()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/data')
def data_page():
    """基础数据管理页面"""
    return render_template('data.html')


@app.route('/selection')
def selection_page():
    """选课管理页面"""
    return render_template('selection.html')


@app.route('/scheduling')
def scheduling_page():
    """排课管理页面"""
    return render_template('scheduling.html')


@app.route('/query')
def query_page():
    """查询统计页面"""
    return render_template('query.html')


# ==================== 基础数据管理 ====================

@app.route('/api/campuses', methods=['GET', 'POST'])
def manage_campuses():
    """校区管理"""
    if request.method == 'GET':
        data = data_manager.get_all('campuses')
        return jsonify({'success': True, 'data': data})
    elif request.method == 'POST':
        campus = request.json
        result = data_manager.add('campuses', campus)
        return jsonify(result)


@app.route('/api/campuses/<int:campus_id>', methods=['PUT', 'DELETE'])
def update_campus(campus_id):
    """更新/删除校区"""
    if request.method == 'PUT':
        campus = request.json
        result = data_manager.update('campuses', campus_id, campus)
        return jsonify(result)
    elif request.method == 'DELETE':
        result = data_manager.delete('campuses', campus_id)
        return jsonify(result)


@app.route('/api/teachers', methods=['GET', 'POST'])
def manage_teachers():
    """教师管理"""
    if request.method == 'GET':
        data = data_manager.get_all('teachers')
        return jsonify({'success': True, 'data': data})
    elif request.method == 'POST':
        teacher = request.json
        result = data_manager.add('teachers', teacher)
        return jsonify(result)


@app.route('/api/teachers/<int:teacher_id>', methods=['PUT', 'DELETE'])
def update_teacher(teacher_id):
    """更新/删除教师"""
    if request.method == 'PUT':
        teacher = request.json
        result = data_manager.update('teachers', teacher_id, teacher)
        return jsonify(result)
    elif request.method == 'DELETE':
        result = data_manager.delete('teachers', teacher_id)
        return jsonify(result)


@app.route('/api/students', methods=['GET', 'POST'])
def manage_students():
    """学生管理"""
    if request.method == 'GET':
        data = data_manager.get_all('students')
        return jsonify({'success': True, 'data': data})
    elif request.method == 'POST':
        student = request.json
        result = data_manager.add('students', student)
        return jsonify(result)


@app.route('/api/students/<int:student_id>', methods=['PUT', 'DELETE'])
def update_student(student_id):
    """更新/删除学生"""
    if request.method == 'PUT':
        student = request.json
        result = data_manager.update('students', student_id, student)
        return jsonify(result)
    elif request.method == 'DELETE':
        result = data_manager.delete('students', student_id)
        return jsonify(result)


@app.route('/api/classes', methods=['GET', 'POST'])
def manage_classes():
    """班级管理"""
    if request.method == 'GET':
        data = data_manager.get_all('classes')
        return jsonify({'success': True, 'data': data})
    elif request.method == 'POST':
        class_info = request.json
        result = data_manager.add('classes', class_info)
        return jsonify(result)


@app.route('/api/classrooms', methods=['GET', 'POST'])
def manage_classrooms():
    """教室管理"""
    if request.method == 'GET':
        data = data_manager.get_all('classrooms')
        return jsonify({'success': True, 'data': data})
    elif request.method == 'POST':
        classroom = request.json
        result = data_manager.add('classrooms', classroom)
        return jsonify(result)


@app.route('/api/courses', methods=['GET', 'POST'])
def manage_courses():
    """课程管理"""
    if request.method == 'GET':
        data = data_manager.get_all('courses')
        return jsonify({'success': True, 'data': data})
    elif request.method == 'POST':
        course = request.json
        result = data_manager.add('courses', course)
        return jsonify(result)


@app.route('/api/courses/<int:course_id>', methods=['PUT', 'DELETE'])
def update_course(course_id):
    """更新/删除课程"""
    if request.method == 'PUT':
        course = request.json
        result = data_manager.update('courses', course_id, course)
        return jsonify(result)
    elif request.method == 'DELETE':
        result = data_manager.delete('courses', course_id)
        return jsonify(result)


# ==================== Excel 导入导出 ====================

@app.route('/api/import/<data_type>', methods=['POST'])
def import_data(data_type):
    """导入 Excel 数据"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未找到上传文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '文件名为空'})
    
    try:
        # 保存临时文件
        temp_path = os.path.join(Config.DATA_DIR, f'temp_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx')
        file.save(temp_path)
        
        # 导入数据
        result = excel_handler.import_data(temp_path, data_type, data_manager)
        
        # 删除临时文件
        os.remove(temp_path)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/export/<data_type>')
def export_data(data_type):
    """导出 Excel 数据"""
    try:
        data = data_manager.get_all(data_type)
        filename = excel_handler.export_data(data, data_type)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# ==================== 选课管理 ====================

@app.route('/api/selection/scheme', methods=['POST'])
def create_selection_scheme():
    """创建选课方案"""
    scheme = request.json
    result = selection_service.create_scheme(scheme)
    return jsonify(result)


@app.route('/api/selection/schemes', methods=['GET'])
def get_selection_schemes():
    """获取所有选课方案"""
    schemes = selection_service.get_all_schemes()
    return jsonify({'success': True, 'data': schemes})


@app.route('/api/selection/submit', methods=['POST'])
def submit_selection():
    """学生提交选课志愿"""
    selection = request.json
    result = selection_service.submit_selection(selection)
    return jsonify(result)


@app.route('/api/selection/results')
def get_selection_results():
    """获取选课结果"""
    results = selection_service.get_results()
    return jsonify({'success': True, 'data': results})


@app.route('/api/selection/optimize', methods=['POST'])
def optimize_classes():
    """分班优化"""
    config = request.json
    result = selection_service.optimize_classes(config)
    return jsonify(result)


# ==================== 排课管理 ====================

@app.route('/api/scheduling/generate', methods=['POST'])
def generate_schedule():
    """生成课表"""
    config = request.json
    result = scheduling_service.generate_schedules(config)
    return jsonify(result)


@app.route('/api/scheduling/schemes')
def get_scheduling_schemes():
    """获取排课方案列表"""
    schemes = scheduling_service.get_all_schemes()
    return jsonify({'success': True, 'data': schemes})


@app.route('/api/scheduling/scheme/<int:scheme_id>')
def get_schedule_detail(scheme_id):
    """获取排课方案详情"""
    scheme = scheduling_service.get_scheme_detail(scheme_id)
    if scheme:
        return jsonify({'success': True, 'data': scheme})
    return jsonify({'success': False, 'message': '方案不存在'}), 404


@app.route('/api/scheduling/timetable')
def get_timetable():
    """获取课表（学生/教师/班级/教室）"""
    timetable_type = request.args.get('type', 'student')
    target_id = request.args.get('id', type=int)
    
    timetable = scheduling_service.get_timetable(timetable_type, target_id)
    return jsonify({'success': True, 'data': timetable})


# ==================== 查询统计 ====================

@app.route('/api/stats/overview')
def get_overview_stats():
    """获取统计概览"""
    stats = data_manager.get_overview_stats()
    return jsonify({'success': True, 'data': stats})


@app.route('/api/stats/selection')
def get_selection_stats():
    """获取选课统计"""
    stats = selection_service.get_statistics()
    return jsonify({'success': True, 'data': stats})


if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    
    # 初始化数据文件
    for key, path in Config.DATA_FILES.items():
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
