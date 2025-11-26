#!/usr/bin/env python3
"""
数据源抽象层
定义统一的数据源接口，支持实验数据和理论计算数据
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass

from .nuclide_data import (
    ValueWithUncertainty, NuclideProperties, LevelInfo, DecayModeInfo,
    ELEMENT_SYMBOLS, HALF_LIFE_UNITS
)


# ==================== 数据源基类 ====================

class DataSource(ABC):
    """数据源抽象基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """数据源名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """数据源描述"""
        pass
    
    @property
    def is_theoretical(self) -> bool:
        """是否为理论数据"""
        return False
    
    @abstractmethod
    def get_nuclide(self, Z: int, N: int) -> Optional[NuclideProperties]:
        """
        获取核素数据
        
        参数:
            Z: 质子数
            N: 中子数
            
        返回:
            NuclideProperties 或 None
        """
        pass
    
    @abstractmethod
    def has_nuclide(self, Z: int, N: int) -> bool:
        """检查核素是否存在"""
        pass
    
    @abstractmethod
    def list_nuclides(self) -> List[Tuple[int, int]]:
        """列出所有可用核素的 (Z, N) 列表"""
        pass
    
    def get_isotopes(self, Z: int) -> List[NuclideProperties]:
        """
        获取指定质子数的所有同位素数据
        默认实现：遍历 list_nuclides 进行筛选（子类可优化）
        """
        results = []
        for z, n in self.list_nuclides():
            if z == Z:
                data = self.get_nuclide(z, n)
                if data:
                    results.append(data)
        # 按中子数排序
        results.sort(key=lambda x: x['N'])
        return results

    def get_isotones(self, N: int) -> List[NuclideProperties]:
        """
        获取指定中子数的所有同中子素数据
        默认实现：遍历 list_nuclides 进行筛选
        """
        results = []
        for z, n in self.list_nuclides():
            if n == N:
                data = self.get_nuclide(z, n)
                if data:
                    results.append(data)
        # 按质子数排序
        results.sort(key=lambda x: x['Z'])
        return results



# ==================== 实验数据源 ====================

class ExperimentalDataSource(DataSource):
    """
    NNDC 实验数据源
    
    数据来源: NNDC NuDat 数据库
    包含结合能、分离能、半衰期、衰变模式等完整实验数据
    """
    
    def __init__(self, data_file: Optional[str] = None):
        if data_file is None:
            self.data_file = Path(__file__).parent / 'data' / 'nndc_nudat_data_export.json'
        else:
            self.data_file = Path(data_file)
        
        # 数据缓存
        self._data: Dict[Tuple[int, int], NuclideProperties] = {}
        self._loaded = False
    
    @property
    def name(self) -> str:
        return "experiment"
    
    @property
    def description(self) -> str:
        return "NNDC NuDat 实验数据"
    
    @property
    def is_theoretical(self) -> bool:
        return False
    
    def _ensure_loaded(self):
        """确保数据已加载"""
        if not self._loaded:
            self._load_data()
            self._loaded = True
    
    def _load_data(self):
        """加载 JSON 数据"""
        if not self.data_file.exists():
            raise FileNotFoundError(f"数据文件不存在: {self.data_file}")
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        for nuclide_name, nuclide_dict in raw_data.items():
            if not isinstance(nuclide_dict, dict):
                continue
            
            Z = nuclide_dict.get('z')
            N = nuclide_dict.get('n')
            A = nuclide_dict.get('a')
            
            if Z is None or N is None:
                continue
            
            # 解析能级信息
            levels = []
            ground_state = None
            if 'levels' in nuclide_dict and nuclide_dict['levels']:
                for level_data in nuclide_dict['levels']:
                    level_info = self._parse_level_info(level_data)
                    levels.append(level_info)
                    if level_info.energy.value == 0:
                        ground_state = level_info
            
            # 构建 NuclideProperties
            # 注意：原始数据单位是 keV，需要除以 1000 转换为 MeV
            be_per_nucleon = self._parse_value_mev(nuclide_dict.get('bindingEnergy'))
            
            props: NuclideProperties = {
                'Z': Z,
                'N': N,
                'A': A,
                'name': nuclide_dict.get('name', nuclide_name),
                'symbol': ELEMENT_SYMBOLS.get(Z, f"X{Z}"),
                'levels': levels,
                'ground_state': ground_state,
                
                # 结合能 (keV -> MeV)
                'bindingEnergy': self._multiply_value(be_per_nucleon, A),
                'bindingEnergyPerNucleon': be_per_nucleon,
                
                # 分离能 (keV -> MeV)
                'neutronSeparationEnergy': self._parse_value_mev(nuclide_dict.get('neutronSeparationEnergy')),
                'protonSeparationEnergy': self._parse_value_mev(nuclide_dict.get('protonSeparationEnergy')),
                'twoNeutronSeparationEnergy': self._parse_value_mev(nuclide_dict.get('twoNeutronSeparationEnergy')),
                'twoProtonSeparationEnergy': self._parse_value_mev(nuclide_dict.get('twoProtonSeparationEnergy')),
                
                # Q 值 (keV -> MeV)
                'alpha': self._parse_value_mev(nuclide_dict.get('alpha')),
                'betaMinus': self._parse_value_mev(nuclide_dict.get('betaMinus')),
                'electronCapture': self._parse_value_mev(nuclide_dict.get('electronCapture')),
                
                # 激发态能量 (keV -> MeV)
                'firstExcitedStateEnergy': self._parse_value_mev(nuclide_dict.get('firstExcitedStateEnergy')),
                'firstTwoPlusEnergy': self._parse_value_mev(nuclide_dict.get('firstTwoPlusEnergy')),
                'firstFourPlusEnergy': self._parse_value_mev(nuclide_dict.get('firstFourPlusEnergy')),
                'firstThreeMinusEnergy': self._parse_value_mev(nuclide_dict.get('firstThreeMinusEnergy')),
                
                # 裂变产额
                'FY235U': self._parse_value(nuclide_dict.get('FY235U')),
                'FY238U': self._parse_value(nuclide_dict.get('FY238U')),
                'FY239Pu': self._parse_value(nuclide_dict.get('FY239Pu')),
                'FY252Cf': self._parse_value(nuclide_dict.get('FY252Cf')),
                'cFY235U': self._parse_value(nuclide_dict.get('cFY235U')),
                'cFY238U': self._parse_value(nuclide_dict.get('cFY238U')),
                'cFY239Pu': self._parse_value(nuclide_dict.get('cFY239Pu')),
                'cFY252Cf': self._parse_value(nuclide_dict.get('cFY252Cf')),
            }
            
            self._data[(Z, N)] = props
    
    def _parse_value(self, data) -> Optional[ValueWithUncertainty]:
        """解析带不确定度的值（保持原单位）"""
        if data is None:
            return None
        if isinstance(data, dict):
            return ValueWithUncertainty(
                value=data.get('value'),
                uncertainty=data.get('uncertainty'),
                unit=data.get('unit', '')
            )
        if isinstance(data, (int, float)):
            return ValueWithUncertainty(value=float(data), unit='')
        return None
    
    def _parse_value_mev(self, data) -> Optional[ValueWithUncertainty]:
        """解析带不确定度的值，并从 keV 转换为 MeV"""
        if data is None:
            return None
        if isinstance(data, dict):
            val = data.get('value')
            unc = data.get('uncertainty')
            return ValueWithUncertainty(
                value=val / 1000.0 if isinstance(val, (int, float)) else None,
                uncertainty=unc / 1000.0 if isinstance(unc, (int, float)) else None,
                unit='MeV'
            )
        if isinstance(data, (int, float)):
            return ValueWithUncertainty(value=float(data) / 1000.0, unit='MeV')
        return None
    
    def _multiply_value(self, val: Optional[ValueWithUncertainty], factor: int) -> Optional[ValueWithUncertainty]:
        """将 ValueWithUncertainty 乘以一个因子"""
        if val is None or val.value is None:
            return None
        return ValueWithUncertainty(
            value=val.value * factor,
            uncertainty=val.uncertainty * factor if val.uncertainty else None,
            unit=val.unit
        )
    
    def _parse_level_info(self, level_data: dict) -> LevelInfo:
        """解析能级信息"""
        energy = self._parse_value(level_data.get('energy')) or ValueWithUncertainty(value=0)
        mass_excess = self._parse_value(level_data.get('massExcess')) or ValueWithUncertainty()
        
        # 解析衰变模式
        decay_modes = []
        if 'decayModesObserved' in level_data and level_data['decayModesObserved']:
            for dm in level_data['decayModesObserved']:
                decay_modes.append(DecayModeInfo(
                    mode=dm.get('mode', ''),
                    value=dm.get('value'),
                    uncertainty=dm.get('uncertainty'),
                    unit=dm.get('unit', '%')
                ))
        
        return LevelInfo(
            energy=energy,
            mass_excess=mass_excess,
            spin_parity=level_data.get('spinParity'),
            halflife=self._parse_value(level_data.get('halflife')),
            decay_modes_observed=decay_modes if decay_modes else None
        )
    
    def get_nuclide(self, Z: int, N: int) -> Optional[NuclideProperties]:
        self._ensure_loaded()
        return self._data.get((Z, N))
    
    def has_nuclide(self, Z: int, N: int) -> bool:
        self._ensure_loaded()
        return (Z, N) in self._data
    
    def list_nuclides(self) -> List[Tuple[int, int]]:
        self._ensure_loaded()
        return list(self._data.keys())


# ==================== 理论数据源 ====================

class TheoreticalDataSource(DataSource):
    """
    DFT 理论计算数据源
    
    支持: SKMS, UNEDF0, UNEDF1, SLY4, SKP, SV-MIN
    """
    
    # 可用的理论数据源配置
    SOURCES = {
        'SKMS': ('SKMS_all_nuclei-new.dat', 'SkM* 能量密度泛函'),
        'UNEDF0': ('UNEDF0_all_nuclei.dat', 'UNEDF0 能量密度泛函'),
        'UNEDF1': ('UNEDF1_all_nuclei.dat', 'UNEDF1 能量密度泛函'),
        'SLY4': ('SLY4_all_nuclei.dat', 'Skyrme SLy4 泛函'),
        'SKP': ('SKP_all_nuclei.dat', 'Skyrme SKP 泛函'),
        'SV-MIN': ('SV-MIN_all_nuclei.dat', 'SV-min 泛函'),
    }
    
    def __init__(self, source_name: str, data_dir: Optional[str] = None):
        """
        初始化理论数据源
        
        参数:
            source_name: 数据源名称 (SKMS, UNEDF1, 等)
            data_dir: 数据文件目录
        """
        source_name = source_name.upper()
        if source_name not in self.SOURCES:
            raise ValueError(f"未知数据源: {source_name}，可用: {list(self.SOURCES.keys())}")
        
        self._source_name = source_name
        self._filename, self._description = self.SOURCES[source_name]
        
        if data_dir is None:
            self.data_dir = Path(__file__).parent / 'data'
        else:
            self.data_dir = Path(data_dir)
        
        # 数据缓存
        self._data: Dict[Tuple[int, int], NuclideProperties] = {}
        self._loaded = False
    
    @property
    def name(self) -> str:
        return self._source_name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def is_theoretical(self) -> bool:
        return True
    
    @classmethod
    def list_available_sources(cls, data_dir: Optional[str] = None) -> List[str]:
        """列出所有可用的理论数据源"""
        if data_dir is None:
            path_obj = Path(__file__).parent / 'data'
        else:
            path_obj = Path(data_dir)
        
        available = []
        for name, (filename, _) in cls.SOURCES.items():
            if (path_obj / filename).exists():
                available.append(name)
        return available
    
    def _ensure_loaded(self):
        """确保数据已加载"""
        if not self._loaded:
            self._load_data()
            self._loaded = True
    
    def _load_data(self):
        """加载数据文件"""
        filepath = self.data_dir / self._filename
        if not filepath.exists():
            raise FileNotFoundError(f"数据文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            # 跳过表头
            header = f.readline()
            
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) < 10:
                    continue
                
                try:
                    symbol = parts[0]
                    Z = int(parts[1])
                    N = int(parts[2])
                    A = int(parts[3])
                    
                    # 解析能量值
                    BE = self._parse_float(parts[4])
                    Sp = self._parse_float(parts[5])
                    S2p = self._parse_float(parts[6])
                    Sn = self._parse_float(parts[7])
                    S2n = self._parse_float(parts[8])
                    Q_alpha = self._parse_float(parts[9])
                    
                    # 理论数据的结合能是负值，取绝对值
                    if BE is not None:
                        BE = abs(BE)
                    
                    # 构建 NuclideProperties
                    props: NuclideProperties = {
                        'Z': Z,
                        'N': N,
                        'A': A,
                        'name': f"{A}{symbol}",
                        'symbol': symbol,
                        
                        # 结合能
                        'bindingEnergy': ValueWithUncertainty(value=BE, unit='MeV') if BE else None,
                        'bindingEnergyPerNucleon': ValueWithUncertainty(value=BE/A, unit='MeV') if BE and A > 0 else None,
                        
                        # 分离能
                        'neutronSeparationEnergy': ValueWithUncertainty(value=Sn, unit='MeV') if Sn else None,
                        'protonSeparationEnergy': ValueWithUncertainty(value=Sp, unit='MeV') if Sp else None,
                        'twoNeutronSeparationEnergy': ValueWithUncertainty(value=S2n, unit='MeV') if S2n else None,
                        'twoProtonSeparationEnergy': ValueWithUncertainty(value=S2p, unit='MeV') if S2p else None,
                        
                        # Q 值
                        'alpha': ValueWithUncertainty(value=Q_alpha, unit='MeV') if Q_alpha else None,
                    }
                    
                    self._data[(Z, N)] = props
                    
                except (ValueError, IndexError):
                    continue
    
    def _parse_float(self, value_str: str) -> Optional[float]:
        """解析浮点数"""
        value_str = value_str.strip()
        if value_str == 'No_Data' or value_str == '':
            return None
        try:
            return float(value_str)
        except ValueError:
            return None
    
    def get_nuclide(self, Z: int, N: int) -> Optional[NuclideProperties]:
        self._ensure_loaded()
        return self._data.get((Z, N))
    
    def has_nuclide(self, Z: int, N: int) -> bool:
        self._ensure_loaded()
        return (Z, N) in self._data
    
    def list_nuclides(self) -> List[Tuple[int, int]]:
        self._ensure_loaded()
        return list(self._data.keys())


# ==================== 数据源管理器 ====================

class DataSourceManager:
    """
    数据源管理器
    
    统一管理和访问多个数据源
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / 'data'
        self._sources: Dict[str, DataSource] = {}
        
        # 自动注册实验数据源
        self._register_experimental_source()
    
    def _register_experimental_source(self):
        """注册实验数据源"""
        try:
            exp_source = ExperimentalDataSource(str(self.data_dir / 'nndc_nudat_data_export.json'))
            self._sources['experiment'] = exp_source
        except FileNotFoundError:
            pass
    
    def get_source(self, name: str) -> DataSource:
        """
        获取数据源
        
        参数:
            name: 数据源名称 (experiment, SKMS, UNEDF1, 等)
            
        返回:
            DataSource 实例
        """
        name_lower = name.lower()
        
        # 检查是否已缓存
        if name_lower in self._sources:
            return self._sources[name_lower]
        if name.upper() in self._sources:
            return self._sources[name.upper()]
        
        # 实验数据
        if name_lower in ('experiment', 'exp', 'nndc'):
            if 'experiment' not in self._sources:
                self._sources['experiment'] = ExperimentalDataSource(
                    str(self.data_dir / 'nndc_nudat_data_export.json')
                )
            return self._sources['experiment']
        
        # 理论数据
        source_name = name.upper()
        if source_name in TheoreticalDataSource.SOURCES:
            if source_name not in self._sources:
                self._sources[source_name] = TheoreticalDataSource(source_name, str(self.data_dir))
            return self._sources[source_name]
        
        raise ValueError(f"未知数据源: {name}，可用: {self.list_sources()}")
    
    def list_sources(self) -> List[str]:
        """列出所有可用数据源"""
        sources = ['experiment']
        sources.extend(TheoreticalDataSource.list_available_sources(str(self.data_dir)))
        return sources
    
    def get_nuclide(self, Z: int, N: int, source: str = 'experiment') -> Optional[NuclideProperties]:
        """从指定数据源获取核素数据"""
        return self.get_source(source).get_nuclide(Z, N)
    
    def compare_sources(self, Z: int, N: int, 
                       sources: Optional[List[str]] = None) -> Dict[str, Optional[NuclideProperties]]:
        """
        比较多个数据源的核素数据
        
        返回:
            {source_name: NuclideProperties} 字典
        """
        if sources is None:
            sources = self.list_sources()
        
        result = {}
        for src in sources:
            try:
                result[src] = self.get_source(src).get_nuclide(Z, N)
            except ValueError:
                result[src] = None
        return result


# ==================== 全局单例 ====================

_default_manager: Optional[DataSourceManager] = None

def get_data_source_manager() -> DataSourceManager:
    """获取默认数据源管理器"""
    global _default_manager
    if _default_manager is None:
        _default_manager = DataSourceManager()
    return _default_manager


def get_source(name: str) -> DataSource:
    """快捷函数：获取数据源"""
    return get_data_source_manager().get_source(name)


def list_sources() -> List[str]:
    """快捷函数：列出所有数据源"""
    return get_data_source_manager().list_sources()
