import json
from typing import Dict, List, Optional
from collections import defaultdict
import numpy as np
from pathlib import Path
from nuclide_data import (
    DecayModeInfo,
    HalfLifeInfo,
    ELEMENT_SYMBOLS,
    HALF_LIFE_UNITS,
    NuclideProperties,
    ValueWithUncertainty,
    DecayModeInfo,
    LevelInfo
)
from config import QueryConfig, DATA_FILE_PATH

class NuclideDataLoader:
    """从本地JSON文件加载核素数据的类"""
    
    def __init__(self, data_file: Optional[str] = None, query_config: QueryConfig = QueryConfig()):
        """
        初始化数据加载器
        
        参数:
            data_file: JSON数据文件路径，默认使用配置文件中的路径
            query_config: 查询配置名称
        """
        if data_file is None:
            data_file = DATA_FILE_PATH
        
        self.data_file = Path(data_file)
        self.query_config = query_config
        
        # 核素数据存储结构 - 使用 NuclideProperties
        self.nuclide_data: Dict[tuple, NuclideProperties] = {}
        
        # 初始化常用数据
        self._init_common_data()
        
        # 加载数据
        self._load_all_data()
    
    def _init_common_data(self):
        """初始化常用核数据(如元素符号)"""
        self.element_symbols = ELEMENT_SYMBOLS
    
    def _load_all_data(self):
        """加载所有核素数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for nuclide_name, nuclide_data_temp in data.items():
                # 跳过没有基本信息的条目
                if not isinstance(nuclide_data_temp, dict):
                    continue
                    
                Z = nuclide_data_temp['z']
                N = nuclide_data_temp['n']
                A = nuclide_data_temp['a']
                
                # 处理能级信息
                levels = []
                ground_state = None
                if 'levels' in nuclide_data_temp and nuclide_data_temp['levels']:
                    for level_data in nuclide_data_temp['levels']:
                        level_info = self._parse_level_info(level_data)
                        levels.append(level_info)
                        if level_info.energy.value == 0:  # 基态
                            ground_state = level_info

                # 创建完整的核素属性对象，直接使用JSON字段名
                nuclide_props: NuclideProperties = {
                    # 必需字段
                    'Z': Z,
                    'N': N,
                    'A': A,
                    'name': nuclide_data_temp.get('name', nuclide_name),
                    'symbol': ELEMENT_SYMBOLS.get(Z, f"X{Z}"),
                    
                    # 可选字段 - 能级信息
                    'levels': levels,
                    'ground_state': ground_state,
                    
                    # 结合能
                    'bindingEnergy': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('bindingEnergy')
                    )*A,
                    'bindingEnergyPerNucleon': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('bindingEnergy')
                    ),
                    'bindingEnergyLDMFit': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('bindingEnergyLDMFit')
                    ),

                    # 分离能
                    'neutronSeparationEnergy': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('neutronSeparationEnergy')
                    ),
                    'protonSeparationEnergy': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('protonSeparationEnergy')
                    ),
                    'twoNeutronSeparationEnergy': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('twoNeutronSeparationEnergy')
                    ),
                    'twoProtonSeparationEnergy': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('twoProtonSeparationEnergy')
                    ),

                    # 结构信息（导出量）
                    'pairingGap': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('pairingGap')
                    ),
                    'quadrupoleDeformation': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('quadrupoleDeformation')
                    ),

                    # 衰变相关Q值
                    'alpha': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('alpha')
                        ),
                    'deltaAlpha': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('deltaAlpha')
                        ),
                    'betaMinus': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('betaMinus')
                        ),
                    'electronCapture': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('electronCapture')
                        ),
                    'positronEmission': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('positronEmission')
                        ),
                    'betaMinusOneNeutronEmission': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('betaMinusOneNeutronEmission')
                        ),
                    'betaMinusTwoNeutronEmission': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('betaMinusTwoNeutronEmission')
                        ),
                    'electronCaptureOneProtonEmission': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('electronCaptureOneProtonEmission')
                        ),
                    'doubleBetaMinus': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('doubleBetaMinus')
                        ),
                    'doubleElectronCapture': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('doubleElectronCapture')
                        ),
                    
                    # 激发态能量
                    'firstExcitedStateEnergy': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('firstExcitedStateEnergy')
                    ),
                    'firstTwoPlusEnergy': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('firstTwoPlusEnergy')
                    ),
                    'firstFourPlusEnergy': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('firstFourPlusEnergy')
                    ),
                    'firstFourPlusOverFirstTwoPlusEnergy': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('firstFourPlusOverFirstTwoPlusEnergy')
                    ),
                    'firstThreeMinusEnergy': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('firstThreeMinusEnergy')
                    ),
                    
                    
                    'BE4DBE2': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('BE4DBE2')
                    ),
                    
                    # 核裂变产额
                    'FY235U': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('FY235U')
                    ),
                    'FY238U': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('FY238U')
                    ),
                    'FY239Pu': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('FY239Pu')
                    ),
                    'FY252Cf': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('FY252Cf')
                    ),
                    'cFY235U': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('cFY235U')
                    ),
                    'cFY238U': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('cFY238U')
                    ),
                    'cFY239Pu': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('cFY239Pu')
                    ),
                    'cFY252Cf': self._parse_value_with_uncertainty(
                        nuclide_data_temp.get('cFY252Cf')
                    ),

                    # 核反应数据（如果需要，基于实际JSON添加）
                    'thermal_neutron_capture': self._parse_thermal_neutron_capture(
                        nuclide_data_temp.get('thermalNeutronCapture')
                    ),
                }
                
                # 存储数据
                self.nuclide_data[(Z, N)] = nuclide_props
            
        except Exception as e:
            print(f"加载数据文件失败: {e}")
            raise  # 重新抛出异常，以便更好地诊断问题
    
    def _parse_value_with_uncertainty(self, data) -> ValueWithUncertainty:
        """解析带不确定度的数值"""
        if not data or not isinstance(data, dict):
            return ValueWithUncertainty(None, None, '')
        
        value = data.get('value')
        uncertainty = data.get('uncertainty', 0.0)
        unit = data.get('unit', '')
        
        if value is None:
            return ValueWithUncertainty(None, None, unit or '')
        
        # 确保uncertainty不是None
        if uncertainty is None:
            uncertainty = 0.0
            
        scale = 1.0
        if unit == 'keV':
            scale = 1e-3
            unit = 'MeV'  # 将keV转换为MeV
        elif unit is None:
            unit = ''

        return ValueWithUncertainty(
            value=float(value) * scale,
            uncertainty=float(uncertainty) * scale,
            unit=unit
        )
    
    def _parse_level_info(self, level_data: Dict) -> LevelInfo:
        """解析能级信息"""
        energy = self._parse_value_with_uncertainty(
            level_data.get('energy')
        )
        
        mass_excess = self._parse_value_with_uncertainty(
            level_data.get('massExcess')
        )
        
        # 解析半衰期
        halflife = None
        if 'halflife' in level_data:
            hl_data = level_data['halflife']
            if isinstance(hl_data, dict):
                if hl_data.get('value') == "STABLE":
                    halflife = HalfLifeInfo("STABLE", None, "")
                else:
                    value = hl_data.get('value', 0.0)
                    unit = hl_data.get('unit', 's')
                    uncertainty = hl_data.get('uncertainty', 0.0)
                    halflife = HalfLifeInfo(value, uncertainty, unit)
        
        # 解析衰变模式
        decay_modes_observed = []
        decay_modes_predicted = []
        
        if 'decayModes' in level_data:
            dm = level_data['decayModes']
            
            if 'observed' in dm:
                for decay in dm['observed']:
                    mode_info = DecayModeInfo(
                        mode=decay.get('mode', ''),
                        value=decay.get('value', 0.0),
                        uncertainty=decay.get('uncertainty', 0.0)
                    )
                    decay_modes_observed.append(mode_info)
            
            if 'predicted' in dm:
                for decay in dm['predicted']:
                    mode_info = DecayModeInfo(
                        mode=decay.get('mode', ''),
                        value=decay.get('value', 0.0),
                        uncertainty=decay.get('uncertainty', 0.0)
                    )
                    decay_modes_predicted.append(mode_info)
        
        return LevelInfo(
            energy=energy,
            mass_excess=mass_excess,
            spin_parity=level_data.get('spinParity'),
            halflife=halflife,
            decay_modes_observed=decay_modes_observed,
            decay_modes_predicted=decay_modes_predicted
        )
    
    def _parse_thermal_neutron_capture(self, data) -> Optional[ValueWithUncertainty]:
        """解析热中子俘获截面"""
        if not data or not isinstance(data, dict):
            return None
        
        value = data.get('crossSection')
        uncertainty = data.get('uncertainty', 0.0)
        
        if value is None:
            return None
            
        return ValueWithUncertainty(
            value=float(value),
            uncertainty=float(uncertainty),
            unit="barn"
        )
    
    def _check_magic_numbers(self, Z: int, N: int) -> List[str]:
        """检查是否为幻数"""
        magic_numbers = []
        magic_values = [2, 8, 20, 28, 50, 82, 126]
        
        if Z in magic_values:
            magic_numbers.append(f"Z={Z}")
        if N in magic_values:
            magic_numbers.append(f"N={N}")
        
        return magic_numbers
    
    def get_nuclide_data(self, Z: int, N: int) -> Optional[NuclideProperties]:
        """获取特定核素的数据"""
        data = self.nuclide_data.get((Z, N))
        if not data:
            pass # print(f"未找到核素数据: Z={Z}, N={N}")
        return data
    
    def get_isotope_chain(self, Z: int) -> List[NuclideProperties]:
        """获取特定元素的所有同位素数据"""
        return [data for (z, n), data in self.nuclide_data.items() if z == Z]
