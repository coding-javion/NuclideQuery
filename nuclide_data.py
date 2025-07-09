from typing import TypedDict, Dict, List, Optional, Union, Any
from enum import Enum
from dataclasses import dataclass

@dataclass
class ValueWithUncertainty:
    """带不确定度的数值"""
    value: Union[float, str, None] = None
    uncertainty: Optional[float] = None
    unit: str = ""

    def __mul__(self, other: int) -> 'ValueWithUncertainty':
        """乘法运算"""
        new_value = self.value * other if isinstance(self.value, float) else None
        new_uncertainty = self.uncertainty * other if isinstance(self.uncertainty, float) else None
        return ValueWithUncertainty(new_value, new_uncertainty, self.unit)

    def __truediv__(self, other: int) -> 'ValueWithUncertainty':
        """除法运算"""
        new_value = self.value / other if isinstance(self.value, float) else None
        new_uncertainty = self.uncertainty / other if isinstance(self.uncertainty, float) else None
        return ValueWithUncertainty(new_value, new_uncertainty, self.unit)

@dataclass
class DecayModeInfo(ValueWithUncertainty):
    """衰变模式信息"""
    mode: str = ""

@dataclass
class HalfLifeInfo(ValueWithUncertainty):
    """半衰期信息"""
    value = "STABLE"  # 可以是数值或"STABLE"

@dataclass
class LevelInfo:
    """能级信息"""
    energy: ValueWithUncertainty
    mass_excess: ValueWithUncertainty
    spin_parity: Optional[str] = None
    halflife: Optional[ValueWithUncertainty] = None
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
    bindingEnergyPerNucleon: Optional[ValueWithUncertainty]  # 每核结合能
    bindingEnergyLDMFit: Optional[ValueWithUncertainty]  # LDM拟合结合能

    # 分离能 (高频字段)
    neutronSeparationEnergy: Optional[ValueWithUncertainty]  # 单中子分离能
    protonSeparationEnergy: Optional[ValueWithUncertainty]  # 单质子分离能
    twoNeutronSeparationEnergy: Optional[ValueWithUncertainty]  # 双中子分离能
    twoProtonSeparationEnergy: Optional[ValueWithUncertainty]  # 双质子分离能

    # 结构信息（导出量）
    pairingGap: Optional[ValueWithUncertainty]  # 配对能隙
    quadrupoleDeformation: Optional[ValueWithUncertainty]  # 四极形变
    
    # 衰变相关 Q值
    alpha: Optional[ValueWithUncertainty]  # α衰变Q值
    deltaAlpha: Optional[ValueWithUncertainty]  # α衰变Q值的变化量
    betaMinus: Optional[ValueWithUncertainty]  # β-能量
    electronCapture: Optional[ValueWithUncertainty]  # 电子俘获能量
    positronEmission: Optional[ValueWithUncertainty]  # 正电子发射能量
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