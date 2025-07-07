#!/usr/bin/env python3
"""
核素查询使用示例
演示如何使用 nuclide_query.py 和 batch_nuclide_query.py
"""

from nuclide_query import NuclideQuery
from batch_nuclide_query import BatchNuclideQuery
import config


def example_single_query():
    """单个核素查询示例"""
    print("=" * 60)
    print("单个核素查询示例")
    print("=" * 60)
    
    # 初始化查询器 - 使用详细配置
    query_tool = NuclideQuery(query_config="detailed")
    
    # 查询一些常见核素
    test_nuclides = [
        (1, 0),   # 氢-1
        (1, 1),   # 氘
        (2, 2),   # 氦-4
        (6, 6),   # 碳-12
        (8, 8),   # 氧-16
        (26, 30), # 铁-56
        (82, 126), # 铅-208
    ]
    
    for Z, N in test_nuclides:
        print(f"\n查询 Z={Z}, N={N}:")
        found = query_tool.print_nuclide_info(Z, N)
        if not found:
            print(f"未找到 Z={Z}, N={N} 的数据")


def example_batch_query():
    """批量查询示例"""
    print("\n" + "=" * 60)
    print("批量查询示例")
    print("=" * 60)
    
    # 初始化批量查询器
    batch_query = BatchNuclideQuery(query_config="basic")
    
    # 示例1: 查询铁的同位素 (Z=26)
    print("\n1. 铁的同位素 (Z=26):")
    iron_isotopes = batch_query.query_isotopes(26, 28, 35)
    batch_query.print_results_table(iron_isotopes, max_rows=10)
    
    # 示例2: 查询幻数N=82的同中子素
    print("\n2. 幻数 N=82 的同中子素:")
    magic_isotones = batch_query.query_isotones(82, 50, 90)
    batch_query.print_results_table(magic_isotones, max_rows=10)
    
    # 示例3: 查询轻核范围
    print("\n3. 轻核范围 (Z=1-10, N=1-10):")
    light_nuclei = batch_query.query_range(1, 10, 1, 10)
    batch_query.print_results_table(light_nuclei, max_rows=15)
    
    # 示例4: 自定义核素列表
    print("\n4. 双幻数核:")
    double_magic = [
        (2, 2),   # He-4
        (8, 8),   # O-16
        (20, 20), # Ca-40
        (20, 28), # Ca-48
        (50, 82), # Sn-132
        (82, 126), # Pb-208
    ]
    double_magic_results = batch_query.query_from_list(double_magic)
    batch_query.print_results_table(double_magic_results)


def example_data_analysis():
    """数据分析示例"""
    print("\n" + "=" * 60)
    print("数据分析示例")
    print("=" * 60)
    
    batch_query = BatchNuclideQuery()
    
    # 获取一些数据进行分析
    results = batch_query.query_range(20, 30, 20, 40)
    
    if results:
        print(f"\n分析 {len(results)} 个核素的数据:")
        
        # 统计有效数据
        valid_be = [r for r in results if r['binding_energy'] is not None]
        valid_s2n = [r for r in results if r['S2N'] is not None]
        valid_s2p = [r for r in results if r['S2P'] is not None]
        
        print(f"有结合能数据的核素: {len(valid_be)}")
        print(f"有S2N数据的核素: {len(valid_s2n)}")
        print(f"有S2P数据的核素: {len(valid_s2p)}")
        
        if valid_be:
            be_values = [r['binding_energy'] for r in valid_be]
            print(f"结合能范围: {min(be_values):.3f} - {max(be_values):.3f} MeV")
            print(f"平均结合能: {sum(be_values)/len(be_values):.3f} MeV")
        
        if valid_s2n:
            s2n_values = [r['S2N'] for r in valid_s2n]
            print(f"S2N范围: {min(s2n_values):.3f} - {max(s2n_values):.3f} MeV")
            print(f"平均S2N: {sum(s2n_values)/len(s2n_values):.3f} MeV")
        
        # 找出最大结合能的核素
        if valid_be:
            max_be_nuclide = max(valid_be, key=lambda x: x['binding_energy'])
            print(f"\n最大结合能核素: {max_be_nuclide['A']}{max_be_nuclide['symbol']} "
                  f"(BE={max_be_nuclide['binding_energy']:.3f} MeV)")


def example_configuration_system():
    """配置系统示例"""
    print("\n" + "=" * 60)
    print("配置系统示例")
    print("=" * 60)
    
    # 演示不同的配置模式
    configs = ["basic", "detailed"]
    
    Z, N = 26, 30  # 铁-56
    
    for config_name in configs:
        print(f"\n使用 '{config_name}' 配置查询 Fe-56:")
        print("-" * 40)
        
        query_tool = NuclideQuery(query_config=config_name)
        query_tool.print_nuclide_info(Z, N)
    
    # 演示自定义配置
    print(f"\n使用自定义配置查询 Fe-56:")
    print("-" * 40)
    
    from nuclide_data import create_custom_config
    custom_config = create_custom_config(
        show_basic_info=True,
        show_binding_energy=True,
        show_binding_energy_per_nucleon=True,
        show_neutron_separation=True,
        show_proton_separation=True,
        show_two_neutron_separation=False,
        show_two_proton_separation=False,
        show_decay_mode=True,
        show_halflife=True,
        show_spin_parity=True,
        show_uncertainties=False,
        decimal_places=2
    )
    
    # 注意：这里我们需要手动设置配置，因为NuclideQuery不直接接受自定义配置对象
    query_tool = NuclideQuery(query_config="basic")
    query_tool.data_loader.query_config = custom_config
    query_tool.print_nuclide_info(Z, N)


def main():
    """主函数"""
    try:
        print("核素查询工具使用示例")
        print("确保 nndc_nudat_data_export.json 文件存在于当前目录")
        
        # 运行示例
        example_single_query()
        example_batch_query()
        example_data_analysis()
        example_configuration_system()
        
        print("\n" + "=" * 60)
        print("示例运行完成!")
        print("您可以运行以下脚本进行交互式查询:")
        print("- python nuclide_query.py                     (单个核素查询)")
        print("- python nuclide_query.py fe56                (使用元素符号+质量数)")
        print("- python nuclide_query.py 26 30 -m detailed   (详细模式查询)")
        print("- python batch_nuclide_query.py               (批量查询)")
        print("=" * 60)
        
    except Exception as e:
        print(f"运行示例时发生错误: {e}")
        print("请确保:")
        print("1. nndc_nudat_data_export.json 文件存在")
        print("2. 相关模块文件存在 (nuclide_data.py, database_loader.py)")


if __name__ == "__main__":
    main()
