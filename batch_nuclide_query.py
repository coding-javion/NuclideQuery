#!/usr/bin/env python3
"""
批量核素查询工具
支持批量查询多个核素的结合能、S2N和S2P
"""

import csv
import json
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path
from nuclide_query import NuclideQuery
from nuclide_data import ELEMENT_SYMBOLS, NuclideProperties
import config


class BatchNuclideQuery:
    """批量核素查询类"""
    
    def __init__(self, data_file: Optional[str] = None, query_config: str = "basic"):
        """
        初始化批量查询器
        
        参数:
            data_file: JSON数据文件路径
            query_config: 查询配置名称
        """
        if data_file is None:
            data_file = config.DATA_FILE_PATH
        self.query_tool = NuclideQuery(data_file, query_config)
    
    def query_range(self, Z_min: int, Z_max: int, N_min: int, N_max: int) -> List[Dict]:
        """
        查询指定范围内的所有核素
        
        参数:
            Z_min, Z_max: 质子数范围
            N_min, N_max: 中子数范围
            
        返回:
            核素数据列表
        """
        results = []
        
        for Z in range(Z_min, Z_max + 1):
            for N in range(N_min, N_max + 1):
                data = self.query_tool.get_summary_data(Z, N)
                if data:
                    results.append(data)
        
        return results
    
    def query_isotopes(self, Z: int, N_min: Optional[int] = None, N_max: Optional[int] = None) -> List[Dict]:
        """
        查询指定元素的所有同位素
        
        参数:
            Z: 质子数
            N_min, N_max: 中子数范围（可选）
            
        返回:
            同位素数据列表
        """
        results = []
        
        # 如果没有指定中子数范围，使用合理的默认值
        if N_min is None:
            N_min = max(1, Z - 10)
        if N_max is None:
            N_max = Z + 50
        
        for N in range(N_min, N_max + 1):
            data = self.query_tool.get_summary_data(Z, N)
            if data:
                results.append(data)
        
        return results
    
    def query_isotones(self, N: int, Z_min: Optional[int] = None, Z_max: Optional[int] = None) -> List[Dict]:
        """
        查询指定中子数的所有同中子素
        
        参数:
            N: 中子数
            Z_min, Z_max: 质子数范围（可选）
            
        返回:
            同中子素数据列表
        """
        results = []
        
        # 如果没有指定质子数范围，使用合理的默认值
        if Z_min is None:
            Z_min = max(1, N - 10)
        if Z_max is None:
            Z_max = min(118, N + 10)
        
        for Z in range(Z_min, Z_max + 1):
            data = self.query_tool.get_summary_data(Z, N)
            if data:
                results.append(data)
        
        return results
    
    def query_from_list(self, nuclide_list: List[Tuple[int, int]]) -> List[Dict]:
        """
        从核素列表查询数据
        
        参数:
            nuclide_list: [(Z, N), ...] 格式的核素列表
            
        返回:
            核素数据列表
        """
        results = []
        
        for Z, N in nuclide_list:
            data = self.query_tool.get_summary_data(Z, N)
            if data:
                results.append(data)
        
        return results
    
    def save_to_csv(self, results: List[Dict], filename: str = "nuclide_results.csv"):
        """
        将查询结果保存为CSV文件
        
        参数:
            results: 查询结果列表
            filename: 输出文件名
        """
        if not results:
            print("没有数据可保存")
            return
        
        # 定义CSV列头
        fieldnames = [
            'Z', 'N', 'A', 'Symbol', 'Nuclide',
            'BE (MeV)', 'BE/A (MeV)', 
            'S2N (MeV)', 'S2P (MeV)', 'SN (MeV)', 'SP (MeV)'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for data in results:
                row = {
                    'Z': data['Z'],
                    'N': data['N'],
                    'A': data['A'],
                    'Symbol': data['symbol'],
                    'Nuclide': f"{data['A']}{data['symbol']}",
                    'BE (MeV)': f"{data['binding_energy']:.3f}" if data['binding_energy'] is not None else "N/A",
                    'BE/A (MeV)': f"{data['binding_energy_per_nucleon']:.3f}" if data['binding_energy_per_nucleon'] is not None else "N/A",
                    'S2N (MeV)': f"{data['S2N']:.3f}" if data['S2N'] is not None else "N/A",
                    'S2P (MeV)': f"{data['S2P']:.3f}" if data['S2P'] is not None else "N/A",
                    'SN (MeV)': f"{data['SN']:.3f}" if data['SN'] is not None else "N/A",
                    'SP (MeV)': f"{data['SP']:.3f}" if data['SP'] is not None else "N/A"
                }
                writer.writerow(row)
        
        print(f"已保存 {len(results)} 条数据到 {filename}")
    
    def print_results_table(self, results: List[Dict], max_rows: int = 20):
        """
        以表格形式打印查询结果
        
        参数:
            results: 查询结果列表
            max_rows: 最大显示行数
        """
        if not results:
            print("没有找到数据")
            return
        
        # 表头
        print(f"\n{'='*120}")
        print(f"{'Nuclide':<10} {'Z':<3} {'N':<3} {'A':<3} {'BE (MeV)':<10} {'BE/A':<8} {'S2N (MeV)':<10} {'S2P (MeV)':<10} {'SN (MeV)':<9} {'SP (MeV)':<9}")
        print(f"{'='*120}")
        
        # 数据行
        for i, data in enumerate(results[:max_rows]):
            nuclide = f"{data['A']}{data['symbol']}"
            be = f"{data['binding_energy']:.3f}" if data['binding_energy'] is not None else "N/A"
            bea = f"{data['binding_energy_per_nucleon']:.3f}" if data['binding_energy_per_nucleon'] is not None else "N/A"
            s2n = f"{data['S2N']:.3f}" if data['S2N'] is not None else "N/A"
            s2p = f"{data['S2P']:.3f}" if data['S2P'] is not None else "N/A"
            sn = f"{data['SN']:.3f}" if data['SN'] is not None else "N/A"
            sp = f"{data['SP']:.3f}" if data['SP'] is not None else "N/A"
            
            print(f"{nuclide:<10} {data['Z']:<3} {data['N']:<3} {data['A']:<3} {be:<10} {bea:<8} {s2n:<10} {s2p:<10} {sn:<9} {sp:<9}")
        
        if len(results) > max_rows:
            print(f"... 还有 {len(results) - max_rows} 条数据未显示")
        
        print(f"{'='*120}")
        print(f"总计: {len(results)} 个核素")


def main():
    """主函数 - 交互式批量查询"""
    print("批量核素查询工具")
    print("="*50)
    
    # 初始化查询器
    try:
        batch_query = BatchNuclideQuery()
    except Exception as e:
        print(f"初始化失败: {e}")
        return
    
    while True:
        print("\n请选择查询模式:")
        print("1. 范围查询 (Z和N范围)")
        print("2. 同位素查询 (相同Z)")
        print("3. 同中子素查询 (相同N)")
        print("4. 自定义列表查询")
        print("5. 退出")
        
        try:
            choice = input("请输入选择 (1-5): ").strip()
            
            if choice == '5':
                break
            
            results = []
            
            if choice == '1':
                # 范围查询
                Z_min = int(input("请输入最小质子数: "))
                Z_max = int(input("请输入最大质子数: "))
                N_min = int(input("请输入最小中子数: "))
                N_max = int(input("请输入最大中子数: "))
                
                results = batch_query.query_range(Z_min, Z_max, N_min, N_max)
                
            elif choice == '2':
                # 同位素查询
                Z = int(input("请输入质子数: "))
                N_min_input = input("请输入最小中子数 (回车使用默认): ").strip()
                N_max_input = input("请输入最大中子数 (回车使用默认): ").strip()
                
                N_min = int(N_min_input) if N_min_input else None
                N_max = int(N_max_input) if N_max_input else None
                
                results = batch_query.query_isotopes(Z, N_min, N_max)
                
            elif choice == '3':
                # 同中子素查询
                N = int(input("请输入中子数: "))
                Z_min_input = input("请输入最小质子数 (回车使用默认): ").strip()
                Z_max_input = input("请输入最大质子数 (回车使用默认): ").strip()
                
                Z_min = int(Z_min_input) if Z_min_input else None
                Z_max = int(Z_max_input) if Z_max_input else None
                
                results = batch_query.query_isotones(N, Z_min, Z_max)
                
            elif choice == '4':
                # 自定义列表查询
                print("请输入核素列表，格式: Z,N (每行一个，空行结束)")
                nuclide_list = []
                while True:
                    line = input("Z,N: ").strip()
                    if not line:
                        break
                    try:
                        Z, N = map(int, line.split(','))
                        nuclide_list.append((Z, N))
                    except ValueError:
                        print("格式错误，请输入 Z,N 格式")
                
                results = batch_query.query_from_list(nuclide_list)
            
            else:
                print("无效选择")
                continue
            
            if results:
                # 显示结果
                batch_query.print_results_table(results)
                
                # 询问是否保存
                save = input("\n是否保存为CSV文件? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("输入文件名 (回车使用默认): ").strip()
                    if not filename:
                        filename = "nuclide_results.csv"
                    batch_query.save_to_csv(results, filename)
            else:
                print("没有找到符合条件的核素数据")
                
        except ValueError:
            print("请输入有效的数字!")
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    main()
