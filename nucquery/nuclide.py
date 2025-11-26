#!/usr/bin/env python3
"""
核素数据便捷访问接口

提供简洁、直观的属性访问方式，支持IDE自动补全
支持实验数据和理论计算数据（SKMS, UNEDF1 等）

示例:
    >>> nuc = Nuclide(26, 30)  # Fe-56
    >>> print(nuc.BE)  # 结合能
    >>> print(nuc.Sn)  # 中子分离能
    
    >>> nuc_theo = Nuclide(26, 30, source='SKMS')
    >>> print(nuc_theo.BE)
"""

from typing import Optional, List, Tuple, Dict
import re

from .data_source import (
    DataSource, DataSourceManager, get_data_source_manager,
    ExperimentalDataSource, TheoreticalDataSource, list_sources
)
from .nuclide_data import NuclideProperties, ValueWithUncertainty, ELEMENT_SYMBOLS


class Nuclide:
    """
    核素数据封装类
    
    提供简洁的属性访问接口，如 .BE, .Sn, .S2n 等
    支持实验数据和理论数据
    
    属性列表:
        基本信息: Z, N, A, name, symbol, exists, source
        结合能: BE (MeV), BE_A (MeV/核子)
        分离能: Sn, Sp, S2n, S2p (MeV)
        Q值: Q_alpha, Q_beta (MeV)
        能级: E_2plus, E_4plus, E_3minus (MeV)
        衰变: halflife, spin_parity, is_stable, decay_modes
    """
    
    # 类级别缓存数据源管理器
    _manager: Optional[DataSourceManager] = None
    
    def __init__(self, Z: int, N: int, source: str = 'experiment', data: Optional[NuclideProperties] = None):
        """
        创建核素对象
        
        参数:
            Z: 质子数
            N: 中子数
            source: 数据源 ('experiment', 'SKMS', 'UNEDF1', 等)
            data: 预加载的数据 (可选，用于优化性能)
        """
        self._Z = Z
        self._N = N
        self._source_name = source
        self._data: Optional[NuclideProperties] = data
        
        # 如果未提供数据，则加载
        if self._data is None:
            self._load_data()
    
    @classmethod
    def _get_manager(cls) -> DataSourceManager:
        """获取数据源管理器（单例）"""
        if cls._manager is None:
            cls._manager = get_data_source_manager()
        return cls._manager
    
    def _load_data(self):
        """加载核素数据"""
        manager = self._get_manager()
        try:
            source = manager.get_source(self._source_name)
            self._data = source.get_nuclide(self._Z, self._N)
        except ValueError:
            self._data = None
    
    @staticmethod
    def parse_str(s: str) -> Tuple[Optional[int], Optional[int]]:
        """
        解析核素字符串
        
        支持格式:
            - "Fe56", "Fe-56", "fe56" (元素符号+质量数)
            
        返回:
            (Z, N) 元组。如果解析失败，返回 (None, None)
        """
        s = s.strip()
        # 匹配 元素符号[-]?质量数
        match = re.match(r'^([A-Za-z]+)[-]?(\d+)$', s)
        if match:
            element = match.group(1).capitalize()
            A = int(match.group(2))
            
            # 查找质子数
            Z = None
            for atomic_num, sym in ELEMENT_SYMBOLS.items():
                if sym.lower() == element.lower():
                    Z = atomic_num
                    break
            
            if Z is not None:
                N = A - Z
                if N >= 0:
                    return Z, N
        
        return None, None

    @classmethod
    def from_symbol(cls, symbol_str: str, source: str = 'experiment') -> 'Nuclide':
        """
        从元素符号创建核素对象
        
        参数:
            symbol_str: 如 "Fe56", "Pb208", "U235"
            source: 数据源
            
        示例:
            >>> nuc = Nuclide.from_symbol("Fe56")
            >>> nuc = Nuclide.from_symbol("Pb208", source='SKMS')
        """
        Z, N = cls.parse_str(symbol_str)
        if Z is None or N is None:
            raise ValueError(f"无法解析核素符号: {symbol_str}")
        
        return cls(Z, N, source=source)
    
    # ==================== 基本属性 ====================
    
    @property
    def Z(self) -> int:
        """质子数"""
        return self._Z
    
    @property
    def N(self) -> int:
        """中子数"""
        return self._N
    
    @property
    def A(self) -> int:
        """质量数"""
        return self._Z + self._N
    
    @property
    def name(self) -> str:
        """核素名称 (如 Fe-56)"""
        symbol = ELEMENT_SYMBOLS.get(self._Z, f"X{self._Z}")
        return f"{symbol}-{self.A}"
    
    @property
    def symbol(self) -> str:
        """元素符号"""
        return ELEMENT_SYMBOLS.get(self._Z, f"X{self._Z}")
    
    @property
    def exists(self) -> bool:
        """核素是否存在于数据库中"""
        return self._data is not None
    
    @property
    def source(self) -> str:
        """数据源名称"""
        return self._source_name
    
    @property
    def data(self) -> Optional[NuclideProperties]:
        """原始数据（NuclideProperties 字典）"""
        return self._data
    
    # ==================== 结合能 ====================
    
    @property
    def BE(self) -> Optional[float]:
        """结合能 (MeV)"""
        return self._get_value('bindingEnergy')
    
    @property
    def BE_A(self) -> Optional[float]:
        """比结合能 (MeV/核子)"""
        return self._get_value('bindingEnergyPerNucleon')
    
    # ==================== 分离能 ====================
    
    @property
    def Sn(self) -> Optional[float]:
        """单中子分离能 (MeV)"""
        return self._get_value('neutronSeparationEnergy')
    
    @property
    def Sp(self) -> Optional[float]:
        """单质子分离能 (MeV)"""
        return self._get_value('protonSeparationEnergy')
    
    @property
    def S2n(self) -> Optional[float]:
        """双中子分离能 (MeV)"""
        return self._get_value('twoNeutronSeparationEnergy')
    
    @property
    def S2p(self) -> Optional[float]:
        """双质子分离能 (MeV)"""
        return self._get_value('twoProtonSeparationEnergy')
    
    # ==================== Q 值 ====================
    
    @property
    def Q_alpha(self) -> Optional[float]:
        """α衰变 Q 值 (MeV)"""
        return self._get_value('alpha')
    
    @property
    def Q_beta(self) -> Optional[float]:
        """β⁻衰变 Q 值 (MeV)"""
        return self._get_value('betaMinus')
    
    @property
    def Q_EC(self) -> Optional[float]:
        """电子俘获 Q 值 (MeV)"""
        return self._get_value('electronCapture')
    
    # ==================== 激发态能量 ====================
    
    @property
    def E_first(self) -> Optional[float]:
        """第一激发态能量 (MeV)"""
        return self._get_value('firstExcitedStateEnergy')
    
    @property
    def E_2plus(self) -> Optional[float]:
        """第一 2⁺ 态能量 (MeV)"""
        return self._get_value('firstTwoPlusEnergy')
    
    @property
    def E_4plus(self) -> Optional[float]:
        """第一 4⁺ 态能量 (MeV)"""
        return self._get_value('firstFourPlusEnergy')
    
    @property
    def E_3minus(self) -> Optional[float]:
        """第一 3⁻ 态能量 (MeV)"""
        return self._get_value('firstThreeMinusEnergy')
    
    # ==================== 衰变信息（仅实验数据）====================
    
    @property
    def halflife(self) -> Optional[str]:
        """半衰期"""
        if self._data is None:
            return None
        gs = self._data.get('ground_state')
        if gs and gs.halflife:
            val = gs.halflife.value
            unit = gs.halflife.unit
            if val == 'STABLE':
                return 'STABLE'
            return f"{val} {unit}" if unit else str(val)
        return None
    
    @property
    def spin_parity(self) -> Optional[str]:
        """自旋宇称"""
        if self._data is None:
            return None
        gs = self._data.get('ground_state')
        return gs.spin_parity if gs else None
    
    @property
    def is_stable(self) -> bool:
        """是否稳定核素"""
        hl = self.halflife
        return hl == 'STABLE' if hl else False
    
    @property
    def decay_modes(self) -> Optional[List[str]]:
        """衰变模式列表"""
        if self._data is None:
            return None
        gs = self._data.get('ground_state')
        if gs and gs.decay_modes_observed:
            return [dm.mode for dm in gs.decay_modes_observed]
        return None
    
    # ==================== 辅助方法 ====================
    
    def _get_value(self, key: str) -> Optional[float]:
        """从数据中获取数值"""
        if self._data is None:
            return None
        
        obj = self._data.get(key)
        if obj is None:
            return None
        
        if isinstance(obj, ValueWithUncertainty):
            return obj.value if isinstance(obj.value, (int, float)) else None
        if isinstance(obj, (int, float)):
            return float(obj)
        return None
    
    def get_with_uncertainty(self, key: str) -> Optional[ValueWithUncertainty]:
        """获取带不确定度的值"""
        if self._data is None:
            return None
        
        obj = self._data.get(key)
        if isinstance(obj, ValueWithUncertainty):
            return obj
        return None
    
    @staticmethod
    def list_properties() -> List[str]:
        """列出所有可用属性"""
        return [
            '=== 基本信息 ===',
            'Z          - 质子数',
            'N          - 中子数',
            'A          - 质量数',
            'name       - 核素名称 (如 Fe-56)',
            'symbol     - 元素符号',
            'exists     - 是否存在于数据库',
            'source     - 数据源名称',
            '',
            '=== 结合能 ===',
            'BE         - 结合能 (MeV)',
            'BE_A       - 比结合能 (MeV/核子)',
            '',
            '=== 分离能 ===',
            'Sn         - 单中子分离能 (MeV)',
            'Sp         - 单质子分离能 (MeV)',
            'S2n        - 双中子分离能 (MeV)',
            'S2p        - 双质子分离能 (MeV)',
            '',
            '=== Q 值 ===',
            'Q_alpha    - α衰变 Q 值 (MeV)',
            'Q_beta     - β⁻衰变 Q 值 (MeV)',
            'Q_EC       - 电子俘获 Q 值 (MeV)',
            '',
            '=== 激发态能量 ===',
            'E_first    - 第一激发态 (MeV)',
            'E_2plus    - 第一 2⁺ 态 (MeV)',
            'E_4plus    - 第一 4⁺ 态 (MeV)',
            'E_3minus   - 第一 3⁻ 态 (MeV)',
            '',
            '=== 衰变信息（仅实验数据）===',
            'halflife   - 半衰期',
            'spin_parity - 自旋宇称',
            'is_stable  - 是否稳定',
            'decay_modes - 衰变模式列表',
        ]
    
    def __repr__(self) -> str:
        status = '✓' if self.exists else '✗'
        return f"Nuclide({self.name}, source='{self._source_name}', exists={status})"
    
    def __str__(self) -> str:
        return self.name
