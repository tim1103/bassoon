# 浙江省新高考选课排课系统

基于 Python Flask 的新高考选课排课系统，支持 7 选 3 模式、行政班 + 走班制混合排课、语数英分层教学等功能。

## 功能特性

### 基础数据管理
- 校区/学部管理
- 学年/学期管理
- 班级管理（行政班/教学班）
- 教师信息管理
- 学生信息管理
- 教室信息管理
- Excel 批量导入/导出
- 数据校验与提示

### 选课管理
- 选课方案制定
- 规则引擎（互斥、连选、禁选、人数限制、性别限制）
- 学生预选流程
- 选课结果确认
- 人工调整
- 分班优化（成绩均衡、男女均衡、原行政班集中）

### 排课管理
- 多种排课模式（行政班、教学班、先选后排、先排后选、大走班、定二走一）
- 约束条件处理（教师互斥、教室容量、课时连续、特定时段、跨年级冲突规避）
- 自动生成多套方案
- 冲突自动规避
- 生成各类课表（学生/教师/教室/班级）

### 查询统计
- 数据统计概览
- 选课统计分析
- 课表查询与打印
- 数据导出
- 数据归档

## 技术栈

- **后端**: Python 3.8+, Flask 3.0
- **数据处理**: pandas, openpyxl, numpy
- **数据存储**: JSON 文件（可扩展为 SQLite/MySQL）
- **前端**: HTML5, CSS3, JavaScript (原生)
- **排课算法**: 遗传算法 + 模拟退火

## 安装与运行

### 环境要求
- Python 3.8 或更高版本
- Windows / Linux / macOS

### 快速开始

#### 方法一：使用启动脚本（Windows）
1. 双击运行 `start.bat`
2. 浏览器访问 http://localhost:8080

#### 方法二：手动运行
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动系统
python app.py

# 3. 访问系统
# 浏览器打开 http://localhost:8080
```

### 依赖安装
```bash
pip install Flask==3.0.0
pip install pandas==2.1.3
pip install openpyxl==3.1.2
pip install numpy==1.26.2
```

或使用清华镜像源加速：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 项目结构

```
scheduling_system/
├── app.py                 # 主应用入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
├── start.bat              # Windows 启动脚本
├── data/                  # 数据文件目录
│   ├── campuses.json      # 校区数据
│   ├── classes.json       # 班级数据
│   ├── teachers.json      # 教师数据
│   ├── students.json      # 学生数据
│   ├── classrooms.json    # 教室数据
│   └── courses.json       # 课程数据
├── templates/             # HTML 模板
│   ├── base.html          # 基础模板
│   ├── index.html         # 首页
│   ├── data.html          # 数据管理页
│   ├── selection.html     # 选课管理页
│   ├── scheduling.html    # 排课管理页
│   └── query.html         # 查询统计页
├── static/                # 静态资源
│   ├── css/
│   │   └── style.css      # 样式文件
│   └── js/
│       └── main.js        # JavaScript 文件
├── models/                # 数据模型层
│   └── data_manager.py    # 数据管理器
├── services/              # 业务服务层
│   ├── selection_service.py   # 选课服务
│   └── scheduling_service.py  # 排课服务
└── utils/                 # 工具类
    └── excel_handler.py   # Excel 处理器
```

## 使用流程

### 1. 初始化基础数据
1. 进入"基础数据"页面
2. 手动添加或通过 Excel 导入：
   - 校区信息
   - 班级信息
   - 教师信息
   - 学生信息
   - 教室信息
   - 课程信息

### 2. 创建选课方案
1. 进入"选课管理"页面
2. 创建选课方案，设置规则：
   - 互斥科目（如物理和历史不能同选）
   - 必选组合（如选了化学必须选物理）
   - 人数限制
   - 其他约束条件

### 3. 学生选课
1. 学生提交选课志愿（7 选 3）
2. 系统自动校验规则
3. 查看选课结果统计

### 4. 分班优化
1. 设置优化参数：
   - 最大/最小班级人数
   - 是否男女均衡
   - 是否成绩均衡
   - 是否行政班集中
2. 执行分班优化
3. 查看优化结果

### 5. 生成课表
1. 进入"排课管理"页面
2. 设置排课参数
3. 点击"开始排课"
4. 系统自动生成最优课表
5. 可生成多套方案供选择

### 6. 查询与导出
1. 查询学生/教师/班级/教室课表
2. 导出各类数据为 Excel
3. 打印课表

## API 接口

### 基础数据 API
- `GET/POST /api/campuses` - 校区管理
- `GET/POST /api/classes` - 班级管理
- `GET/POST /api/teachers` - 教师管理
- `GET/POST /api/students` - 学生管理
- `GET/POST /api/classrooms` - 教室管理
- `GET/POST /api/courses` - 课程管理

### 导入导出 API
- `POST /api/import/<type>` - 导入 Excel
- `GET /api/export/<type>` - 导出 Excel

### 选课 API
- `POST /api/selection/scheme` - 创建选课方案
- `GET /api/selection/schemes` - 获取方案列表
- `POST /api/selection/submit` - 提交选课
- `GET /api/selection/results` - 获取选课结果
- `POST /api/selection/optimize` - 分班优化

### 排课 API
- `POST /api/scheduling/generate` - 生成课表
- `GET /api/scheduling/schemes` - 获取排课方案
- `GET /api/scheduling/timetable` - 获取课表

### 统计 API
- `GET /api/stats/overview` - 概览统计
- `GET /api/stats/selection` - 选课统计

## 配置说明

在 `config.py` 中可以修改以下配置：

```python
# 每天课时数
'time_slots_per_day': 8

# 每周天数
'days_per_week': 5

# 遗传算法参数
'max_iterations': 1000      # 最大迭代次数
'population_size': 50       # 种群大小
'mutation_rate': 0.1        # 变异率
'crossover_rate': 0.8       # 交叉率
```

## 课时时间定义

默认课时时间安排（可在 config.py 修改）：
1. 08:00-08:45
2. 08:55-09:40
3. 10:00-10:45
4. 10:55-11:40
5. 14:00-14:45
6. 14:55-15:40
7. 16:00-16:45
8. 16:55-17:40

## 常见问题

### 1. 依赖安装失败
- 确保 Python 版本 >= 3.8
- 使用国内镜像源：`-i https://pypi.tuna.tsinghua.edu.cn/simple`

### 2. 端口被占用
- 修改 `app.py` 中的端口号：`app.run(host='0.0.0.0', port=8080)`

### 3. 中文乱码
- 确保文件使用 UTF-8 编码保存
- Windows 系统可运行 `chcp 65001` 切换代码页

### 4. Excel 导入失败
- 确保 Excel 文件格式正确
- 检查必填字段是否完整
- 查看错误提示信息

## 扩展开发

### 添加新的数据类型
1. 在 `config.py` 的 `DATA_FILES` 中添加文件路径
2. 在 `app.py` 中添加对应的 API 路由
3. 在 `templates/data.html` 的 `fieldConfigs` 中添加字段配置

### 自定义排课规则
1. 修改 `services/scheduling_service.py`
2. 在 `_can_place_task` 方法中添加约束检查
3. 在 `_calculate_fitness` 方法中调整适应度计算

### 集成数据库存储
1. 安装 SQLAlchemy: `pip install sqlalchemy`
2. 创建数据库模型类
3. 修改 `DataManager` 使用数据库操作

## 许可证

MIT License

## 技术支持

如有问题或建议，请联系开发团队。
