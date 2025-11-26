#!/usr/bin/env python3
"""
核素查询工具
支持实验数据和理论计算数据的命令行查询
"""

from typing import Optional, Tuple, List
from .nuclide import Nuclide
from .data_source import get_data_source_manager, list_sources


def parse_nuclide_string(nuclide_str: str) -> tuple:
    """
    解析元素符号+质量数格式的核素字符串
    已废弃，请使用 Nuclide.parse_str
    """
    return Nuclide.parse_str(nuclide_str)
    
    
class NuclideQuery:
    """核素查询类 - 核心服务"""
    
    def __init__(self, source: str = 'experiment'):
        """
        初始化查询器
        
        参数:
            source: 数据源名称 ('experiment', 'SKMS', 'UNEDF1', 等)
        """
        self._source_name = source
    
    @property
    def source_name(self) -> str:
        """当前数据源名称"""
        return self._source_name
    
    def set_source(self, source: str):
        """切换数据源"""
        self._source_name = source
    
    def list_sources(self) -> List[str]:
        """列出所有可用数据源"""
        return list_sources()
    
    def query_nuclide(self, Z: int, N: int) -> Optional[Nuclide]:
        """
        查询指定质子数和中子数的核素数据
        
        参数:
            Z: 质子数
            N: 中子数
            
        返回:
            Nuclide 对象，如果未找到则返回None
        """
        nuc = Nuclide(Z, N, source=self._source_name)
        return nuc if nuc.exists else None

    def query_range(self, Z_min: int, Z_max: int, N_min: int, N_max: int) -> List[Nuclide]:
        """
        查询指定范围内的所有核素
        
        参数:
            Z_min, Z_max: 质子数范围
            N_min, N_max: 中子数范围
            
        返回:
            Nuclide 对象列表
        """
        manager = get_data_source_manager()
        src_obj = manager.get_source(self._source_name)
        
        results = []
        
        # 获取所有存在的核素列表，避免无效查询
        all_nuclides = src_obj.list_nuclides()
        
        for Z, N in all_nuclides:
            if Z_min <= Z <= Z_max and N_min <= N <= N_max:
                # 获取数据并创建对象
                data = src_obj.get_nuclide(Z, N)
                nuc = Nuclide(Z, N, source=self._source_name, data=data)
                results.append(nuc)
        
        # 按 Z 然后 N 排序
        results.sort(key=lambda x: (x.Z, x.N))
        
        return results
    
    def query_isotopes(self, Z: int, N_min: Optional[int] = None, N_max: Optional[int] = None) -> List[Nuclide]:
        """
        查询指定元素的所有同位素
        
        参数:
            Z: 质子数
            N_min, N_max: 中子数范围（可选）
            
        返回:
            Nuclide 对象列表
        """
        manager = get_data_source_manager()
        src_obj = manager.get_source(self._source_name)
        
        # 从数据源获取真实的同位素数据列表
        props_list = src_obj.get_isotopes(Z)
        
        nuclides = []
        for props in props_list:
            N = props['N']
            # 如果指定了范围，进行过滤
            if N_min is not None and N < N_min:
                continue
            if N_max is not None and N > N_max:
                continue
            
            # 创建 Nuclide 对象 (传入预加载的数据)
            nuc = Nuclide(Z, N, source=self._source_name, data=props)
            nuclides.append(nuc)
            
        return nuclides
    
    def query_isotones(self, N: int, Z_min: Optional[int] = None, Z_max: Optional[int] = None) -> List[Nuclide]:
        """
        查询指定中子数的所有同中子素
        
        参数:
            N: 中子数
            Z_min, Z_max: 质子数范围（可选）
            
        返回:
            Nuclide 对象列表
        """
        manager = get_data_source_manager()
        src_obj = manager.get_source(self._source_name)
        
        # 从数据源获取真实的同中子素数据列表
        props_list = src_obj.get_isotones(N)
        
        nuclides = []
        for props in props_list:
            Z = props['Z']
            # 如果指定了范围，进行过滤
            if Z_min is not None and Z < Z_min:
                continue
            if Z_max is not None and Z > Z_max:
                continue
                
            nuc = Nuclide(Z, N, source=self._source_name, data=props)
            nuclides.append(nuc)
            
        return nuclides
    
    def query_from_list(self, nuclide_list: List[Tuple[int, int]]) -> List[Nuclide]:
        """
        从给定的核素列表查询数据
        
        参数:
            nuclide_list: [(Z1, N1), (Z2, N2), ...] 的列表
            
        返回:
            Nuclide 对象列表
        """
        results = []
        
        for Z, N in nuclide_list:
            nuc = Nuclide(Z, N, source=self._source_name)
            if nuc.exists:
                results.append(nuc)
        
        return results