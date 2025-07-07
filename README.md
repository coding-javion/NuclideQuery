# 核素查询工具 v1.0.0-beta

基于NNDC NUDAT数据库的核素实验数据查询工具包，支持查询结合能、分离能、半衰期、自旋宇称等核物理参数。

## 🚀 特性

- **灵活输入**：支持质子数+中子数或元素符号+质量数两种格式
- **完整数据**：提供结合能、单/双中子分离能、单/双质子分离能、半衰期、自旋宇称
- **多种模式**：基础模式和详细模式，满足不同需求
- **美观输出**：全新设计的格式化输出，清晰易读
- **准确数据**：基于NNDC官方数据，包含不确定度信息
- **易于使用**：简洁的命令行接口和详细的数据展示
- **类型安全**：完整的类型注解，支持现代Python开发环境

## 📁 项目结构

```bash
NuclideQuery/
├── batch_nuclide_query.py       # 批量查询工具
├── config.py                    # 配置文件
├── database_loader.py           # 数据库加载器（核心模块）
├── examples.py                  # 使用示例演示
├── nndc_nudat_data_export.json  # NNDC数据文件
├── nuclide_data.py              # 数据结构定义
├── nuclide_query.py             # 单个查询工具
├── README.md
```

## 🔧 快速开始

### 1. 基本查询

```python
from database_loader import NuclideDataLoader

# 创建数据加载器
loader = NuclideDataLoader()

# 查询核素数据
data = loader.get_nuclide_data(Z=26, N=30)  # Fe-56
output = loader.format_nuclide_output(data)
print(output)
```

### 2. 命令行查询（推荐）

```bash
# 查询铁-56
python nuclide_query.py fe56
```

### 3. 基础模式输出示例

```bash
核素实验数据查询工具
==================================================
查询核素: 56Fe (Z=26, N=30)
查询模式: basic
╔═══ 56Fe (Z=26, N=30) ═══
║  半衰期: STABLE | 自旋宇称: 0+
╠─ 能量特性
║  结合能: 8.79 MeV | 比结合能: 0.16 MeV/核子
╠─ 分离能
║  中子分离能:   11.20 MeV | 质子分离能:   10.18 MeV
║  双中子分离能: 20.50 MeV | 双质子分离能: 18.25 MeV
╠─ 其他特性
║  四极形变 β₂     : 0.25
```

## 📊 高级用法

### 1. 详细模式查询（包含不确定度）

```python
from database_loader import NuclideDataLoader

# 使用详细配置，显示不确定度
loader = NuclideDataLoader(query_config="detailed")
data = loader.get_nuclide_data(6, 8)  # C-14
output = loader.format_nuclide_output(data)
print(output)
```

### 2. 配置自定义查询

```python
from nuclide_data import load_query_config

# 查看可用配置
configs = ["basic", "detailed", "research", "quick"]

# 使用特定配置
loader = NuclideDataLoader(query_config="research")
```

## 🔬 数据结构

### 核素属性 (NuclideProperties)

```python
class NuclideProperties(TypedDict, total=False):
    # 基本属性
    Z: int                              # 质子数
    N: int                              # 中子数
    A: int                              # 质量数
    name: str                           # 核素名称
    symbol: str                         # 元素符号
    
    # 能量相关
    binding_energy: ValueWithUncertainty        # 结合能
    binding_energy_per_nucleon: float           # 比结合能
    mass_excess: ValueWithUncertainty           # 质量余量
    
    # 分离能
    neutron_separation_energy: ValueWithUncertainty   # 单中子分离能
    proton_separation_energy: ValueWithUncertainty    # 单质子分离能
    two_neutron_separation_energy: ValueWithUncertainty  # 双中子分离能
    two_proton_separation_energy: ValueWithUncertainty   # 双质子分离能
    
    # 衰变相关
    decay_mode: DecayMode               # 主要衰变模式
    halflife: HalfLifeInfo              # 半衰期
    
    # 激发态信息
    first_excited_state_energy: ValueWithUncertainty
    first_two_plus_energy: ValueWithUncertainty
    first_four_plus_energy: ValueWithUncertainty
    
    # 其他属性
    spin_parity: str                    # 自旋宇称
    abundance: float                    # 自然丰度
    # ... 更多字段
```

