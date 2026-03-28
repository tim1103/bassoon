# 系统改进说明

本文档详细说明了为浙江省新高考选课排课系统实现的四大改进功能。

## 1. 添加输入验证 - 使用 Marshmallow 进行数据校验

### 新增文件
- `schemas/__init__.py` - 定义所有数据校验 Schema

### 功能说明
使用 Marshmallow 库对所有输入数据进行严格校验，防止无效数据进入系统。

#### 支持的 Schema
- **基础数据**: CampusSchema, TeacherSchema, StudentSchema, ClassSchema, ClassroomSchema, CourseSchema
- **选课相关**: SelectionSchemeSchema, SelectionSubmitSchema, OptimizeClassConfigSchema
- **排课相关**: GenerateScheduleConfigSchema

#### 使用示例
```python
from schemas import StudentSchema
from marshmallow import ValidationError

schema = StudentSchema()
try:
    data = schema.load(request.json)
    # 验证通过，data 包含清洗后的数据
except ValidationError as e:
    # 返回验证错误信息
    return jsonify({'success': False, 'errors': e.messages}), 400
```

#### 验证规则示例
- 性别只能是"男"或"女"
- 选课必须是 3 门科目
- 成绩范围 0-100
- 必填字段检查
- 字符串长度限制

---

## 2. 服务层持久化 - SelectionService 和 SchedulingService 数据持久化

### 新增文件
- `models/persistence.py` - ServicePersistence 类

### 修改文件
- `services/selection_service.py` - 添加持久化支持
- `services/scheduling_service.py` - 添加持久化支持
- `app.py` - 初始化 ServicePersistence

### 功能说明
将原本存储在内存中的选课方案、选课记录、分班优化结果和排课方案持久化到 JSON 文件，确保服务重启后数据不丢失。

#### 持久化的数据类型
1. **选课方案** (`selection_schemes.json`)
2. **选课记录** (`selections.json`)
3. **分班优化结果** (`optimized_classes.json`)
4. **排课方案** (`scheduling_schemes.json`)

#### 核心方法
```python
persistence = ServicePersistence(data_dir)

# 保存/读取选课方案
persistence.save_selection_scheme(scheme)
persistence.get_all_selection_schemes()

# 保存/读取选课记录
persistence.save_selection(selection)
persistence.get_all_selections()

# 保存/读取排课方案
persistence.save_scheduling_scheme(scheme)
persistence.get_all_scheduling_schemes()
persistence.get_scheduling_scheme_by_id(scheme_id)
```

---

## 3. 改进错误处理 - 全局异常捕获和结构化日志

### 新增文件
- `utils/error_handler.py` - 错误处理和日志配置
- `utils/validators.py` - 验证装饰器

### 修改文件
- `app.py` - 集成错误处理和日志系统

### 功能说明

#### 3.1 结构化日志
- **JSON 格式日志**: 便于日志分析系统解析
- **按日期分割**: 每天一个日志文件 (`logs/app_YYYYMMDD.log`)
- **双输出**: 同时输出到文件 (JSON) 和控制台 (人类可读)

#### 3.2 自定义异常类
- `APIError` - API 错误基类
- `ValidationError` - 数据验证错误 (400)
- `NotFoundError` - 资源未找到 (404)
- `UnauthorizedError` - 未授权访问 (401)
- `ServerError` - 服务器内部错误 (500)

#### 3.3 全局错误处理器
自动捕获并格式化所有异常，返回统一的 JSON 响应格式：
```json
{
    "success": false,
    "message": "错误描述",
    "errors": {}  // 验证错误详情
}
```

#### 使用示例
```python
from utils.error_handler import ValidationError, NotFoundError

# 抛出验证错误
raise ValidationError('数据验证失败', errors={'name': ['不能为空']})

# 抛出未找到错误
raise NotFoundError('学生不存在')
```

---

## 4. 前端体验 - 加载状态和数据可视化

### 新增文件
- `static/js/dashboard.js` - 数据可视化组件
- `static/css/style.css` - 新增样式（追加）

### 功能说明

#### 4.1 数据可视化 (Chart.js)
- **饼图**: 展示基础数据统计（校区、教师、学生等分布）
- **柱状图**: 展示选科统计（各科目选课人数）
- **动态更新**: 自动从 API 加载数据并渲染

#### 4.2 加载状态
- **旋转加载动画**: 数据加载时显示 spinner
- **Toast 提示**: 操作成功/失败的浮动提示
- **错误信息显示**: 友好的错误提示框

#### 4.3 CSS 样式
```css
/* 加载动画 */
.loading-spinner { ... }
.spinner { ... }

/* Toast 提示 */
.toast { ... }
.toast-success { background-color: #4CAF50; }
.toast-error { background-color: #f44336; }

/* 统计卡片 */
.stats-grid { ... }
.stat-card { ... }

/* 图表容器 */
.chart-container { height: 300px; }
```

#### 4.4 JavaScript 工具函数
```javascript
// 显示加载状态
showLoading('containerId');

// 隐藏加载状态
hideLoading('containerId');

// 显示成功提示
showSuccess('操作成功');

// 显示错误提示
showToastError('操作失败');

// 创建图表
createPieChart('chartId', data);
createBarChart('chartId', labels, values, title);
```

---

## 依赖更新

### requirements.txt 新增
```
marshmallow>=3.14.0      # 数据验证
python-json-logger>=2.0.0 # JSON 日志格式
```

### 前端依赖
需要在 HTML 模板中添加 Chart.js CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

---

## 测试验证

运行测试脚本验证所有改进功能:
```bash
python test_improvements.py
```

测试结果:
- ✓ Marshmallow Schema 验证
- ✓ 服务层持久化
- ✓ 错误处理
- ✓ API 正常响应

---

## 使用建议

### 1. 在 API 中使用验证装饰器
```python
from utils.validators import validate_request
from schemas import StudentSchema

@app.route('/api/students', methods=['POST'])
@validate_request(StudentSchema)
def create_student():
    data = request.validated_data  # 已验证的数据
    result = data_manager.add('students', data)
    return jsonify(result)
```

### 2. 在前端使用可视化和加载状态
```html
<!-- 统计卡片 -->
<div class="stats-grid">
    <div class="stat-card">
        <div class="icon">👨‍🏫</div>
        <h3>教师数量</h3>
        <div class="value" id="teacherCount">0</div>
    </div>
</div>

<!-- 图表容器 -->
<div class="chart-container">
    <canvas id="basicDataChart"></canvas>
</div>
```

### 3. 查看日志
```bash
# 实时查看日志
tail -f logs/app_$(date +%Y%m%d).log

# 或使用 jq 格式化 JSON 日志
cat logs/app_*.log | jq .
```

---

## 后续改进建议

1. **数据库迁移**: 从 JSON 文件迁移到 SQLite/PostgreSQL
2. **用户认证**: 添加 Flask-Login 和用户角色管理
3. **缓存层**: 使用 Redis 缓存频繁访问的数据
4. **异步任务**: 使用 Celery 处理耗时排课任务
5. **单元测试**: 使用 pytest 编写完整测试套件
6. **API 文档**: 使用 Swagger/OpenAPI 生成文档
7. **Docker 部署**: 容器化便于部署和扩展
