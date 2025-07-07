from typing import TypedDict, Dict, List, Optional, Union, Any
from enum import Enum
from dataclasses import dataclass

class DecayMode(Enum):
    """衰变模式枚举"""
    STABLE = 'stable'
    ALPHA = 'alpha'
    BETA_MINUS = 'beta-'
    BETA_PLUS = 'beta+'
    ELECTRON_CAPTURE = 'EC'
    SPONTANEOUS_FISSION = 'sf'
    PROTON_EMISSION = 'p'
    NEUTRON_EMISSION = 'n'
    UNKNOWN = 'unknown'

@dataclass
class ValueWithUncertainty:
    """带不确定度的数值"""
    value: float
    uncertainty: float = 0.0
    unit: str = ""

@dataclass
class HalfLifeInfo:
    """半衰期信息"""
    value: Union[float, str]  # 数值或"STABLE"
    unit: str = "s"
    uncertainty: float = 0.0

@dataclass
class DecayModeInfo:
    """衰变模式信息"""
    mode: str
    value: float  # 分支比(%)
    uncertainty: float = 0.0

@dataclass
class LevelInfo:
    """能级信息"""
    energy: ValueWithUncertainty
    mass_excess: ValueWithUncertainty
    spin_parity: Optional[str] = None
    halflife: Optional[HalfLifeInfo] = None
    decay_modes_observed: Optional[List[DecayModeInfo]] = None
    decay_modes_predicted: Optional[List[DecayModeInfo]] = None

class NuclidePropertiesRequired(TypedDict):
    """核素属性必需字段"""
    Z: int  # 质子数
    N: int  # 中子数
    A: int  # 质量数
    name: str  # 核素名称
    symbol: str  # 元素符号

class NuclideProperties(NuclidePropertiesRequired, total=False):
    """核素属性定义 - 基于NNDC JSON数据的实际字段"""
    # 能级信息
    levels: List[LevelInfo]  # 所有能级
    ground_state: Optional[LevelInfo]  # 基态信息
    
    # 能量相关 (最常见字段)
    bindingEnergy: Optional[ValueWithUncertainty]  # 结合能
    bindingEnergyLDMFit: Optional[ValueWithUncertainty]  # LDM拟合结合能

    # 分离能 (高频字段)
    neutronSeparationEnergy: Optional[ValueWithUncertainty]  # 单中子分离能
    protonSeparationEnergy: Optional[ValueWithUncertainty]  # 单质子分离能
    twoNeutronSeparationEnergy: Optional[ValueWithUncertainty]  # 双中子分离能
    twoProtonSeparationEnergy: Optional[ValueWithUncertainty]  # 双质子分离能

    # 衰变相关 Q值
    alpha: Optional[ValueWithUncertainty]  # α衰变Q值
    deltaAlpha: Optional[ValueWithUncertainty]  # α衰变Q值不确定度
    betaMinus: Optional[ValueWithUncertainty]  # β-能量
    electronCapture: Optional[ValueWithUncertainty]  # 电子俘获能量
    positronEmission: Optional[ValueWithUncertainty]  # 正电子发射能量

    # 核结构参数
    pairingGap: Optional[ValueWithUncertainty]  # 配对能隙
    quadrupoleDeformation: Optional[ValueWithUncertainty]  # 四极形变

    # 多中子/质子衰变模式
    betaMinusOneNeutronEmission: Optional[ValueWithUncertainty]  # β-+中子发射
    betaMinusTwoNeutronEmission: Optional[ValueWithUncertainty]  # β-+双中子发射
    electronCaptureOneProtonEmission: Optional[ValueWithUncertainty]  # EC+质子发射
    doubleBetaMinus: Optional[ValueWithUncertainty]  # 双β-衰变
    doubleElectronCapture: Optional[ValueWithUncertainty]  # 双电子俘获

    # 激发态能量
    firstExcitedStateEnergy: Optional[ValueWithUncertainty]  # 第一激发态能量
    firstTwoPlusEnergy: Optional[ValueWithUncertainty]  # 第一个2+态能量
    firstFourPlusEnergy: Optional[ValueWithUncertainty]  # 第一个4+态能量
    firstFourPlusOverFirstTwoPlusEnergy: Optional[ValueWithUncertainty]  # 4+/2+比值
    firstThreeMinusEnergy: Optional[ValueWithUncertainty]  # 第一个3-态能量

    # 核结构和能级比
    BE4DBE2: Optional[ValueWithUncertainty]  # B(E4)/B(E2)比值

    # 核裂变产额 (约28%的核素有数据)
    FY235U: Optional[ValueWithUncertainty]  # U-235热中子裂变产额
    FY238U: Optional[ValueWithUncertainty]  # U-238快中子裂变产额
    FY239Pu: Optional[ValueWithUncertainty]  # Pu-239热中子裂变产额
    FY252Cf: Optional[ValueWithUncertainty]  # Cf-252自发裂变产额
    cFY235U: Optional[ValueWithUncertainty]  # U-235累积裂变产额
    cFY238U: Optional[ValueWithUncertainty]  # U-238累积裂变产额
    cFY239Pu: Optional[ValueWithUncertainty]  # Pu-239累积裂变产额
    cFY252Cf: Optional[ValueWithUncertainty]  # Cf-252累积裂变产额

    # 核反应数据 (如果需要，可以基于实际JSON添加)
    thermal_neutron_capture: Optional[ValueWithUncertainty]  # 热中子俘获截面
    
    # 统计和分布
    abundance: Optional[float]  # 自然丰度(%)
    isotopic_mass: Optional[ValueWithUncertainty]  # 同位素质量
    
    # 其他属性
    spin_parity: Optional[str]  # 自旋宇称
    isomeric_state: bool  # 是否为同核异能态
    magic_numbers: List[str]  # 幻数标记

