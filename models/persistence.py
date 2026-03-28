"""
服务层持久化模块
将 SelectionService 和 SchedulingService 的数据持久化到 JSON 文件
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any


class ServicePersistence:
    """服务数据持久化管理器"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.selections_file = os.path.join(data_dir, 'selections.json')
        self.schemes_file = os.path.join(data_dir, 'selection_schemes.json')
        self.optimized_classes_file = os.path.join(data_dir, 'optimized_classes.json')
        self.scheduling_schemes_file = os.path.join(data_dir, 'scheduling_schemes.json')
        
        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化文件
        self._init_files()
    
    def _init_files(self):
        """初始化数据文件"""
        file_paths = [
            self.selections_file,
            self.schemes_file,
            self.optimized_classes_file,
            self.scheduling_schemes_file
        ]
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    # ==================== 选课方案持久化 ====================
    
    def save_selection_scheme(self, scheme: Dict) -> None:
        """保存选课方案"""
        schemes = self._load_json(self.schemes_file)
        
        # 检查是否已存在，存在则更新
        existing_idx = next((i for i, s in enumerate(schemes) if s['id'] == scheme['id']), None)
        if existing_idx is not None:
            schemes[existing_idx] = scheme
        else:
            schemes.append(scheme)
        
        self._save_json(self.schemes_file, schemes)
    
    def get_all_selection_schemes(self) -> List[Dict]:
        """获取所有选课方案"""
        return self._load_json(self.schemes_file)
    
    # ==================== 选课结果持久化 ====================
    
    def save_selection(self, selection: Dict) -> None:
        """保存选课记录"""
        selections = self._load_json(self.selections_file)
        selections.append(selection)
        self._save_json(self.selections_file, selections)
    
    def get_all_selections(self) -> List[Dict]:
        """获取所有选课记录"""
        return self._load_json(self.selections_file)
    
    def clear_selections(self) -> None:
        """清空选课记录"""
        self._save_json(self.selections_file, [])
    
    # ==================== 分班优化结果持久化 ====================
    
    def save_optimized_classes(self, optimized_classes: List[Dict]) -> None:
        """保存分班优化结果"""
        self._save_json(self.optimized_classes_file, optimized_classes)
    
    def get_optimized_classes(self) -> List[Dict]:
        """获取分班优化结果"""
        return self._load_json(self.optimized_classes_file)
    
    # ==================== 排课方案持久化 ====================
    
    def save_scheduling_scheme(self, scheme: Dict) -> None:
        """保存排课方案"""
        schemes = self._load_json(self.scheduling_schemes_file)
        
        # 检查是否已存在，存在则更新
        existing_idx = next((i for i, s in enumerate(schemes) if s['id'] == scheme['id']), None)
        if existing_idx is not None:
            schemes[existing_idx] = scheme
        else:
            schemes.append(scheme)
        
        self._save_json(self.scheduling_schemes_file, schemes)
    
    def get_all_scheduling_schemes(self) -> List[Dict]:
        """获取所有排课方案"""
        return self._load_json(self.scheduling_schemes_file)
    
    def get_scheduling_scheme_by_id(self, scheme_id: int) -> Dict:
        """根据 ID 获取排课方案"""
        schemes = self._load_json(self.scheduling_schemes_file)
        return next((s for s in schemes if s['id'] == scheme_id), None)
    
    # ==================== 工具方法 ====================
    
    def _load_json(self, file_path: str) -> List[Dict]:
        """加载 JSON 文件"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载数据失败 {file_path}: {e}")
        return []
    
    def _save_json(self, file_path: str, data: Any) -> None:
        """保存 JSON 文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败 {file_path}: {e}")
            raise
