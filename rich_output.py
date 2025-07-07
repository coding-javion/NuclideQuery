#!/usr/bin/env python3
"""
核素数据美观输出类
使用 rich 库实现美观的命令行输出
"""

from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.emoji import Emoji
from rich.style import Style
from rich.box import ROUNDED
from rich.align import Align
from rich.measure import Measurement

from nuclide_data import NuclideProperties

class NuclideRichPrinter:
    """核素数据的美观输出类"""
    
    def __init__(self, query_config=None):
        """
        初始化输出器
        
        参数:
            query_config: 查询配置对象，用于确定显示哪些信息
        """
        self.console = Console()
        self.config = query_config
        
        # 计算表格宽度（终端宽度的80%）
        terminal_width = self.console.size.width
        self.table_width = int(terminal_width * 0.8)
        # 设置列宽比例 (4:6)
        self.key_width = int(self.table_width * 0.4)
        self.value_width = int(self.table_width * 0.6)
        
        # 定义颜色主题
        self.theme = {
            'title': 'bold cyan',
            'key': 'bold white',
            'value': 'white',
            'unit': 'yellow',
            'uncertainty': 'dim white',
            'warning': 'bold red',
            'success': 'bold green',
            'info': 'bold blue',
            'highlight': 'bold magenta',
            'border': 'dim blue',
            'element': 'bold cyan',
            'energy': 'bold yellow',
            'separation': 'bold green',
            'excitation': 'bold magenta',
            'Q_value': 'bold cyan',
            'fission_yield': 'bold green',
            'level': 'bold blue',
            'decay': 'bold red',
        }
    
    def format_value(self, data, style="value", scientific=False):
        """格式化各种数值（包括不带/带不确定度，不带/带单位的数值，返回Rich Text对象"""
        if not data:
            return None
        
        # 处理 ValueWithUncertainty 对象
        if hasattr(data, 'value') and hasattr(data, 'uncertainty') and hasattr(data, 'unit'):
            value, uncertainty, unit = data.value, data.uncertainty, data.unit
        else:
            return Text(str(data), style=style)
        
        if value is None:
            return None
        
        
        # 格式化数值，如果小于1e-3则使用科学计数法
        if isinstance(value, (int, float)):
            if value < 1e-3:
                scientific = True
        fmt = "e" if scientific else "f"
        precision = getattr(self.config, 'decimal_places', 3) if self.config else 3
        
        # 构建Rich Text对象
        text = Text()
        
        # 主要数值
        text.append(f"{value:.{precision}{fmt}}", style=style)
        
        # 不确定度
        if (getattr(self.config, 'show_uncertainties', True) if self.config else True) and uncertainty:
            if isinstance(uncertainty, dict):
                # 处理复杂不确定度格式
                if uncertainty.get('type') == 'symmetric':
                    unc_val = uncertainty.get('value', 0)
                    if unc_val > 0:
                        text.append(" ± ", style=self.theme['uncertainty'])
                        text.append(f"{unc_val:.{precision}{fmt}}", style=self.theme['uncertainty'])
                elif uncertainty.get('type') == 'asymmetric':
                    upper = uncertainty.get('upperLimit', 0)
                    lower = uncertainty.get('lowerLimit', 0)
                    if upper > 0 or lower > 0:
                        text.append(" +", style=self.theme['uncertainty'])
                        text.append(f"{upper:.{precision}{fmt}}", style=self.theme['uncertainty'])
                        text.append("/-", style=self.theme['uncertainty'])
                        text.append(f"{lower:.{precision}{fmt}}", style=self.theme['uncertainty'])
            elif isinstance(uncertainty, (int, float)) and uncertainty > 0:
                text.append(" ± ", style=self.theme['uncertainty'])
                text.append(f"{uncertainty:.{precision}{fmt}}", style=self.theme['uncertainty'])
        
        text.append(f" {unit}", style=self.theme['unit'])
        
        return text

    def _create_standard_table(self, title: str, show_header: bool = False, style: Optional[str] = None, columns: Optional[List[tuple]] = None) -> Table:
        """创建标准格式的表格
        
        参数:
            title: 表格标题
            show_header: 是否显示表头
            columns: 列定义列表，格式为 [(name, width, style), ...]
        """
        table = Table(
            title=title,
            show_header=show_header,
            box=ROUNDED,
            header_style=style,
            border_style=style,
            title_style=style,
            padding=(0, 1),
            width=self.table_width
        )
        
        if columns:
            for name, width, style in columns:
                table.add_column(name, width=width, style=style)
        else:
            # 默认两列布局 (4:6比例)
            table.add_column("属性", width=self.key_width, style=style)
            table.add_column("数值", width=self.value_width, style=self.theme['value'])
        
        return table
    
    def print_nuclide_info(self, nuclide_data: NuclideProperties) -> None:
        """打印核素的详细信息"""
        if not nuclide_data:
            self.console.print(Panel(
                "[warning]未找到核素数据[/warning]",
                title="❌ 查询结果",
                style="border"
            ))
            return
        
        # 基本信息
        Z, N, A = nuclide_data.get('Z', 0), nuclide_data.get('N', 0), nuclide_data.get('A', 0)
        symbol = nuclide_data.get('symbol', 'Unknown')
        
        def add_row_to_table(self, table: Table, key: str, data_key: str) -> None:
            """向表格添加一行数据
            
            参数:
                table: 要添加行的表格对象
                key: 列名
                value: 列值，可以是字符串、数值或Rich Text对象
                data_key: 数据键，用于获取数据
                style: 列样式
            """
            data = nuclide_data.get(data_key)
            if data:
                table.add_row(Text(key), self.format_value(data))

        # 能量特性
        title = f"{A}{symbol} (Z={Z}, N={N})"
        energy_table = self._create_standard_table(title, style=self.theme['energy'])

        # 结合能
        if getattr(self.config, 'show_binding_energy', True) if self.config else True:
            add_row_to_table(self, energy_table, "结合能", 'bindingEnergy')
                    
        # 比结合能
        if getattr(self.config, 'show_binding_energy_per_nucleon', True) if self.config else True:
            add_row_to_table(self, energy_table, "比结合能", 'bindingEnergyPerNucleon')
                    
        # 显示表格（居中）
        self.console.print(Align.center(energy_table))
        
        # 分离能
        separation_table = self._create_standard_table(
            title=f"{A}{symbol} 分离能",
            style=self.theme['separation']
        )
        
        # 中子分离能
        if getattr(self.config, 'show_neutron_separation', True) if self.config else True:
            add_row_to_table(self, separation_table, "中子分离能", 'neutronSeparationEnergy')
        
        # 质子分离能
        if getattr(self.config, 'show_proton_separation', True) if self.config else True:
            add_row_to_table(self, separation_table, "质子分离能", 'protonSeparationEnergy')
        
        # 双中子分离能
        if getattr(self.config, 'show_two_neutron_separation', True) if self.config else True:
            add_row_to_table(self, separation_table, "双中子分离能", 'twoNeutronSeparationEnergy')
        
        # 双质子分离能
        if getattr(self.config, 'show_two_proton_separation', True) if self.config else True:
            add_row_to_table(self, separation_table, "双质子分离能", 'twoProtonSeparationEnergy')
        
        # 显示表格（居中）
        self.console.print(Align.center(separation_table))
        
        # Q值特性
        if getattr(self.config, 'show_Q_values', True) if self.config else True:
            Q_value_table = self._create_standard_table(
                title=f"{A}{symbol} Q值",
                style=self.theme['Q_value']
            )
            add_row_to_table(self, Q_value_table, "α衰变Q值", 'alpha')
            add_row_to_table(self, Q_value_table, "α衰变Q值变化量", 'deltaAlpha')
            add_row_to_table(self, Q_value_table, "β-衰变Q值", 'betaMinus')
            add_row_to_table(self, Q_value_table, "电子捕获Q值", 'electronCapture')
            add_row_to_table(self, Q_value_table, "正电子发射Q值", 'positronEmission')
            add_row_to_table(self, Q_value_table, "β-单中子发射Q值", 'betaMinusOneNeutronEmission')
            add_row_to_table(self, Q_value_table, "β-双中子发射Q值", 'betaMinusTwoNeutronEmission')
            add_row_to_table(self, Q_value_table, "电子捕获单中子发射Q值", 'electronCaptureOneProtonEmission')
            add_row_to_table(self, Q_value_table, "双β-衰变Q值", 'doubleBetaMinus')
            add_row_to_table(self, Q_value_table, "双电子捕获Q值", 'doubleElectronCapture')
            
            # 显示Q值表格（居中）
            self.console.print(Align.center(Q_value_table))
        

        
        # 激发态能量
        if getattr(self.config, 'show_decay_energies', True) if self.config else True:
            excitation_table = self._create_standard_table(
                title=f"{A}{symbol} 激发态性质",
                style=self.theme['excitation']
            )
            add_row_to_table(self, excitation_table, "第一激发态", 'firstExcitedStateEnergy')
            add_row_to_table(self, excitation_table, "第一2+态", 'firstTwoPlusEnergy')
            add_row_to_table(self, excitation_table, "第一4+态", 'firstFourPlusEnergy')
            add_row_to_table(self, excitation_table, "第一4+态/第一2+态", 'firstFourPlusOverFirstTwoPlusEnergy')
            add_row_to_table(self, excitation_table, "第一3-态", 'firstThreeMinusEnergy')

            # 显示表格（居中）
            self.console.print(Align.center(excitation_table))
    
        # 裂变产额
        if getattr(self.config, 'show_fission_yield', True) if self.config else True:
            fission_yield_table = self._create_standard_table(
                title=f"{A}{symbol} 裂变产额",
                style=self.theme['fission_yield']
            )
            add_row_to_table(self, fission_yield_table, "U235独立产额", 'FY235U')
            add_row_to_table(self, fission_yield_table, "U238独立产额", 'FY238U')
            add_row_to_table(self, fission_yield_table, "Pu239独立产额", 'FY239Pu')
            add_row_to_table(self, fission_yield_table, "Cf252独立产额", 'FY252Cf')
            add_row_to_table(self, fission_yield_table, "U235累积产额", 'cFY235U')
            add_row_to_table(self, fission_yield_table, "U238累积产额", 'cFY238U')
            add_row_to_table(self, fission_yield_table, "Pu239累积产额", 'cFY239Pu')
            add_row_to_table(self, fission_yield_table, "Cf252累积产额", 'cFY252Cf')
            
            # 显示表格（居中）
            self.console.print(Align.center(fission_yield_table))
        
        # 其他特性
        
        table = self._create_standard_table(
            title=f"{A}{symbol} 其他特性",
            style=self.theme['info']
        )
                
        if getattr(self.config, 'show_deformation', False) if self.config else False:
            add_row_to_table(self, table, "四极形变 β₂", 'quadrupoleDeformation')
        
        # 配对能隙
        if getattr(self.config, 'show_pairing_gap', True) if self.config else True:
            add_row_to_table(self, table, "配对能隙", 'pairingGap')

        # 半衰期信息
        if getattr(self.config, 'show_halflife', True) if self.config else True:
            ground_state = nuclide_data.get('ground_state')
            if ground_state and hasattr(ground_state, 'halflife') and ground_state.halflife:
                hl = ground_state.halflife
                if hasattr(hl, 'value'):
                    if isinstance(hl.value, str):
                        table.add_row(
                            Text("半衰期", style="halflife"),
                            Text(hl.value, style="value")
                        )
                    else:
                        formatted = self.format_value(hl, style="halflife")
                        if formatted:
                            table.add_row(
                                Text("半衰期", style="halflife"),
                                formatted
                            )
        # 丰度
        if getattr(self.config, 'show_abundance', True) if self.config else True:
            add_row_to_table(self, table, "自然丰度", 'abundance')

        # 自旋宇称
        if getattr(self.config, 'show_spin_parity', True) if self.config else True:
            ground_state = nuclide_data.get('ground_state')
            if ground_state and hasattr(ground_state, 'spin_parity') and ground_state.spin_parity:
                table.add_row(
                    Text("自旋宇称", style="key"),
                    Text(str(ground_state.spin_parity), style="value")
                )
                
        # 质量过剩
        if getattr(self.config, 'show_mass_excess', True) if self.config else True:
            ground_state = nuclide_data.get('ground_state')
            if ground_state and hasattr(ground_state, 'mass_excess') and ground_state.mass_excess:
                formatted = self.format_value(ground_state.mass_excess, "energy")
                if formatted:
                    energy_table.add_row(
                        Text("质量过剩", style="key"),
                        formatted
                    )
        # 显示表格（居中）
        self.console.print(Align.center(table))
        
        # 衰变模式 - 单独显示
        if getattr(self.config, 'show_halflife', True) if self.config else True:
            ground_state = nuclide_data.get('ground_state')
            if ground_state and hasattr(ground_state, 'decay_modes_observed') and ground_state.decay_modes_observed:
                # 定义衰变模式表格的列
                decay_columns = [
                    ("衰变类型", self.key_width, self.theme['decay']),
                    ("分支比", self.value_width, self.theme['value'])
                ]
                
                decay_table = self._create_standard_table(
                    title="衰变模式",
                    show_header=True,
                    style=self.theme['decay'],
                    columns=decay_columns
                )

                precision = getattr(self.config, 'decimal_places', 3) if self.config else 3
                for decay_mode in ground_state.decay_modes_observed:
                    if hasattr(decay_mode, 'mode') and hasattr(decay_mode, 'value'):
                        mode_name = str(decay_mode.mode)
                        value_str = f"{decay_mode.value:.{precision}f}%"
                        
                        # 处理不确定度
                        if hasattr(decay_mode, 'uncertainty') and decay_mode.uncertainty:
                            uncertainty = decay_mode.uncertainty
                            if isinstance(uncertainty, dict):
                                unc_val = uncertainty.get('value', 0) if uncertainty else 0
                                if unc_val and unc_val > 0:
                                    value_str += f" ± {unc_val:.{precision}f}%"
                            elif isinstance(uncertainty, (int, float)) and uncertainty > 0:
                                value_str += f" ± {uncertainty:.{precision}f}%"
                        
                        decay_table.add_row(mode_name, value_str)
                
                self.console.print(Align.center(decay_table))
    
    def print_search_results(self, results: List[NuclideProperties], title: str = "查询结果") -> None:
        """打印搜索结果列表"""
        if not results:
            self.console.print(Panel(
                f"[{self.theme['warning']}]未找到匹配的核素数据[/{self.theme['warning']}]",
                title="❌ 搜索结果",
                style=self.theme['border']
            ))
            return
        
        # 创建结果表格
        search_columns = [
            ("核素", int(self.table_width * 0.2), self.theme['element']),
            ("半衰期", int(self.table_width * 0.35), self.theme['halflife']),
            ("结合能", int(self.table_width * 0.25), self.theme['energy']),
            ("自旋宇称", int(self.table_width * 0.2), self.theme['key'])
        ]
        
        table = self._create_standard_table(
            title=f"📊 {title} ({len(results)} 个结果)",
            show_header=True,
            columns=search_columns
        )
        
        for nuclide in results:
            Z, N, A = nuclide.get('Z', 0), nuclide.get('N', 0), nuclide.get('A', 0)
            symbol = nuclide.get('symbol', 'Unknown')
            nuclide_name = f"{A}{symbol}"
            
            # 半衰期
            halflife_str = "未知"
            ground_state = nuclide.get('ground_state')
            if ground_state and hasattr(ground_state, 'halflife') and ground_state.halflife:
                hl = ground_state.halflife
                if hasattr(hl, 'value'):
                    if isinstance(hl.value, str):
                        halflife_str = hl.value
                    else:
                        formatted = self.format_value(hl, style="halflife")
                        if formatted:
                            halflife_str = formatted.plain
            
            # 结合能
            be_str = "未知"
            be_data = nuclide.get('bindingEnergy')
            if be_data:
                energy_unit = getattr(self.config, 'energy_unit', 'MeV') if self.config else 'MeV'
                formatted_be = self.format_value(be_data, "energy")
                if formatted_be:
                    be_str = formatted_be.plain
            
            # 自旋宇称
            spin_parity_str = "未知"
            if ground_state and hasattr(ground_state, 'spin_parity') and ground_state.spin_parity:
                spin_parity_str = str(ground_state.spin_parity)
            
            table.add_row(nuclide_name, halflife_str, be_str, spin_parity_str)
        
        self.console.print(Align.center(table))
    
    def print_error(self, message: str) -> None:
        """打印错误信息"""
        self.console.print(Panel(
            f"[{self.theme['warning']}]{message}[/{self.theme['warning']}]",
            title="❌ 错误",
            style=self.theme['border']
        ))
    
    def print_success(self, message: str) -> None:
        """打印成功信息"""
        self.console.print(Panel(
            f"[{self.theme['success']}]{message}[/{self.theme['success']}]",
            title="✅ 成功",
            style=self.theme['border']
        ))
    
    def print_info(self, message: str) -> None:
        """打印信息"""
        self.console.print(Panel(
            f"[{self.theme['info']}]{message}[/{self.theme['info']}]",
            title="ℹ️ 信息",
            style=self.theme['border']
        ))
    
    def print_header(self, title: str) -> None:
        """打印程序头部"""
        self.console.print(Rule(Text(f"🔍 {title}", style=self.theme['title']), style=self.theme['title']))

    def print_separator(self) -> None:
        """打印分隔线"""
        self.console.print(Rule(style="dim"))
    
    def show_progress(self, description: str = "处理中..."):
        """显示进度条"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        )
