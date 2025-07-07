# 核素查询工具配置文件
# Nuclide Query Tool Configuration

# ====================================================
# 查询配置定义
# ====================================================

# 基础查询配置 - 包含基态宇称的简化显示
BASIC_QUERY_CONFIG = {
    "show_basic_info": True,
    "show_element_symbol": True,
    "show_mass_number": True,
    "show_binding_energy": True,
    "show_binding_energy_per_nucleon": True,
    "show_mass_excess": False,
    "show_neutron_separation": True,
    "show_proton_separation": True,
    "show_two_neutron_separation": True,
    "show_two_proton_separation": True,
    "show_alpha_separation": False,
    "show_decay_mode": False,
    "show_halflife": True,
    "show_decay_energies": False,
    "show_thermal_neutron_capture": False,
    "show_spin_parity": True,  # 显示基态自旋宇称
    "show_pairing_gap": False,
    "show_shell_correction": False,
    "show_deformation": True,  # 启用形变显示
    "show_abundance": False,
    "show_uncertainties": False,
    "energy_unit": "MeV",
    "decimal_places": 2
}

# 详细查询配置
DETAILED_QUERY_CONFIG = {
    "show_basic_info": True,
    "show_element_symbol": True,
    "show_mass_number": True,
    "show_binding_energy": True,
    "show_binding_energy_per_nucleon": True,
    "show_mass_excess": True,
    "show_neutron_separation": True,
    "show_proton_separation": True,
    "show_two_neutron_separation": True,
    "show_two_proton_separation": True,
    "show_alpha_separation": True,
    "show_decay_mode": True,
    "show_halflife": True,
    "show_decay_energies": True,
    "show_thermal_neutron_capture": True,
    "show_spin_parity": True,
    "show_pairing_gap": True,
    "show_shell_correction": True,
    "show_deformation": True,
    "show_abundance": True,
    "show_uncertainties": True,
    "energy_unit": "MeV",
    "decimal_places": 6
}

# 默认查询模式
DEFAULT_QUERY_MODE = "basic"

# 查询配置映射
QUERY_CONFIGS = {
    "basic": BASIC_QUERY_CONFIG,
    "detailed": DETAILED_QUERY_CONFIG
}

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

# 能量单位
ENERGY_UNIT = "MeV"

# 数据文件路径
DATA_FILE_PATH = "nndc_nudat_data_export.json"
