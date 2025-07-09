# 核素查询工具配置文件
# Nuclide Query Tool Configuration


from dataclasses import dataclass

# ====================================================
# 查询配置定义
# ====================================================

# 查询配置相关
@dataclass
class QueryConfig:
    """查询配置类"""
    # 块信息显示
    show_minimal_info: bool = False
    show_energy_info : bool = True
    show_separation_info: bool = True
    show_Q_values: bool = False
    show_excitation_energy: bool = False
    show_fission_yields: bool = False
    show_levels: bool = True
    
    # 能量信息显示
    show_binding_energy: bool = True
    show_binding_energy_per_nucleon: bool = True
    show_mass_excess: bool = False
    
    # 分离能显示
    show_neutron_separation: bool = True
    show_proton_separation: bool = True
    show_two_neutron_separation: bool = True
    show_two_proton_separation: bool = True

    # Q值信息显示
    show_alpha_separation: bool = True
    show_delta_alpha: bool = True
    show_beta_minus: bool = True
    show_electron_capture: bool = True
    show_positron_emission: bool = True
    show_beta_minus_one_neutron_emission: bool = True
    show_beta_minus_two_neutron_emission: bool = True
    show_electron_capture_one_proton_emission: bool = True
    show_double_beta_minus: bool = True
    show_double_electron_capture: bool = True

    # 激发态能量信息
    show_first_excitation_energy: bool = True
    show_first_2plus_energy: bool = True
    show_first_4plus_energy: bool = True
    show_first_4plus_divided_by_2plus: bool = True
    show_first_3minus_energy: bool = True
    
    # 裂变产额信息
    
    show_u235_ify: bool = True
    show_u238_ify: bool = True
    show_pu239_ify: bool = True
    show_cf252_ify: bool = True
    show_u235_cfy: bool = True
    show_u238_cfy: bool = True
    show_pu239_cfy: bool = True
    show_cf252_cfy: bool = True

    # 核素能级信息
    show_levels_energy: bool = True
    show_levels_halflife: bool = True
    show_levels_spin_parity: bool = True
    show_levels_decay_modes: bool = True
    show_levels_branching_ratios: bool = True
    
    # 显示格式
    show_uncertainties: bool = False
    energy_unit: str = "MeV"  # "MeV" 或 "keV"
    decimal_places: int = 3

    # 预定义的查询配置
    def __init__(self, mode: str = "basic"):
        if mode == "basic":
            pass
        elif mode == "detailed":
            self.show_energy_info = True
            self.show_separation_info = True
            self.show_Q_values = True
            self.show_excitation_states_energy = True
            self.show_fission_yields = True
            self.show_levels = True
            self.show_uncertainties = True
        elif mode == "minimal":
            self.show_minimal_info = True
            self.show_energy_info = False
            self.show_separation_info = False
            self.show_Q_values = False
            self.show_excitation_states_energy = False
            self.show_fission_yields = False
            self.show_levels = False
            self.show_uncertainties = False
        else:
            print(f"未知查询模式: {mode}, 使用默认配置")

# ====================================================
# 批量查询配置
# ====================================================

# 批量查询CSV导出字段
BATCH_QUERY_CSV_FIELDS = [
    "Z", "N", "A", "symbol", "name",
    "binding_energy", "binding_energy_per_nucleon",
    "neutron_separation_energy", "proton_separation_energy",
    "two_neutron_separation_energy", "two_proton_separation_energy",
    "decay_mode", "halflife", "spin_parity"
]

# ====================================================
# 显示格式配置
# ====================================================

# 数据文件路径
DATA_FILE_PATH = "nndc_nudat_data_export.json"