### 带不确定度的数值

```python
@dataclass
class ValueWithUncertainty:
    value: float                        # 数值
    uncertainty: float = 0.0            # 不确定度
    unit: str = ""                      # 单位
```

## ⚙️ 配置系统

### 预定义配置

- **`basic`**: 基础信息 + 自旋宇称
- **`detailed`**: 详细信息 + 不确定度
- **`research`**: 研究级配置，包含所有信息
- **`quick`**: 快速查询，仅核心信息

### 自定义配置

```python
from nuclide_data import create_custom_config

# 创建自定义配置
custom_config = create_custom_config(
    show_binding_energy=True,
    show_uncertainties=True,
    show_spin_parity=True,
    decimal_places=2
)
```

## 🧪 测试

运行系统性测试：

```bash
python test_system.py
```

测试覆盖：

- ✅ 模块导入测试
- ✅ 数据加载测试（3603个核素数据）
- ✅ 查询配置测试
- ✅ 数据结构测试
- ✅ 单核素查询测试
- ✅ 批量查询测试
- ✅ 格式化输出测试

## 📋 支持的数据字段

### 基本信息

- 质子数、中子数、质量数
- 元素符号、核素名称
- 自旋宇称、自然丰度

### 能量信息

- 结合能、比结合能
- 质量余量
- 各种分离能（SN, SP, S2N, S2P, Sα）

### 衰变信息

- 衰变模式、半衰期
- 各种衰变能量（α, β±, EC等）

### 激发态信息

- 第一激发态能量
- 特定态能量（2+, 4+, 3-）
- 能级比值（4+/2+）

### 核裂变产额

- U-235, U-238, Pu-239, Cf-252裂变产额
- 累积裂变产额

## 📝 版本信息

**v1.0.0-beta** (2025-07-07)

### 最新改进

- ✅ **重写输出格式**：全新设计的美观清晰的输出格式
- ✅ **修复半衰期显示**：解决了半衰期查询显示问题
- ✅ **改进不确定度处理**：支持对称和非对称不确定度格式
- ✅ **优化代码结构**：简化了格式化逻辑，提高可维护性
- ✅ **完善类型安全**：零类型检查错误，完整的类型注解
- ✅ **数据验证**：基于NNDC NUDAT数据的3603个核素数据验证

### 主要特性

- 完整的类型安全系统
- 基于NNDC NUDAT数据的3603个核素数据
- 灵活的配置系统（basic, detailed, research, quick）
- 美观的格式化输出
- 全面的测试覆盖
- 完整的错误处理

### 已知问题

- 无重大已知问题

### 技术规格

- Python 3.8+
- 基于TypedDict的类型安全
- 支持dataclass数据结构
- 完整的类型注解

## 🛠️ 开发

### 数据源

- NNDC NUDAT数据库
- 数据文件：`nndc_nudat_data_export.json`

### 核心模块

- `database_loader.py`: 数据加载和处理
- `nuclide_data.py`: 数据结构定义
- `config.py`: 配置管理
- `nuclide_query.py`: 单核素查询
- `batch_nuclide_query.py`: 批量查询

### 代码质量

- 完整的类型注解
- 零类型检查错误
- 全面的错误处理
- 详细的文档字符串

## 📞 使用支持

### 基本用法

```python
from database_loader import NuclideDataLoader

# 创建加载器
loader = NuclideDataLoader()

# 查询核素
data = loader.get_nuclide_data(Z=26, N=30)  # Fe-56
if data:
    print(loader.format_nuclide_output(data))
```

### 详细模式

```python
# 显示不确定度信息
loader = NuclideDataLoader(query_config="detailed") 
data = loader.get_nuclide_data(Z=6, N=8)  # C-14
print(loader.format_nuclide_output(data))
```

---

> 基于NNDC NUDAT数据库构建的核素查询工具 - 为核物理研究提供准确、便捷的核素数据查询服务
