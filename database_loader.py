import json
from typing import Dict, List, Optional
from collections import defaultdict
import numpy as np
from pathlib import Path
from nuclide_data import (
    DecayMode, 
    ELEMENT_SYMBOLS,
    HALF_LIFE_UNITS,
    NuclideProperties,
    ValueWithUncertainty,
    HalfLifeInfo,
    DecayModeInfo,
    LevelInfo,
    QueryConfig,
    load_query_config
)
import config

class NuclideDataLoader:
    """从本地JSON文件加载核素数据的类"""
    
    def __init__(self, data_file: Optional[str] = None, query_config: str = "basic"):
        """
        初始化数据加载器
        
        参数:
            data_file: JSON数据文件路径，默认使用配置文件中的路径
            query_config: 查询配置名称
        """
        if data_file is None:
            data_file = config.DATA_FILE_PATH
        
        self.data_file = Path(data_file)
        self.query_config = load_query_config(query_config)
        
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
            
            for nuclide_name, nuclide_data in data.items():
                # 跳过没有基本信息的条目
                if not isinstance(nuclide_data, dict):
                    continue
                    
                Z = nuclide_data['z']
                N = nuclide_data['n']
                A = nuclide_data['a']
                
                # 处理能级信息
                levels = []
                ground_state = None
                if 'levels' in nuclide_data and nuclide_data['levels']:
                    for level_data in nuclide_data['levels']:
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
                    'name': nuclide_data.get('name', nuclide_name),
                    'symbol': ELEMENT_SYMBOLS.get(Z, f"X{Z}"),
                    
                    # 可选字段 - 能级信息
                    'levels': levels,
                    'ground_state': ground_state,
                    
                    # 直接存储JSON原始字段，保持字段名一致
                    'bindingEnergy': self._parse_value_with_uncertainty(
                        nuclide_data.get('bindingEnergy'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'bindingEnergyLDMFit': self._parse_value_with_uncertainty(
                        nuclide_data.get('bindingEnergyLDMFit'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'neutronSeparationEnergy': self._parse_value_with_uncertainty(
                        nuclide_data.get('neutronSeparationEnergy'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'protonSeparationEnergy': self._parse_value_with_uncertainty(
                        nuclide_data.get('protonSeparationEnergy'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'twoNeutronSeparationEnergy': self._parse_value_with_uncertainty(
                        nuclide_data.get('twoNeutronSeparationEnergy'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'twoProtonSeparationEnergy': self._parse_value_with_uncertainty(
                        nuclide_data.get('twoProtonSeparationEnergy'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'alpha': self._parse_value_with_uncertainty(
                        nuclide_data.get('alpha'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'deltaAlpha': self._parse_value_with_uncertainty(
                        nuclide_data.get('deltaAlpha'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'betaMinus': self._parse_value_with_uncertainty(
                        nuclide_data.get('betaMinus'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'electronCapture': self._parse_value_with_uncertainty(
                        nuclide_data.get('electronCapture'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'positronEmission': self._parse_value_with_uncertainty(
                        nuclide_data.get('positronEmission'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'pairingGap': self._parse_value_with_uncertainty(
                        nuclide_data.get('pairingGap'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'quadrupoleDeformation': self._parse_value_with_uncertainty(
                        nuclide_data.get('quadrupoleDeformation')  # 四极形变是无量纲的，不需要转换
                        ) or ValueWithUncertainty(0.0, 0.0, ""),
                    'betaMinusOneNeutronEmission': self._parse_value_with_uncertainty(
                        nuclide_data.get('betaMinusOneNeutronEmission'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'betaMinusTwoNeutronEmission': self._parse_value_with_uncertainty(
                        nuclide_data.get('betaMinusTwoNeutronEmission'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'electronCaptureOneProtonEmission': self._parse_value_with_uncertainty(
                        nuclide_data.get('electronCaptureOneProtonEmission'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'doubleBetaMinus': self._parse_value_with_uncertainty(
                        nuclide_data.get('doubleBetaMinus'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'doubleElectronCapture': self._parse_value_with_uncertainty(
                        nuclide_data.get('doubleElectronCapture'), scale=1e-3 # 将keV转换为MeV
                        ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'firstExcitedStateEnergy': self._parse_value_with_uncertainty(
                        nuclide_data.get('firstExcitedStateEnergy'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'firstTwoPlusEnergy': self._parse_value_with_uncertainty(
                        nuclide_data.get('firstTwoPlusEnergy'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'firstFourPlusEnergy': self._parse_value_with_uncertainty(
                        nuclide_data.get('firstFourPlusEnergy'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'firstFourPlusOverFirstTwoPlusEnergy': self._parse_value_with_uncertainty(
                        nuclide_data.get('firstFourPlusOverFirstTwoPlusEnergy'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'firstThreeMinusEnergy': self._parse_value_with_uncertainty(
                        nuclide_data.get('firstThreeMinusEnergy'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'BE4DBE2': self._parse_value_with_uncertainty(
                        nuclide_data.get('BE4DBE2'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'FY235U': self._parse_value_with_uncertainty(
                        nuclide_data.get('FY235U'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'FY238U': self._parse_value_with_uncertainty(
                        nuclide_data.get('FY238U'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'FY239Pu': self._parse_value_with_uncertainty(
                        nuclide_data.get('FY239Pu'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'FY252Cf': self._parse_value_with_uncertainty(
                        nuclide_data.get('FY252Cf'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'cFY235U': self._parse_value_with_uncertainty(
                        nuclide_data.get('cFY235U'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'cFY238U': self._parse_value_with_uncertainty(
                        nuclide_data.get('cFY238U'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'cFY239Pu': self._parse_value_with_uncertainty(
                        nuclide_data.get('cFY239Pu'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),
                    'cFY252Cf': self._parse_value_with_uncertainty(
                        nuclide_data.get('cFY252Cf'), scale=1e-3 # 将keV转换为MeV
                    ) or ValueWithUncertainty(0.0, 0.0, "MeV"),

                    # 核反应数据（如果需要，基于实际JSON添加）
                    'thermal_neutron_capture': self._parse_thermal_neutron_capture(
                        nuclide_data.get('thermalNeutronCapture')
                    ),
                }
                
                # 存储数据
                self.nuclide_data[(Z, N)] = nuclide_props
            
        except Exception as e:
            print(f"加载数据文件失败: {e}")
            raise  # 重新抛出异常，以便更好地诊断问题
    
    def _determine_decay_mode_from_nndc(self, nuclide_data: Dict) -> DecayMode:
        """从NNDC数据格式确定衰变模式"""
        # 检查是否有衰变信息
        if 'levels' in nuclide_data and nuclide_data['levels']:
            level = nuclide_data['levels'][0]  # 取基态
            
            # 检查半衰期，如果是稳定的
            if 'halflife' in level:
                halflife = level['halflife']
                if isinstance(halflife, dict) and halflife.get('value') == "STABLE":
                    return DecayMode.STABLE
                    
                # 检查衰变模式
                if 'decayModes' in level and 'observed' in level['decayModes']:
                    for decay in level['decayModes']['observed']:
                        mode = decay.get('mode', '')
                        if mode == 'B-':
                            return DecayMode.BETA_MINUS
                        elif mode == 'B+' or mode == 'EC':
                            return DecayMode.BETA_PLUS
                        elif mode == 'A':
                            return DecayMode.ALPHA
                        elif mode == 'N':
                            return DecayMode.NEUTRON_EMISSION
                        elif mode == 'P':
                            return DecayMode.PROTON_EMISSION
        
        # 根据分离能判断衰变模式（备用方法）
        neutron_sep = 0.0
        proton_sep = 0.0
        two_neutron_sep = 0.0
        two_proton_sep = 0.0
        
        if 'neutronSeparationEnergy' in nuclide_data:
            neutron_sep = nuclide_data['neutronSeparationEnergy'].get('value', 0.0) / 1000.0  # keV to MeV
        if 'protonSeparationEnergy' in nuclide_data:
            proton_sep = nuclide_data['protonSeparationEnergy'].get('value', 0.0) / 1000.0  # keV to MeV
        if 'twoNeutronSeparationEnergy' in nuclide_data:
            two_neutron_sep = nuclide_data['twoNeutronSeparationEnergy'].get('value', 0.0) / 1000.0  # keV to MeV
        if 'twoProtonSeparationEnergy' in nuclide_data:
            two_proton_sep = nuclide_data['twoProtonSeparationEnergy'].get('value', 0.0) / 1000.0  # keV to MeV
        
        if neutron_sep < 0:  # 中子分离能为负，可能发生中子发射
            return DecayMode.NEUTRON_EMISSION
        elif proton_sep < 0:  # 质子分离能为负，可能发生质子发射
            return DecayMode.PROTON_EMISSION
        elif two_neutron_sep < 0:  # 双中子分离能为负，可能发生双中子发射
            return DecayMode.NEUTRON_EMISSION
        elif two_proton_sep < 0:  # 双质子分离能为负，可能发生双质子发射
            return DecayMode.PROTON_EMISSION
        
        # 默认返回未知
        return DecayMode.UNKNOWN
    
    def _parse_value_with_uncertainty(self, data, scale=1.0) -> Optional[ValueWithUncertainty]:
        """解析带不确定度的数值"""
        if not data or not isinstance(data, dict):
            return None
        
        value = data.get('value')
        uncertainty = data.get('uncertainty', 0.0)
        unit = data.get('unit', '')
        
        if value is None:
            return None
        
        # 确保uncertainty不是None
        if uncertainty is None:
            uncertainty = 0.0
            
        return ValueWithUncertainty(
            value=float(value) * scale,
            uncertainty=float(uncertainty) * scale,
            unit=unit
        )
    
    def _parse_level_info(self, level_data: Dict) -> LevelInfo:
        """解析能级信息"""
        energy = self._parse_value_with_uncertainty(
            level_data.get('energy'), scale=1e-3  # keV to MeV
        ) or ValueWithUncertainty(0.0, 0.0, "MeV")
        
        mass_excess = self._parse_value_with_uncertainty(
            level_data.get('massExcess'), scale=1e-3  # keV to MeV
        ) or ValueWithUncertainty(0.0, 0.0, "MeV")
        
        # 解析半衰期
        halflife = None
        if 'halflife' in level_data:
            hl_data = level_data['halflife']
            if isinstance(hl_data, dict):
                if hl_data.get('value') == "STABLE":
                    halflife = HalfLifeInfo("STABLE", "", 0.0)
                else:
                    value = hl_data.get('value', 0.0)
                    unit = hl_data.get('unit', 's')
                    uncertainty = hl_data.get('uncertainty', 0.0)
                    halflife = HalfLifeInfo(value, unit, uncertainty)
        
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
    
    def get_decay_path(self, Z: int, N: int) -> List[NuclideProperties]:
        """获取核素的衰变路径"""
        path = []
        current = (Z, N)
        
        while current in self.nuclide_data:
            data = self.nuclide_data[current]
            path.append(data)
            
            # 根据衰变模式确定下一个核素
            decay_mode = data.get('decay_mode')
            if decay_mode == DecayMode.ALPHA:
                current = (Z-2, N-2)
            elif decay_mode == DecayMode.BETA_MINUS:
                current = (Z+1, N-1)
            elif decay_mode == DecayMode.BETA_PLUS:
                current = (Z-1, N+1)
            elif decay_mode == DecayMode.NEUTRON_EMISSION:
                current = (Z, N-1)
            elif decay_mode == DecayMode.PROTON_EMISSION:
                current = (Z-1, N)
            else:
                break
        
        return path