# 元素符号映射 (Z -> symbol)
ELEMENT_SYMBOLS: Dict[int, str] = {
    1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O',
    9: 'F', 10: 'Ne', 11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P',
    16: 'S', 17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca', 21: 'Sc', 22: 'Ti',
    23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu',
    30: 'Zn', 31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr',
    37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb', 42: 'Mo', 43: 'Tc',
    44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn',
    51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba', 57: 'La',
    58: 'Ce', 59: 'Pr', 60: 'Nd', 61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd',
    65: 'Tb', 66: 'Dy', 67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb', 71: 'Lu',
    72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt',
    79: 'Au', 80: 'Hg', 81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At',
    86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th', 91: 'Pa', 92: 'U',
    93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm', 97: 'Bk', 98: 'Cf', 99: 'Es',
    100: 'Fm', 101: 'Md', 102: 'No', 103: 'Lr', 104: 'Rf', 105: 'Db',
    106: 'Sg', 107: 'Bh', 108: 'Hs', 109: 'Mt', 110: 'Ds', 111: 'Rg',
    112: 'Cn', 113: 'Nh', 114: 'Fl', 115: 'Mc', 116: 'Lv', 117: 'Ts',
    118: 'Og'
}

# 幻数
MAGIC_NUMBERS: List[int] = [2, 8, 20, 28, 50, 82, 126]

# 半衰期单位转换
HALF_LIFE_UNITS: Dict[str, float] = {
    'ys': 1e-24,  # 幺秒
    'zs': 1e-21,  # 仄秒
    'as': 1e-18,  # 阿秒
    'fs': 1e-15,  # 飞秒
    'ps': 1e-12,  # 皮秒
    'ns': 1e-9,   # 纳秒
    'μs': 1e-6,   # 微秒
    'ms': 1e-3,   # 毫秒
    's': 1,       # 秒
    'm': 60,      # 分钟
    'h': 3600,    # 小时
    'd': 86400,   # 天
    'y': 31557600 # 年(儒略年)
}

def get_nuclide_symbol(Z: int, N: int, style: str = 'style1') -> str:
    """返回核素的 LaTeX 格式符号"""
    A = Z + N
    symbol = ELEMENT_SYMBOLS.get(Z, f"X{Z}")
    
    # 使用最简单的 LaTeX 格式
    return f"{A}{symbol}"

def decay_mode_to_color(decay_mode: DecayMode) -> str:
    """衰变模式到颜色的映射"""
    colors = {
        DecayMode.STABLE: 'green',
        DecayMode.ALPHA: 'red',
        DecayMode.BETA_MINUS: 'blue',
        DecayMode.BETA_PLUS: 'cyan',
        DecayMode.ELECTRON_CAPTURE: 'cyan',
        DecayMode.SPONTANEOUS_FISSION: 'purple',
        DecayMode.PROTON_EMISSION: 'orange',
        DecayMode.NEUTRON_EMISSION: 'yellow',
        DecayMode.UNKNOWN: 'gray'
    }
    return colors.get(decay_mode, 'gray')

# 查询配置相关
@dataclass
class QueryConfig:
    """查询配置类"""
    # 基本信息显示
    show_basic_info: bool = True
    show_element_symbol: bool = True
    show_mass_number: bool = True
    
    # 能量信息显示
    show_binding_energy: bool = True
    show_binding_energy_per_nucleon: bool = True
    show_mass_excess: bool = False
    
    # 分离能显示
    show_neutron_separation: bool = True
    show_proton_separation: bool = True
    show_two_neutron_separation: bool = True
    show_two_proton_separation: bool = True
    show_alpha_separation: bool = False
    
    # 衰变信息显示
    show_decay_mode: bool = True
    show_halflife: bool = True
    show_decay_energies: bool = False
    
    # 核反应信息
    show_thermal_neutron_capture: bool = False
    
    # 核结构信息
    show_spin_parity: bool = False
    show_pairing_gap: bool = False
    show_shell_correction: bool = False
    show_deformation: bool = False
    
    # 统计信息
    show_abundance: bool = False
    
    # 显示格式
    show_uncertainties: bool = True
    energy_unit: str = "MeV"  # "MeV" 或 "keV"
    decimal_places: int = 3

# 预定义的查询配置 - 从 config.py 加载
def load_query_config(config_name: str = "basic") -> QueryConfig:
    """从配置文件加载查询配置"""
    import config
    
    config_data = config.QUERY_CONFIGS.get(config_name, config.QUERY_CONFIGS["basic"])
    return QueryConfig(**config_data)

def create_custom_config(**kwargs) -> QueryConfig:
    """创建自定义配置"""
    import config
    
    base_config_data = config.QUERY_CONFIGS["basic"]
    config_dict = {
        field.name: kwargs.get(field.name, base_config_data.get(field.name, False))
        for field in QueryConfig.__dataclass_fields__.values()
    }
    return QueryConfig(**config_dict)
