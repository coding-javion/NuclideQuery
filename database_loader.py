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
    
    def format_nuclide_output(self, nuclide_data: NuclideProperties) -> str:
        """根据配置格式化核素数据输出 - 清晰美观版本"""
        if not nuclide_data:
            return "未找到核素数据"
        
        config = self.query_config
        
        def format_value_with_uncertainty(data, unit="", scientific=False):
            """格式化带不确定度的数值"""
            if not data:
                return None
            
            # 处理 ValueWithUncertainty 对象
            if hasattr(data, 'value') and hasattr(data, 'uncertainty'):
                value, uncertainty = data.value, data.uncertainty
                data_unit = getattr(data, 'unit', unit)
            else:
                return str(data)
            
            if value is None:
                return None
            
            # 使用最终单位
            final_unit = unit if unit else data_unit
            
            # 格式化数值
            fmt = "e" if scientific else "f"
            precision = getattr(config, 'decimal_places', 3)  # 默认3位小数
            
            if getattr(config, 'show_uncertainties', True) and uncertainty:
                if isinstance(uncertainty, dict):
                    # 处理复杂不确定度格式
                    if uncertainty.get('type') == 'symmetric':
                        unc_val = uncertainty.get('value', 0)
                        if unc_val > 0:
                            return f"{value:.{precision}{fmt}} ± {unc_val:.{precision}{fmt}} {final_unit}".strip()
                    elif uncertainty.get('type') == 'asymmetric':
                        upper = uncertainty.get('upperLimit', 0)
                        lower = uncertainty.get('lowerLimit', 0)
                        if upper > 0 or lower > 0:
                            return f"{value:.{precision}{fmt}} +{upper:.{precision}{fmt}}/-{lower:.{precision}{fmt}} {final_unit}".strip()
                    else:
                        return f"{value:.{precision}{fmt}} {final_unit}".strip()
                elif isinstance(uncertainty, (int, float)) and uncertainty > 0:
                    return f"{value:.{precision}{fmt}} ± {uncertainty:.{precision}{fmt}} {final_unit}".strip()
            
            return f"{value:.{precision}{fmt}} {final_unit}".strip()
        
        lines = []
        
        # 1. 核素标题
        if getattr(config, 'show_basic_info', True):
            Z, N, A = nuclide_data.get('Z', 0), nuclide_data.get('N', 0), nuclide_data.get('A', 0)
            symbol = nuclide_data.get('symbol', 'Unknown')
            
            title = f"╔═══ {A}{symbol} (Z={Z}, N={N}) ═══"
            lines.append(title)
            
            # 半衰期和自旋宇称单独一行
            info_line = "║"
            if getattr(config, 'show_halflife', True):
                ground_state = nuclide_data.get('ground_state')
                if ground_state and hasattr(ground_state, 'halflife') and ground_state.halflife:
                    hl = ground_state.halflife
                    if hasattr(hl, 'value'):
                        if isinstance(hl.value, str):
                            info_line += f"  半衰期: {hl.value}"
                        else:
                            formatted = format_value_with_uncertainty(hl)
                            if formatted:
                                info_line += f"  半衰期: {formatted}"
            
            if getattr(config, 'show_spin_parity', True):
                ground_state = nuclide_data.get('ground_state')
                if ground_state and hasattr(ground_state, 'spin_parity') and ground_state.spin_parity:
                    if len(info_line) > 1:
                        info_line += " | "
                    info_line += f"自旋宇称: {ground_state.spin_parity}"
            
            if len(info_line) > 1:
                lines.append(info_line)
        
        # 2. 结合能和质量信息
        if getattr(config, 'show_binding_energy', True) or getattr(config, 'show_mass_excess', True):
            lines.append("╠─ 能量特性")
            
            # 结合能和比结合能在一行
            if getattr(config, 'show_binding_energy', True):
                be_data = nuclide_data.get('bindingEnergy')
                if be_data:
                    energy_unit = getattr(config, 'energy_unit', 'MeV')
                    formatted_be = format_value_with_uncertainty(be_data, energy_unit)
                    if formatted_be:
                        # 计算比结合能
                        be_per_nucleon = ""
                        if getattr(config, 'show_binding_energy_per_nucleon', True):
                            if hasattr(be_data, 'value'):
                                be_value = be_data.value
                                A = nuclide_data.get('A', 1)
                                if A > 0 and be_value:
                                    bea = be_value / A
                                    precision = getattr(config, 'decimal_places', 3)
                                    be_per_nucleon = f" | 比结合能: {bea:.{precision}f} {energy_unit}/核子"
                        
                        lines.append(f"║  结合能: {formatted_be}{be_per_nucleon}")
            
            # 质量过剩
            if getattr(config, 'show_mass_excess', True):
                ground_state = nuclide_data.get('ground_state')
                if ground_state and hasattr(ground_state, 'mass_excess') and ground_state.mass_excess:
                    energy_unit = getattr(config, 'energy_unit', 'MeV')
                    formatted = format_value_with_uncertainty(ground_state.mass_excess, energy_unit)
                    if formatted:
                        lines.append(f"║  质量过剩: {formatted}")
        
        # 3. 分离能 - 合并显示
        energy_unit = getattr(config, 'energy_unit', 'MeV')
        
        # 收集分离能数据
        neutron_sep = None
        proton_sep = None
        two_neutron_sep = None
        two_proton_sep = None
        
        if getattr(config, 'show_neutron_separation', True):
            data = nuclide_data.get('neutronSeparationEnergy')
            if data:
                neutron_sep = format_value_with_uncertainty(data, energy_unit)
        
        if getattr(config, 'show_proton_separation', True):
            data = nuclide_data.get('protonSeparationEnergy')
            if data:
                proton_sep = format_value_with_uncertainty(data, energy_unit)
        
        if getattr(config, 'show_two_neutron_separation', True):
            data = nuclide_data.get('twoNeutronSeparationEnergy')
            if data:
                two_neutron_sep = format_value_with_uncertainty(data, energy_unit)
        
        if getattr(config, 'show_two_proton_separation', True):
            data = nuclide_data.get('twoProtonSeparationEnergy')
            if data:
                two_proton_sep = format_value_with_uncertainty(data, energy_unit)
        
        # 显示分离能（合并行）
        if any([neutron_sep, proton_sep, two_neutron_sep, two_proton_sep]):
            lines.append("╠─ 分离能")
            
            # 中子分离能和质子分离能在一行
            if neutron_sep or proton_sep:
                sep_line = "║  "
                if neutron_sep:
                    sep_line += f"中子分离能:   {neutron_sep}"
                if proton_sep:
                    if neutron_sep:
                        sep_line += f" | 质子分离能:   {proton_sep}"
                    else:
                        sep_line += f"质子分离能:   {proton_sep}"
                lines.append(sep_line)
            
            # 双中子分离能和双质子分离能在一行
            if two_neutron_sep or two_proton_sep:
                two_sep_line = "║  "
                if two_neutron_sep:
                    two_sep_line += f"双中子分离能: {two_neutron_sep}"
                if two_proton_sep:
                    if two_neutron_sep:
                        two_sep_line += f" | 双质子分离能: {two_proton_sep}"
                    else:
                        two_sep_line += f"双质子分离能: {two_proton_sep}"
                lines.append(two_sep_line)
        
        # 4. 激发态能量
        excitation_energies = []
        if getattr(config, 'show_decay_energies', True):  # 只有在显示衰变能量时才显示激发态
            energy_unit = getattr(config, 'energy_unit', 'MeV')
            excitation_configs = [
                ("firstExcitedStateEnergy", "第一激发态"),
                ("firstTwoPlusEnergy", "第一2+态"),
                ("firstFourPlusEnergy", "第一4+态"),
                ("firstThreeMinusEnergy", "第一3-态"),
            ]
            
            for data_key, label in excitation_configs:
                data = nuclide_data.get(data_key)
                if data:
                    formatted = format_value_with_uncertainty(data, energy_unit)
                    if formatted:
                        excitation_energies.append((label, formatted))
        
        if excitation_energies:
            lines.append("╠─ 激发态能量")
            for label, value in excitation_energies:
                lines.append(f"║  {label:10}: {value}")
        
        # 5. 其他特性
        other_properties = []
        
        # 形变参数 - 在basic模式下也显示
        if getattr(config, 'show_deformation', False):
            deformation_data = nuclide_data.get('quadrupoleDeformation')
            if deformation_data:
                formatted = format_value_with_uncertainty(deformation_data, "")
                if formatted:
                    other_properties.append(("四极形变 β₂", formatted))
        
        if getattr(config, 'show_decay_energies', True) and getattr(config, 'show_pairing_gap', True):
            energy_unit = getattr(config, 'energy_unit', 'MeV')
            data = nuclide_data.get('pairingGap')
            if data:
                formatted = format_value_with_uncertainty(data, energy_unit)
                if formatted:
                    other_properties.append(("配对能隙", formatted))
        
        # B(E4)/B(E2)比值 - 只在显示衰变能量时显示
        if getattr(config, 'show_decay_energies', True):
            be4be2_data = nuclide_data.get('BE4DBE2')
            if be4be2_data:
                formatted = format_value_with_uncertainty(be4be2_data, "")
                if formatted:
                    other_properties.append(("B(E4)/B(E2)", formatted))
            
            # E(4+)/E(2+)比值
            ratio_data = nuclide_data.get('firstFourPlusOverFirstTwoPlusEnergy')
            if ratio_data:
                formatted = format_value_with_uncertainty(ratio_data, "")
                if formatted:
                    other_properties.append(("E(4+)/E(2+)", formatted))
        
        if getattr(config, 'show_thermal_neutron_capture', True):
            thermal_capture = nuclide_data.get('thermal_neutron_capture')
            if thermal_capture:
                formatted = format_value_with_uncertainty(thermal_capture, "barn")
                if formatted:
                    other_properties.append(("热中子俘获截面", formatted))
        
        if getattr(config, 'show_abundance', True):
            abundance = nuclide_data.get('abundance')
            if abundance is not None:
                precision = getattr(config, 'decimal_places', 3)
                other_properties.append(("自然丰度", f"{abundance:.{precision}f}%"))
        
        if other_properties:
            lines.append("╠─ 其他特性")
            for label, value in other_properties:
                lines.append(f"║  {label:12}: {value}")
        
        # 6. 衰变信息
        if getattr(config, 'show_halflife', True):
            ground_state = nuclide_data.get('ground_state')
            if ground_state and hasattr(ground_state, 'decay_modes_observed') and ground_state.decay_modes_observed:
                lines.append("╠─ 衰变模式")
                precision = getattr(config, 'decimal_places', 3)
                for decay_mode in ground_state.decay_modes_observed:
                    if hasattr(decay_mode, 'mode') and hasattr(decay_mode, 'value'):
                        mode_str = f"{decay_mode.mode}: {decay_mode.value:.{precision}f}%"
                        # 安全处理不确定度
                        if hasattr(decay_mode, 'uncertainty'):
                            uncertainty = decay_mode.uncertainty
                            # 处理不确定度可能是字典的情况
                            if isinstance(uncertainty, dict):
                                # 如果是字典，尝试获取数值
                                unc_val = uncertainty.get('value', 0) if uncertainty else 0
                                if unc_val and unc_val > 0:
                                    mode_str += f" ± {unc_val:.{precision}f}%"
                            elif isinstance(uncertainty, (int, float)) and uncertainty > 0:
                                mode_str += f" ± {uncertainty:.{precision}f}%"
                        lines.append(f"║  {mode_str}")
        
        # 结束线
        if lines:
            # 计算最大宽度，安全处理空行
            max_width = 0
            for line in lines:
                if line:
                    # 移除框线字符来计算内容宽度
                    content = line.replace('║', '').replace('╠', '').replace('─', '').replace('╔', '').replace('═', '')
                    max_width = max(max_width, len(content))
            
            # 确保最小宽度
            max_width = max(max_width, 30)
            lines.append("╚" + "═" * max_width)
        
        return '\n'.join(lines) if lines else "未找到可显示的核素数据"
        
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
