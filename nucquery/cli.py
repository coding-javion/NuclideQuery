#!/usr/bin/env python3
"""
核素查询工具 - 命令行接口
"""

import argparse
from typing import Optional, Tuple, List
from .nuclide_data import ELEMENT_SYMBOLS
from .nuclide import Nuclide
from .data_source import list_sources
from .rich_output import NuclideRichPrinter
from .config import QueryConfig
from .nuclide_query import NuclideQuery, parse_nuclide_string


def print_nuclide_info(printer: NuclideRichPrinter, query_tool: NuclideQuery, Z: int, N: int) -> bool:
    """
    打印核素的详细信息
    
    参数:
        printer: RichPrinter 对象
        query_tool: NuclideQuery 对象
        Z: 质子数
        N: 中子数
        
    返回:
        是否找到对应的核素
    """
    nuc = query_tool.query_nuclide(Z, N)
    
    if not nuc or not nuc.data:
        printer.print_error(f"未找到 Z={Z}, N={N} 的核素数据")
        return False
    
    # 使用Rich美观输出
    printer.print_nuclide_info(nuc.data)
    
    return True

def print_nuclides_info(printer: NuclideRichPrinter, nuclides: List[Nuclide]) -> None:
    """
    打印多个核素的信息
    
    参数:
        printer: RichPrinter 对象
        nuclides: Nuclide 对象列表
    """
    if not nuclides:
        printer.print_error("未找到任何核素数据")
        return
    
    printer.print_info(f"找到 {len(nuclides)} 个核素:")
    
    for nuc in nuclides:
        if nuc.data:
            printer.print_nuclide_info(nuc.data)
            printer.print_separator()

def parse_range(range_str: str) -> Tuple[Optional[int], Optional[int]]:
    """
    解析范围字符串
    
    参数:
        range_str: 格式为 "min-max" 或 "min,max"
        
    返回:
        (min_val, max_val) 元组，解析失败返回 (None, None)
    """
    try:
        # 支持 - 和 , 作为分隔符
        if '-' in range_str:
            parts = range_str.split('-')
        elif ',' in range_str:
            parts = range_str.split(',')
        else:
            return None, None
        
        if len(parts) != 2:
            return None, None
        
        min_val = int(parts[0].strip())
        max_val = int(parts[1].strip())
        
        if min_val > max_val:
            min_val, max_val = max_val, min_val  # 交换顺序
        
        return min_val, max_val
    
    except ValueError:
        return None, None


def parse_nuclide_list(nuclides_str: str) -> List[Tuple[int, int]]:
    """
    解析核素列表字符串
    
    参数:
        nuclides_str: 格式为 "Z1,N1;Z2,N2;..." 或 "fe56,ni60,pb208"
        
    返回:
        [(Z1, N1), (Z2, N2), ...] 列表
    """
    nuclide_list = []
    
    # 分割核素
    nuclides = nuclides_str.split(';') if ';' in nuclides_str else nuclides_str.split(',')
    
    for nuclide in nuclides:
        nuclide = nuclide.strip()
        if not nuclide:
            continue
        
        # 尝试解析为 Z,N 格式
        if ',' in nuclide:
            try:
                parts = nuclide.split(',')
                if len(parts) == 2:
                    Z = int(parts[0].strip())
                    N = int(parts[1].strip())
                    if Z > 0 and N >= 0:
                        nuclide_list.append((Z, N))
                        continue
            except ValueError:
                pass
        
        # 尝试解析为元素符号+质量数格式
        Z, N = parse_nuclide_string(nuclide)
        if Z is not None and N is not None:
            nuclide_list.append((Z, N))
    
    return nuclide_list


