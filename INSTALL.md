# 安装指南

## 快速安装（推荐）

### Windows 用户

1. **确保已安装 Python 3.8+**
   - 下载地址：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **运行启动脚本**
   ```
   双击 start.bat
   ```

3. **访问系统**
   - 浏览器打开：http://localhost:8080

## 手动安装

### 步骤 1: 检查 Python 环境

```bash
# 检查 Python 版本（需要 3.8+）
python --version

# 或
py --version
```

如果未安装 Python，请访问 https://www.python.org/downloads/ 下载安装。

### 步骤 2: 安装依赖

#### 方法 A: 使用 pip（标准方式）

```bash
cd scheduling_system
pip install -r requirements.txt
```

#### 方法 B: 使用国内镜像（中国大陆推荐）

```bash
cd scheduling_system
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 方法 C: 逐个安装（如果上述方法失败）

```bash
pip install Flask
pip install pandas
pip install openpyxl
pip install numpy
pip install python-dateutil
```

### 步骤 3: 验证安装

```bash
# 运行测试脚本
python test_core.py
```

如果看到 "所有测试通过" 提示，说明核心功能正常。

### 步骤 4: 启动系统

```bash
python app.py
```

看到以下提示表示启动成功：
```
* Running on http://0.0.0.0:8080
* Running on http://127.0.0.1:8080
```

### 步骤 5: 访问系统

浏览器打开：**http://localhost:8080**

## 常见问题解决

### 问题 1: pip 命令不存在

**解决方案：**
```bash
# Windows 尝试
py -m pip install -r requirements.txt

# 或使用完整路径
C:\Users\你的用户名\AppData\Local\Programs\Python\Python313\Scripts\pip.exe install -r requirements.txt
```

### 问题 2: 权限错误

**解决方案（Windows）：**
- 右键点击 `start.bat`
- 选择 "以管理员身份运行"

**解决方案（Linux/Mac）：**
```bash
sudo pip install -r requirements.txt
```

### 问题 3: 依赖冲突

**解决方案：**
```bash
# 升级 pip
python -m pip install --upgrade pip

# 然后重新安装
pip install -r requirements.txt --force-reinstall
```

### 问题 4: pandas/numpy 安装失败

这通常是因为缺少编译工具。可以尝试：

**Windows:**
```bash
# 下载预编译的 wheel 文件
# 访问：https://www.lfd.uci.edu/~gohlke/pythonlibs/
# 下载对应的 .whl 文件后安装
pip install numpy‑1.26.2‑cp313‑cp313‑win_amd64.whl
pip install pandas‑2.1.3‑cp313‑cp313‑win_amd64.whl
```

**或者使用 conda:**
```bash
conda install numpy pandas
```

### 问题 5: 端口 8080 被占用

**解决方案：**
编辑 `app.py`，修改端口号：
```python
app.run(host='0.0.0.0', port=8081)  # 改为其他端口
```

## 最小化安装（仅核心功能）

如果只需要基本功能，可以只安装 Flask：

```bash
pip install Flask
```

这样可以运行系统，但无法使用 Excel 导入导出功能。

## 离线安装

1. 在有网络的机器上下载依赖包：
```bash
pip download -r requirements.txt -d ./packages
```

2. 将 packages 文件夹复制到目标机器

3. 离线安装：
```bash
pip install -r requirements.txt --no-index --find-links=./packages
```

## 验证安装完整性

运行以下命令检查所有组件：

```bash
python -c "import flask; print(f'Flask: {flask.__version__}')"
python -c "import pandas; print(f'pandas: {pandas.__version__}')"
python -c "import openpyxl; print(f'openpyxl: {openpyxl.__version__}')"
python -c "import numpy; print(f'numpy: {numpy.__version__}')"
```

## 卸载

```bash
pip uninstall Flask pandas openpyxl numpy python-dateutil
```

## 获取帮助

如果安装过程中遇到问题：

1. 查看错误信息
2. 搜索错误关键词
3. 检查 Python 和 pip 版本
4. 尝试使用国内镜像源
5. 考虑使用虚拟环境（venv）

## 使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 激活虚拟环境（Linux/Mac）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行系统
python app.py

# 退出虚拟环境
deactivate
```
