"""
数据管理模块
负责基础数据的 CRUD 操作
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class DataManager:
    """数据管理器"""
    
    def __init__(self, data_files: Dict[str, str] = None):
        self.data_files = data_files or {}
        self._cache = {}
        self._load_all()
    
    def _load_all(self):
        """加载所有数据到缓存"""
        for key, path in self.data_files.items():
            self._load_data(key, path)
    
    def _load_data(self, key: str, path: str):
        """加载单个数据文件"""
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self._cache[key] = json.load(f)
            else:
                self._cache[key] = []
        except Exception as e:
            print(f"加载数据失败 {key}: {e}")
            self._cache[key] = []
    
    def _save_data(self, key: str):
        """保存数据到文件"""
        if key not in self.data_files:
            return
        
        path = self.data_files[key]
        # 确保目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._cache[key], f, ensure_ascii=False, indent=2)
    
    def get_all(self, data_type: str) -> List[Dict]:
        """获取所有数据"""
        return self._cache.get(data_type, [])
    
    def get_by_id(self, data_type: str, item_id: int) -> Optional[Dict]:
        """根据 ID 获取数据"""
        items = self._cache.get(data_type, [])
        for item in items:
            if item.get('id') == item_id:
                return item
        return None
    
    def add(self, data_type: str, item: Dict) -> Dict:
        """添加数据"""
        if data_type not in self._cache:
            self._cache[data_type] = []
        
        # 生成新 ID
        max_id = max([x.get('id', 0) for x in self._cache[data_type]], default=0)
        item['id'] = max_id + 1
        item['created_at'] = datetime.now().isoformat()
        item['updated_at'] = datetime.now().isoformat()
        
        self._cache[data_type].append(item)
        self._save_data(data_type)
        
        return {'success': True, 'data': item}
    
    def update(self, data_type: str, item_id: int, item: Dict) -> Dict:
        """更新数据"""
        items = self._cache.get(data_type, [])
        for i, existing in enumerate(items):
            if existing.get('id') == item_id:
                item['id'] = item_id
                item['updated_at'] = datetime.now().isoformat()
                # 保留创建时间
                if 'created_at' in existing:
                    item['created_at'] = existing['created_at']
                items[i] = item
                self._save_data(data_type)
                return {'success': True, 'data': item}
        
        return {'success': False, 'message': '未找到记录'}
    
    def delete(self, data_type: str, item_id: int) -> Dict:
        """删除数据"""
        items = self._cache.get(data_type, [])
        original_len = len(items)
        self._cache[data_type] = [x for x in items if x.get('id') != item_id]
        
        if len(self._cache[data_type]) < original_len:
            self._save_data(data_type)
            return {'success': True}
        
        return {'success': False, 'message': '未找到记录'}
    
    def batch_add(self, data_type: str, items: List[Dict]) -> Dict:
        """批量添加数据"""
        if data_type not in self._cache:
            self._cache[data_type] = []
        
        max_id = max([x.get('id', 0) for x in self._cache[data_type]], default=0)
        now = datetime.now().isoformat()
        
        added_items = []
        for i, item in enumerate(items):
            item['id'] = max_id + i + 1
            item['created_at'] = now
            item['updated_at'] = now
            added_items.append(item)
        
        self._cache[data_type].extend(added_items)
        self._save_data(data_type)
        
        return {'success': True, 'count': len(added_items), 'data': added_items}
    
    def find(self, data_type: str, filters: Dict) -> List[Dict]:
        """根据条件查找数据"""
        items = self._cache.get(data_type, [])
        result = []
        
        for item in items:
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                result.append(item)
        
        return result
    
    def get_overview_stats(self) -> Dict:
        """获取统计概览"""
        stats = {}
        for key in self._cache.keys():
            stats[key] = len(self._cache[key])
        return stats