def main():
    """主函数 - 支持命令行参数和交互式查询"""
    # 设置命令行参数
    parser = argparse.ArgumentParser(
        description='核素数据查询工具（支持实验和理论数据）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  单核素查询:
    %(prog)s fe56                    # 查询铁-56
    %(prog)s 26 30                   # 查询 Z=26, N=30 (铁-56)
    
  批量查询:
    %(prog)s -b isotopes 26          # 查询铁的所有同位素
    %(prog)s -b isotones 50          # 查询 N=50 的所有同中子素
    %(prog)s -b range --z-range 1-10 # 查询 Z=1~10 的所有核素
    %(prog)s -b list --nuclides fe56,ni60,pb208
    
  使用理论数据:
    %(prog)s -s SKMS fe56            # 使用 SKMS 数据源查询
    %(prog)s --list-sources          # 列出所有可用数据源
''')
    
    # 通用选项
    parser.add_argument('-m', '--mode', type=str, default='basic', 
                       choices=['basic', 'detailed', 'minimal'],
                       help='输出详细程度 (默认: basic)')
    parser.add_argument('-s', '--source', type=str, default='experiment',
                       help='数据源 (默认: experiment，可选: SKMS/UNEDF0/UNEDF1/SLY4/SKP/SV-MIN)')
    parser.add_argument('--list-sources', action='store_true',
                       help='列出所有可用数据源')

    # 批量查询模式
    parser.add_argument('-b', '--batch', type=str, default='none',
                        choices=['none', 'isotopes', 'isotones', 'range', 'list'],
                        metavar='MODE',
                        help='批量查询模式: isotopes(同位素)/isotones(同中子素)/range(区域)/list(列表)')
    
    # 批量查询参数 (与 -b 配合使用)
    batch_group = parser.add_argument_group('批量查询参数', '以下参数需配合 -b/--batch 使用')
    batch_group.add_argument('--z-range', type=str, metavar='MIN-MAX',
                            help='质子数范围 (用于 -b range)，如: 1-10 或 1,10')
    batch_group.add_argument('--n-range', type=str, metavar='MIN-MAX',
                            help='中子数范围 (用于 -b range)，如: 1-10 或 1,10')
    batch_group.add_argument('--nuclides', type=str, metavar='LIST',
                            help='核素列表 (用于 -b list)，如: fe56,ni60,pb208 或 26,30;28,32')

    # 单个核素查询参数
    parser.add_argument('input1', nargs='?', metavar='核素',
                       help='质子数 或 元素符号+质量数 (如: 26 或 fe56)')
    parser.add_argument('input2', nargs='?', metavar='中子数',
                       help='中子数 (仅当第一个参数为质子数时需要)')
    
    args = parser.parse_args()
    
    # 处理 --list-sources 参数
    if args.list_sources:
        print("可用数据源:")
        for src in list_sources():
            print(f"  - {src}")
        return
    
    # 初始化查询器
    try:
        query_config = QueryConfig(mode=args.mode)
        printer = NuclideRichPrinter(query_config)
        query_tool = NuclideQuery(source=args.source)
        source_info = f"数据源: {args.source}" if args.source != 'experiment' else ""
        printer.print_header(f"核素数据查询工具 {source_info}".strip())
    except Exception as e:
        # 创建临时printer来显示错误
        temp_printer = NuclideRichPrinter()
        temp_printer.print_error(f"初始化失败: {e}")
        return
    
    # 解析命令行参数
    if args.batch != 'none':
        # 批量查询模式
        if args.batch == 'isotopes':
            # 同位素查询
            if not args.input1:
                printer.print_error("同位素查询需要指定质子数")
                return
            
            try:
                Z = int(args.input1)
                N_min = N_max = None
                
                # 解析中子数范围
                if args.n_range:
                    N_min, N_max = parse_range(args.n_range)
                    if N_min is None or N_max is None:
                        printer.print_error("中子数范围格式错误，应为: min-max 或 min,max")
                        return
                
                results = query_tool.query_isotopes(Z, N_min, N_max)
                element_symbol = ELEMENT_SYMBOLS.get(Z, f"X{Z}")
                printer.print_info(f"查询元素 {element_symbol} (Z={Z}) 的同位素:")
                print_nuclides_info(printer, results)
                
            except ValueError:
                printer.print_error("请输入有效的质子数")
                return
        
        elif args.batch == 'isotones':
            # 同中子素查询
            if not args.input1:
                printer.print_error("同中子素查询需要指定中子数")
                return
            
            try:
                N = int(args.input1)
                Z_min = Z_max = None
                
                # 解析质子数范围
                if args.z_range:
                    Z_min, Z_max = parse_range(args.z_range)
                    if Z_min is None or Z_max is None:
                        printer.print_error("质子数范围格式错误，应为: min-max 或 min,max")
                        return
                
                results = query_tool.query_isotones(N, Z_min, Z_max)
                printer.print_info(f"查询中子数 N={N} 的同中子素:")
                print_nuclides_info(printer, results)
                
            except ValueError:
                printer.print_error("请输入有效的中子数")
                return
        
        elif args.batch == 'list':
            # 核素列表查询
            if not args.nuclides:
                printer.print_error("列表查询需要使用 --nuclides 参数指定核素列表")
                printer.print_info("格式: --nuclides 'Z1,N1;Z2,N2;...' 或 --nuclides 'fe56,ni60,pb208'")
                return
            
            nuclide_list = parse_nuclide_list(args.nuclides)
            if not nuclide_list:
                printer.print_error("核素列表格式错误")
                printer.print_info("格式: 'Z1,N1;Z2,N2;...' 或 'fe56,ni60,pb208'")
                return
            
            results = query_tool.query_from_list(nuclide_list)
            printer.print_info(f"查询指定的 {len(nuclide_list)} 个核素:")
            print_nuclides_info(printer, results)
        
        elif args.batch == 'range':
            # 区域范围查询
            Z_min = Z_max = N_min = N_max = None
            
            # 解析质子数范围
            if args.z_range:
                Z_min, Z_max = parse_range(args.z_range)
                if Z_min is None or Z_max is None:
                    printer.print_error("质子数范围格式错误，应为: min-max 或 min,max")
                    return
            
            # 解析中子数范围
            if args.n_range:
                N_min, N_max = parse_range(args.n_range)
                if N_min is None or N_max is None:
                    printer.print_error("中子数范围格式错误，应为: min-max 或 min,max")
                    return
            
            # 至少需要一个范围参数
            if Z_min is None and N_min is None:
                printer.print_error("区域范围查询需要指定 --z-range 或 --n-range")
                printer.print_info("示例: python nuclide_query.py -b range --z-range 1-10 --n-range 1-10")
                return
            
            # 如果只指定了一个范围，使用该范围查询所有可能的核素
            if Z_min is None:
                Z_min, Z_max = 1, 118  # 默认全部元素
            if N_min is None:
                N_min, N_max = 0, 200  # 默认全部中子数
            
            # 确保 Z_max 和 N_max 不为 None (类型检查)
            if Z_max is None: Z_max = 118
            if N_max is None: N_max = 200

            results = query_tool.query_range(Z_min, Z_max, N_min, N_max)
            printer.print_info(f"查询区域 Z=[{Z_min}-{Z_max}], N=[{N_min}-{N_max}]:")
            if results:
                print_nuclides_info(printer, results)
            else:
                printer.print_error("未找到任何核素数据")
        
        return
    
    elif args.input1 is not None:
        Z = N = None
        
        if args.input2 is not None:
            # 两个参数：质子数和中子数
            try:
                Z = int(args.input1)
                N = int(args.input2)
                if Z <= 0 or N < 0:
                    printer.print_error("质子数必须大于0，中子数必须大于等于0")
                    return
            except ValueError:
                printer.print_error("请输入有效的整数")
                return
        else:
            # 单个参数：尝试解析为质子数或元素符号+质量数
            try:
                # 先尝试作为质子数解析
                Z = int(args.input1)
                printer.print_error("缺少中子数参数")
                return
            except ValueError:
                # 作为元素符号+质量数解析
                Z, N = parse_nuclide_string(args.input1)
                if Z is None or N is None:
                    printer.print_error(f"无法解析核素字符串: {args.input1}")
                    printer.print_info("格式应为: 元素符号+质量数，如 fe56, al31, pb208")
                    return
        
        # 显示解析结果
        element_symbol = ELEMENT_SYMBOLS.get(Z, f"X{Z}")
        A = Z + N
        # print(f"查询核素: {A}{element_symbol} (Z={Z}, N={N})")
        # print(f"查询模式: {args.mode}")
        print_nuclide_info(printer, query_tool, Z, N)
        return
    
    # 进入交互模式
    printer.print_separator()
    printer.print_info("进入交互模式 (输入 'q' 退出)")
    
    while True:
        printer.print_separator()
        
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
            printer.print_error("请输入有效的整数!")
            continue
        except KeyboardInterrupt:
            printer.print_info("程序被用户中断")
            break
        
        # 查询并显示结果
        print_nuclide_info(printer, query_tool, Z, N)


if __name__ == "__main__":
    main()
