"""
Excel 处理模块
支持数据的导入导出
"""
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List


class ExcelHandler:
    """Excel 处理器"""
    
    # 定义各数据类型的模板列
    TEMPLATES = {
        'teachers': ['姓名', '性别', '学历', '职称', '手机号', '邮箱', '任教学科', '备注'],
        'students': ['学号', '姓名', '性别', '行政班', '联系电话', '备注'],
        'classes': ['班级名称', '年级', '类型', '班主任', '学生人数', '备注'],
        'classrooms': ['教室编号', '教室名称', '类型', '容量', '所在楼层', '备注'],
        'campuses': ['校区名称', '地址', '备注'],
    }
    
    def __init__(self):
        self.export_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'exports')
        os.makedirs(self.export_dir, exist_ok=True)
    
    def create_template(self, data_type: str) -> str:
        """创建 Excel 模板文件"""
        if data_type not in self.TEMPLATES:
            return None
        
        df = pd.DataFrame(columns=self.TEMPLATES[data_type])
        filename = f"{data_type}_template.xlsx"
        filepath = os.path.join(self.export_dir, filename)
        
        df.to_excel(filepath, index=False, sheet_name='模板')
        return filepath
    
    def import_data(self, filepath: str, data_type: str, data_manager) -> Dict:
        """从 Excel 导入数据"""
        try:
            # 读取 Excel
            df = pd.read_excel(filepath)
            
            # 数据校验和转换
            items = []
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    item = self._validate_and_convert(row, data_type)
                    if item:
                        items.append(item)
                    else:
                        errors.append(f"第{idx + 2}行：数据格式错误")
                except Exception as e:
                    errors.append(f"第{idx + 2}行：{str(e)}")
            
            # 批量添加数据
            if items:
                result = data_manager.batch_add(data_type, items)
                return {
                    'success': True,
                    'message': f'成功导入{result["count"]}条记录',
                    'count': result['count'],
                    'errors': errors[:10] if errors else []  # 最多显示 10 个错误
                }
            else:
                return {
                    'success': False,
                    'message': '没有有效数据',
                    'errors': errors
                }
                
        except Exception as e:
            return {'success': False, 'message': f'导入失败：{str(e)}'}
    
    def _validate_and_convert(self, row: pd.Series, data_type: str) -> Dict:
        """验证并转换单行数据"""
        item = {}
        
        if data_type == 'teachers':
            item = {
                'name': str(row.get('姓名', '')),
                'gender': str(row.get('性别', '')),
                'education': str(row.get('学历', '')),
                'title': str(row.get('职称', '')),
                'phone': str(row.get('手机号', '')),
                'email': str(row.get('邮箱', '')),
                'subjects': str(row.get('任教学科', '')).split(','),
                'remark': str(row.get('备注', ''))
            }
            # 必填项校验
            if not item['name']:
                return None
                
        elif data_type == 'students':
            item = {
                'student_id': str(row.get('学号', '')),
                'name': str(row.get('姓名', '')),
                'gender': str(row.get('性别', '')),
                'admin_class': str(row.get('行政班', '')),
                'phone': str(row.get('联系电话', '')),
                'remark': str(row.get('备注', ''))
            }
            if not item['student_id'] or not item['name']:
                return None
                
        elif data_type == 'classes':
            item = {
                'name': str(row.get('班级名称', '')),
                'grade': str(row.get('年级', '')),
                'type': str(row.get('类型', '行政班')),
                'head_teacher': str(row.get('班主任', '')),
                'student_count': int(row.get('学生人数', 0)),
                'remark': str(row.get('备注', ''))
            }
            if not item['name']:
                return None
                
        elif data_type == 'classrooms':
            item = {
                'code': str(row.get('教室编号', '')),
                'name': str(row.get('教室名称', '')),
                'type': str(row.get('类型', '普通教室')),
                'capacity': int(row.get('容量', 50)),
                'floor': str(row.get('所在楼层', '')),
                'remark': str(row.get('备注', ''))
            }
            if not item['code']:
                return None
        
        return item
    
    def export_data(self, data: List[Dict], data_type: str) -> str:
        """导出数据到 Excel"""
        if not data:
            raise ValueError('没有数据可导出')
        
        # 转换为 DataFrame
        df = pd.DataFrame(data)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{data_type}_{timestamp}.xlsx"
        filepath = os.path.join(self.export_dir, filename)
        
        # 导出
        df.to_excel(filepath, index=False, sheet_name=data_type)
        
        return filepath
