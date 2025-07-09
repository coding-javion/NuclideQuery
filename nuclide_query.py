#!/usr/bin/env python3
"""
核素查询工具
输入质子数和中子数，查询实验上的结合能、S2N和S2P
"""

import json
import sys
import argparse
import re
from typing import Dict, Optional, Tuple
from pathlib import Path
from nuclide_data import ELEMENT_SYMBOLS, NuclideProperties
from database_loader import NuclideDataLoader
from rich_output import NuclideRichPrinter
from config import QueryConfig, DATA_FILE_PATH


def parse_nuclide_string(nuclide_str: str) -> tuple:
    """
    解析元素符号+质量数格式的核素字符串
    
    参数:
        nuclide_str: 格式如 "fe56", "al31", "pb208" 等
        
    返回:
        (Z, N) 元组，如果解析失败返回 (None, None)
    """
    # 使用正则表达式匹配元素符号和质量数
    match = re.match(r'^([a-zA-Z]+)(\d+)$', nuclide_str.strip())
    
    if not match:
        return None, None
    
    element_symbol = match.group(1).capitalize()  # 首字母大写
    mass_number = int(match.group(2))
    
    # 查找元素符号对应的质子数
    Z = None
    for atomic_number, symbol in ELEMENT_SYMBOLS.items():
        if symbol.lower() == element_symbol.lower():
            Z = atomic_number
            break
    
    if Z is None:
        return None, None
    
    # 计算中子数 N = A - Z
    N = mass_number - Z
    
    if N < 0:
        return None, None
    
    return Z, N
    
    
class NuclideQuery:
    """核素查询类"""
    
    def __init__(self, data_file: Optional[str] = None, query_config: QueryConfig = QueryConfig()):
        """
        初始化查询器
        
        参数:
            data_file: JSON数据文件路径
            query_config: 查询配置名称
        """
        if data_file is None:
            data_file = DATA_FILE_PATH
        self.data_loader = NuclideDataLoader(data_file, query_config)
        self.rich_printer = NuclideRichPrinter(query_config)
        
    def query_nuclide(self, Z: int, N: int) -> Optional[NuclideProperties]:
        """
        查询指定质子数和中子数的核素数据
        
        参数:
            Z: 质子数
            N: 中子数
            
        返回:
            包含核素信息的NuclideProperties，如果未找到则返回None
        """
        data = self.data_loader.get_nuclide_data(Z, N)
        return data if data else None
    
    def print_nuclide_info(self, Z: int, N: int) -> bool:
        """
        打印核素的详细信息
        
        参数:
            Z: 质子数
            N: 中子数
            
        返回:
            是否找到对应的核素
        """
        data = self.query_nuclide(Z, N)
        
        if not data:
            self.rich_printer.print_error(f"未找到 Z={Z}, N={N} 的核素数据")
            return False
        
        # 使用Rich美观输出
        self.rich_printer.print_nuclide_info(data)
        
        return True
    
    def get_summary_data(self, Z: int, N: int) -> Optional[Dict]:
        """
        获取核素的摘要数据（用于快速查询）
        
        参数:
            Z: 质子数
            N: 中子数
            
        返回:
            包含核素摘要信息的字典
        """
        data = self.query_nuclide(Z, N)
        
        if not data:
            return None
        
        A = Z + N
        element_symbol = ELEMENT_SYMBOLS.get(Z, f"X{Z}")
        
        # 构建摘要数据字典
        binding_energy_val = data.get('binding_energy')
        s2n_val = data.get('two_neutron_separation_energy')
        s2p_val = data.get('two_proton_separation_energy')
        sn_val = data.get('neutron_separation_energy')
        sp_val = data.get('proton_separation_energy')
        
        summary = {
            'Z': Z,
            'N': N,
            'A': A,
            'symbol': element_symbol,
            'binding_energy': binding_energy_val.value if binding_energy_val else None,
            'binding_energy_per_nucleon': data.get('binding_energy_per_nucleon'),
            'S2N': s2n_val.value if s2n_val else None,
            'S2P': s2p_val.value if s2p_val else None,
            'SN': sn_val.value if sn_val else None,
            'SP': sp_val.value if sp_val else None,
            'spin_parity': data.get('spin_parity'),
        }
        
        return summary


def main():
    """主函数 - 支持命令行参数和交互式查询"""
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='核素实验数据查询工具')
    parser.add_argument('input1', nargs='?', help='质子数或元素符号+质量数 (如: 26 或 fe56)')
    parser.add_argument('input2', nargs='?', help='中子数 (仅当第一个参数为质子数时需要)')
    parser.add_argument('-m', '--mode', type=str, default='basic', 
                       choices=['basic', 'detailed', 'minimal'],
                       help='查询模式 (basic/detailed/minimal)')
    
    args = parser.parse_args()
    
    # 创建Rich控制台并显示程序头部
    from rich.console import Console
    console = Console()
    
    # 初始化查询器
    try:
        query_config = QueryConfig(mode=args.mode)
        query_tool = NuclideQuery(query_config=query_config)
        query_tool.rich_printer.print_header("核素实验数据查询工具")
    except Exception as e:
        # 创建临时printer来显示错误
        from rich_output import NuclideRichPrinter
        temp_printer = NuclideRichPrinter()
        temp_printer.print_error(f"初始化失败: {e}")
        return
    
    # 解析命令行参数
    if args.input1 is not None:
        Z = N = None
        
        if args.input2 is not None:
            # 两个参数：质子数和中子数
            try:
                Z = int(args.input1)
                N = int(args.input2)
                if Z <= 0 or N < 0:
                    query_tool.rich_printer.print_error("质子数必须大于0，中子数必须大于等于0")
                    return
            except ValueError:
                query_tool.rich_printer.print_error("请输入有效的整数")
                return
        else:
            # 单个参数：尝试解析为质子数或元素符号+质量数
            try:
                # 先尝试作为质子数解析
                Z = int(args.input1)
                query_tool.rich_printer.print_error("缺少中子数参数")
                return
            except ValueError:
                # 作为元素符号+质量数解析
                Z, N = parse_nuclide_string(args.input1)
                if Z is None or N is None:
                    query_tool.rich_printer.print_error(f"无法解析核素字符串: {args.input1}")
                    query_tool.rich_printer.print_info("格式应为: 元素符号+质量数，如 fe56, al31, pb208")
                    return
        
        # 显示解析结果
        element_symbol = ELEMENT_SYMBOLS.get(Z, f"X{Z}")
        A = Z + N
        # print(f"查询核素: {A}{element_symbol} (Z={Z}, N={N})")
        # print(f"查询模式: {args.mode}")
        query_tool.print_nuclide_info(Z, N)
        return
    
    # 进入交互模式
    query_tool.rich_printer.print_separator()
    query_tool.rich_printer.print_info("进入交互模式 (输入 'q' 退出)")
    
    while True:
        query_tool.rich_printer.print_separator()
        
        # 获取用户输入
        try:
            user_input = input("🔬 请输入质子数: ").strip()
            if user_input.lower() == 'q':
                break
                
            Z = int(user_input)
            
            user_input = input("⚛️  请输入中子数: ").strip()
            if user_input.lower() == 'q':
                break
                
            N = int(user_input)
            
        except ValueError:
            query_tool.rich_printer.print_error("请输入有效的整数!")
            continue
        except KeyboardInterrupt:
            query_tool.rich_printer.print_info("程序被用户中断")
            break
        
        # 查询并显示结果
        query_tool.print_nuclide_info(Z, N)


if __name__ == "__main__":
    main()
