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

from nuclide_data import NuclideProperties, ELEMENT_SYMBOLS


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
        
        # 定义颜色主题
        self.theme = {
            'title': 'bold cyan',
            'subtitle': 'bold yellow',
            'key': 'bold green',
            'value': 'white',
            'unit': 'dim white',
            'uncertainty': 'dim yellow',
            'warning': 'bold red',
            'success': 'bold green',
            'info': 'bold blue',
            'highlight': 'bold magenta',
            'border': 'dim blue',
            'element': 'bold cyan',
            'energy': 'bold yellow',
            'separation': 'bold green',
            'decay': 'bold red',
            'halflife': 'bold magenta'
        }
    
    def format_value_with_uncertainty(self, data, unit="", style="value", scientific=False):
        """格式化带不确定度的数值，返回Rich Text对象"""
        if not data:
            return None
        
        # 处理 ValueWithUncertainty 对象
        if hasattr(data, 'value') and hasattr(data, 'uncertainty'):
            value, uncertainty = data.value, data.uncertainty
            data_unit = getattr(data, 'unit', unit)
        else:
            return Text(str(data), style=style)
        
        if value is None:
            return None
        
        # 使用最终单位
        final_unit = unit if unit else data_unit
        
        # 格式化数值
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
        
        # 单位
        if final_unit:
            text.append(f" {final_unit}", style=self.theme['unit'])
        
        return text
    
    def print_nuclide_info(self, nuclide_data: NuclideProperties) -> None:
        """打印核素的详细信息 - 使用Rich美观显示"""
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
        
        # 创建主标题
        title = f"[element]{A}{symbol}[/element] [dim]([/dim][key]Z={Z}, N={N}[/key][dim])[/dim]"
        
        # 创建表格来显示核素信息
        table = Table(
            title=title,
            show_header=False,
            box=ROUNDED,
            border_style=self.theme['border'],
            title_style=self.theme['title'],
            padding=(0, 1)
        )
        
        # 添加基本信息行
        if getattr(self.config, 'show_basic_info', True) if self.config else True:
            # 半衰期信息
            if getattr(self.config, 'show_halflife', True) if self.config else True:
                ground_state = nuclide_data.get('ground_state')
                if ground_state and hasattr(ground_state, 'halflife') and ground_state.halflife:
                    hl = ground_state.halflife
                    if hasattr(hl, 'value'):
                        if isinstance(hl.value, str):
                            table.add_row(
                                Text("🕐 半衰期", style="halflife"),
                                Text(hl.value, style="value")
                            )
                        else:
                            formatted = self.format_value_with_uncertainty(hl, style="halflife")
                            if formatted:
                                table.add_row(
                                    Text("🕐 半衰期", style="halflife"),
                                    formatted
                                )
            
            # 自旋宇称
            if getattr(self.config, 'show_spin_parity', True) if self.config else True:
                ground_state = nuclide_data.get('ground_state')
                if ground_state and hasattr(ground_state, 'spin_parity') and ground_state.spin_parity:
                    table.add_row(
                        Text("🌀 自旋宇称", style="key"),
                        Text(str(ground_state.spin_parity), style="value")
                    )
        
        # 能量特性
        if getattr(self.config, 'show_binding_energy', True) if self.config else True:
            be_data = nuclide_data.get('bindingEnergy')
            if be_data:
                energy_unit = getattr(self.config, 'energy_unit', 'MeV') if self.config else 'MeV'
                formatted_be = self.format_value_with_uncertainty(be_data, energy_unit, "energy")
                if formatted_be:
                    table.add_row(
                        Text("⚡ 结合能", style="energy"),
                        formatted_be
                    )
                    
                    # 比结合能
                    if getattr(self.config, 'show_binding_energy_per_nucleon', True) if self.config else True:
                        if hasattr(be_data, 'value') and be_data.value and A > 0:
                            bea = be_data.value / A
                            precision = getattr(self.config, 'decimal_places', 3) if self.config else 3
                            table.add_row(
                                Text("⚡ 比结合能", style="energy"),
                                Text(f"{bea:.{precision}f} {energy_unit}/核子", style="energy")
                            )
        
        # 质量过剩
        if getattr(self.config, 'show_mass_excess', True) if self.config else True:
            ground_state = nuclide_data.get('ground_state')
            if ground_state and hasattr(ground_state, 'mass_excess') and ground_state.mass_excess:
                energy_unit = getattr(self.config, 'energy_unit', 'MeV') if self.config else 'MeV'
                formatted = self.format_value_with_uncertainty(ground_state.mass_excess, energy_unit, "energy")
                if formatted:
                    table.add_row(
                        Text("📏 质量过剩", style="key"),
                        formatted
                    )
        
        # 分离能
        energy_unit = getattr(self.config, 'energy_unit', 'MeV') if self.config else 'MeV'
        
        # 中子分离能
        if getattr(self.config, 'show_neutron_separation', True) if self.config else True:
            data = nuclide_data.get('neutronSeparationEnergy')
            if data:
                formatted = self.format_value_with_uncertainty(data, energy_unit, "separation")
                if formatted:
                    table.add_row(
                        Text("🔵 中子分离能", style="separation"),
                        formatted
                    )
        
        # 质子分离能
        if getattr(self.config, 'show_proton_separation', True) if self.config else True:
            data = nuclide_data.get('protonSeparationEnergy')
            if data:
                formatted = self.format_value_with_uncertainty(data, energy_unit, "separation")
                if formatted:
                    table.add_row(
                        Text("🔴 质子分离能", style="separation"),
                        formatted
                    )
        
        # 双中子分离能
        if getattr(self.config, 'show_two_neutron_separation', True) if self.config else True:
            data = nuclide_data.get('twoNeutronSeparationEnergy')
            if data:
                formatted = self.format_value_with_uncertainty(data, energy_unit, "separation")
                if formatted:
                    table.add_row(
                        Text("🔵🔵 双中子分离能", style="separation"),
                        formatted
                    )
        
        # 双质子分离能
        if getattr(self.config, 'show_two_proton_separation', True) if self.config else True:
            data = nuclide_data.get('twoProtonSeparationEnergy')
            if data:
                formatted = self.format_value_with_uncertainty(data, energy_unit, "separation")
                if formatted:
                    table.add_row(
                        Text("🔴🔴 双质子分离能", style="separation"),
                        formatted
                    )
        
        # 激发态能量
        if getattr(self.config, 'show_decay_energies', True) if self.config else True:
            energy_unit = getattr(self.config, 'energy_unit', 'MeV') if self.config else 'MeV'
            excitation_configs = [
                ("firstExcitedStateEnergy", "💫 第一激发态"),
                ("firstTwoPlusEnergy", "💫 第一2+态"),
                ("firstFourPlusEnergy", "💫 第一4+态"),
                ("firstThreeMinusEnergy", "💫 第一3-态"),
            ]
            
            for data_key, label in excitation_configs:
                data = nuclide_data.get(data_key)
                if data:
                    formatted = self.format_value_with_uncertainty(data, energy_unit, "highlight")
                    if formatted:
                        table.add_row(
                            Text(label, style="highlight"),
                            formatted
                        )
        
        # 其他特性
        if getattr(self.config, 'show_deformation', False) if self.config else False:
            deformation_data = nuclide_data.get('quadrupoleDeformation')
            if deformation_data:
                formatted = self.format_value_with_uncertainty(deformation_data, "", "info")
                if formatted:
                    table.add_row(
                        Text("🔺 四极形变 β₂", style="info"),
                        formatted
                    )
        
        # 配对能隙
        if getattr(self.config, 'show_pairing_gap', True) if self.config else True:
            energy_unit = getattr(self.config, 'energy_unit', 'MeV') if self.config else 'MeV'
            data = nuclide_data.get('pairingGap')
            if data:
                formatted = self.format_value_with_uncertainty(data, energy_unit, "info")
                if formatted:
                    table.add_row(
                        Text("🔗 配对能隙", style="info"),
                        formatted
                    )
        
        # 丰度
        if getattr(self.config, 'show_abundance', True) if self.config else True:
            abundance = nuclide_data.get('abundance')
            if abundance is not None:
                precision = getattr(self.config, 'decimal_places', 3) if self.config else 3
                table.add_row(
                    Text("🌍 自然丰度", style="info"),
                    Text(f"{abundance:.{precision}f}%", style="info")
                )
        
        # 显示表格
        self.console.print(table)
        
        # 衰变模式 - 单独显示
        if getattr(self.config, 'show_halflife', True) if self.config else True:
            ground_state = nuclide_data.get('ground_state')
            if ground_state and hasattr(ground_state, 'decay_modes_observed') and ground_state.decay_modes_observed:
                decay_table = Table(
                    title="☢️ 衰变模式",
                    show_header=True,
                    box=ROUNDED,
                    border_style=self.theme['decay'],
                    title_style=self.theme['decay']
                )
                decay_table.add_column("衰变类型", style=self.theme['decay'])
                decay_table.add_column("分支比", style=self.theme['value'])
                
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
                
                self.console.print(decay_table)
    
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
        table = Table(
            title=f"📊 {title} ({len(results)} 个结果)",
            show_header=True,
            box=ROUNDED,
            border_style=self.theme['border'],
            title_style=self.theme['title']
        )
        
        table.add_column("核素", style=self.theme['element'], width=12)
        table.add_column("半衰期", style=self.theme['halflife'], width=20)
        table.add_column("结合能", style=self.theme['energy'], width=15)
        table.add_column("自旋宇称", style=self.theme['key'], width=12)
        
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
                        formatted = self.format_value_with_uncertainty(hl, style="halflife")
                        if formatted:
                            halflife_str = formatted.plain
            
            # 结合能
            be_str = "未知"
            be_data = nuclide.get('bindingEnergy')
            if be_data:
                energy_unit = getattr(self.config, 'energy_unit', 'MeV') if self.config else 'MeV'
                formatted_be = self.format_value_with_uncertainty(be_data, energy_unit, "energy")
                if formatted_be:
                    be_str = formatted_be.plain
            
            # 自旋宇称
            spin_parity_str = "未知"
            if ground_state and hasattr(ground_state, 'spin_parity') and ground_state.spin_parity:
                spin_parity_str = str(ground_state.spin_parity)
            
            table.add_row(nuclide_name, halflife_str, be_str, spin_parity_str)
        
        self.console.print(table)
    
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
        self.console.print(Rule(f"🧬 {title}", style=self.theme['title']))
    
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
