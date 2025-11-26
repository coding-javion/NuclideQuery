# 核素数据查询工具

基于 NNDC NuDat 数据库的核素数据查询工具，同时支持多种 DFT 理论计算数据。

## ✨ 功能特性

- **多数据源支持**：实验数据（NNDC）+ 理论数据（SKMS, UNEDF0, UNEDF1, SLY4, SKP, SV-MIN）
- **统一的 API**：通过 `Nuclide` 类提供简洁一致的接口
- **灵活的输入**：支持 `(Z, N)` 或元素符号（如 `Fe56`）
- **丰富的数据**：结合能、分离能、Q值、激发态、半衰期、衰变模式等

## 📦 安装

> 建议使用 Python 3.9+，并在虚拟环境中操作以避免与系统依赖冲突。

### 方式一：克隆仓库后本地安装

```bash
git clone https://github.com/coding-javion/NuclideQuery.git
cd NuclideQuery
python -m venv .venv  # 可选 创建虚拟环境
.venv\Scripts\activate  # Windows激活虚拟环境
pip install -U pip # 可选 升级pip到最新版本
pip install -e .  # 以可编辑模式安装当前目录的包 或 pip install . 直接安装（非可编辑模式）
```

### 方式二：直接通过 pip 从 Git 安装（无需克隆）

```bash
pip install -U pip
pip install "git+https://github.com/coding-javion/NuclideQuery.git"
```

安装完成后，`nucquery` 命令和 `nuclide` 模块即可在任意位置使用。

## 🚀 快速开始

### Python API 使用

```python
from nucquery import Nuclide, NuclideQuery

# 1. 基础查询：查询实验数据（默认）
fe56 = Nuclide(26, 30)
print(f"BE = {fe56.BE:.3f} MeV")      # 结合能
print(f"BE/A = {fe56.BE_A:.3f} MeV")  # 比结合能
print(f"Sn = {fe56.Sn:.3f} MeV")      # 中子分离能

# 2. 查询理论数据
fe56_skms = Nuclide(26, 30, source='SKMS')
print(f"SKMS: BE = {fe56_skms.BE:.3f} MeV")

# 3. 从元素符号创建
pb208 = Nuclide.from_symbol("Pb208", source='UNEDF1')

# 4. 批量查询：获取同位素链
query = NuclideQuery(source='SKMS')
ca_isotopes = query.query_isotopes(20, N_min=20, N_max=30)
for nuc in ca_isotopes:
    print(f"{nuc.name}: BE/A = {nuc.BE_A:.3f} MeV")
```

### 命令行使用

```bash
# 查询实验数据
nucquery fe56
nucquery 26 30

# 查询理论数据
nucquery -s SKMS fe56
nucquery -s UNEDF1 pb208

# 列出所有可用数据源
nucquery --list-sources

# 批量查询同位素
nucquery -s SKMS -b isotopes 20
```

## 📊 可用数据源

| 数据源 | 类型 | 描述 | 核素数 |
|--------|------|------|--------|
| `experiment` | 实验 | NNDC NuDat 数据库 | ~3600 |
| `SKMS` | 理论 | SkM* 能量密度泛函 | ~8000 |
| `UNEDF0` | 理论 | UNEDF0 能量密度泛函 | ~8000 |
| `UNEDF1` | 理论 | UNEDF1 能量密度泛函 | ~8000 |
| `SLY4` | 理论 | Skyrme SLy4 泛函 | ~8000 |
| `SKP` | 理论 | Skyrme SKP 泛函 | ~8000 |
| `SV-MIN` | 理论 | SV-min 泛函 | ~8000 |

## 🔧 Nuclide 类属性

```python
nuc = Nuclide(26, 30)

# 基本信息
nuc.Z           # 质子数
nuc.N           # 中子数
nuc.A           # 质量数
nuc.name        # "Fe-56"
nuc.symbol      # "Fe"
nuc.exists      # 是否存在
nuc.source      # 数据源名称

# 结合能 (MeV)
nuc.BE          # 总结合能
nuc.BE_A        # 比结合能

# 分离能 (MeV)
nuc.Sn          # 单中子分离能
nuc.Sp          # 单质子分离能
nuc.S2n         # 双中子分离能
nuc.S2p         # 双质子分离能

# Q 值 (MeV)
nuc.Q_alpha     # α衰变 Q 值
nuc.Q_beta      # β⁻衰变 Q 值
nuc.Q_EC        # 电子俘获 Q 值

# 激发态能量 (MeV)
nuc.E_2plus     # 第一 2⁺ 态
nuc.E_4plus     # 第一 4⁺ 态
nuc.E_3minus    # 第一 3⁻ 态

# 衰变信息（仅实验数据）
nuc.halflife    # 半衰期
nuc.spin_parity # 自旋宇称
nuc.is_stable   # 是否稳定
nuc.decay_modes # 衰变模式列表
```

## 📈 绘图示例

```python
import matplotlib.pyplot as plt
from nucquery import NuclideQuery

# 比较实验与理论的比结合能
sources = ['experiment', 'SKMS', 'UNEDF1']
colors = ['black', 'red', 'blue']

plt.figure(figsize=(10, 6))
for src, color in zip(sources, colors):
    query = NuclideQuery(source=src)
    # 查询 Z=50 (锡) 的同位素链，中子数范围 50-90
    isotopes = query.query_isotopes(50, N_min=50, N_max=90)
    
    A = [n.A for n in isotopes if n.BE_A]
    BE_A = [n.BE_A for n in isotopes if n.BE_A]
    plt.plot(A, BE_A, 'o-', label=src, color=color, markersize=3)

plt.xlabel('Mass Number A')
plt.ylabel('BE/A (MeV)')
plt.legend()
plt.show()
```

## 📁 文件结构

```text
NuclideQuery/
├── README.md                     # 使用说明（本文件）
├── setup.py                      # 打包与安装配置
├── example/                      # 使用示例脚本
│   └── examples.py
├── nucquery/
│   ├── __init__.py
│   ├── cli.py                    # 命令行入口
│   ├── config.py                 # 全局配置与常量
│   ├── data_source.py            # 数据源抽象层及管理器
│   ├── nuclide.py                # Nuclide API
│   ├── nuclide_data.py           # 数据结构定义
│   ├── nuclide_query.py          # 核心查询类
│   ├── rich_output.py            # Rich 终端展示
│   └── data/                     # 原始实验/理论数据文件
│       ├── nndc_nudat_data_export.json
│       ├── SKMS_all_nuclei-new.dat
│       ├── SKP_all_nuclei.dat
│       ├── SLY4_all_nuclei.dat
│       ├── SV-MIN_all_nuclei.dat
│       ├── UNEDF0_all_nuclei.dat
│       └── UNEDF1_all_nuclei.dat
└── nucquery.egg-info/            # Python 包元数据
```

## 📝 数据来源

- **实验数据**: [NNDC NuDat](https://www.nndc.bnl.gov/nudat3/)
- **理论数据**: DFT 能量密度泛函计算

## 📄 许可证

MIT License
