#!/usr/bin/env python3
"""
NuclideQuery 库使用示例
=======================

本文件演示了 NuclideQuery 库的核心功能，包括：
1. 基础查询：使用 Nuclide 类获取核素数据
2. 理论数据：查询不同 DFT 泛函的计算结果
3. 数据比较：对比实验值与理论值
4. 数据可视化：绘制结合能曲线

运行方式：
    python examples.py
"""

import sys
import matplotlib.pyplot as plt

# 尝试导入 rich 库以获得更好的终端输出体验
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    print("提示: 安装 'rich' 库可获得更美观的输出 (pip install rich)")

# 导入核心库
try:
    from nucquery import Nuclide, NuclideQuery
except ImportError:
    print("错误: 无法导入 nucquery。请确保已安装该包 (pip install .)")
    sys.exit(1)


def print_header(title):
    """打印带格式的标题"""
    if HAS_RICH:
        console.print(Panel(f"[bold cyan]{title}[/bold cyan]", expand=False))
    else:
        print(f"\n=== {title} ===")


def demo_basic_usage():
    """演示基本查询功能"""
    print_header("1. 基础查询示例")

    # 1. 通过质子数(Z)和中子数(N)创建
    fe56 = Nuclide(26, 30)
    
    if HAS_RICH:
        table = Table(title=f"核素信息: {fe56.name}")
        table.add_column("属性", style="cyan")
        table.add_column("值", style="green")
        table.add_column("单位/说明")
        
        table.add_row("质子数 (Z)", str(fe56.Z), "")
        table.add_row("中子数 (N)", str(fe56.N), "")
        table.add_row("结合能 (BE)", f"{fe56.BE:.3f}", "MeV")
        table.add_row("比结合能 (BE/A)", f"{fe56.BE_A:.3f}", "MeV")
        table.add_row("中子分离能 (Sn)", f"{fe56.Sn:.3f}", "MeV")
        table.add_row("半衰期", str(fe56.halflife), "")
        console.print(table)
    else:
        print(f"核素: {fe56.name}")
        print(f"  Z={fe56.Z}, N={fe56.N}")
        print(f"  结合能: {fe56.BE:.3f} MeV")
        print(f"  比结合能: {fe56.BE_A:.3f} MeV")
        print(f"  中子分离能: {fe56.Sn:.3f} MeV")

    # 2. 通过元素符号创建
    pb208 = Nuclide.from_symbol("Pb208")
    print(f"\n通过符号创建: {pb208.name}")
    print(f"  双中子分离能 (S2n): {pb208.S2n:.3f} MeV")


def demo_theoretical_data():
    """演示理论数据查询"""
    print_header("2. 理论数据查询")

    # 指定数据源为 SKMS
    nuc_skms = Nuclide(26, 30, source='SKMS')
    
    print(f"核素: {nuc_skms.name}")
    print(f"数据源: {nuc_skms.source}")
    print(f"  SKMS 结合能: {nuc_skms.BE:.3f} MeV")
    
    # 比较不同理论模型
    print("\n不同模型的 Pb-208 结合能:")
    models = ['experiment', 'SKMS', 'UNEDF1', 'SLY4']
    
    if HAS_RICH:
        table = Table(show_header=True)
        table.add_column("模型")
        table.add_column("结合能 (MeV)")
        table.add_column("与实验差值 (MeV)")
        
        exp_val = Nuclide.from_symbol("Pb208", source='experiment').BE
        
        for model in models:
            n = Nuclide.from_symbol("Pb208", source=model)
            diff = n.BE - exp_val if n.BE and exp_val else 0
            diff_str = f"{diff:+.3f}" if model != 'experiment' else "-"
            table.add_row(model, f"{n.BE:.3f}", diff_str)
        console.print(table)
    else:
        for model in models:
            n = Nuclide.from_symbol("Pb208", source=model)
            print(f"  {model:12s}: {n.BE:.3f} MeV")


def demo_plotting():
    """演示绘图功能"""
    print_header("3. 数据可视化示例")
    print("正在绘制锡(Sn, Z=50)同位素链的比结合能曲线...")

    try:
        # 获取锡的所有同位素 (Z=50)
        # 实验数据
        query_exp = NuclideQuery(source='experiment')
        sn_exp = query_exp.query_isotopes(50)
        # 理论数据 (UNEDF1)
        query_theory = NuclideQuery(source='UNEDF1')
        sn_theory = query_theory.query_isotopes(50)

        plt.figure(figsize=(10, 6))

        # 提取并绘制实验数据
        x_exp = [n.A for n in sn_exp if n.BE_A is not None]
        y_exp = [n.BE_A for n in sn_exp if n.BE_A is not None]
        plt.plot(x_exp, y_exp, 'o-', label='Experiment (NNDC)', markersize=4, color='black')

        # 提取并绘制理论数据
        x_theo = [n.A for n in sn_theory if n.BE_A is not None]
        y_theo = [n.BE_A for n in sn_theory if n.BE_A is not None]
        plt.plot(x_theo, y_theo, '--', label='Theory (UNEDF1)', linewidth=2, color='red')

        plt.title('Binding Energy per Nucleon: Tin Isotopes (Z=50)')
        plt.xlabel('Mass Number A')
        plt.ylabel('BE/A (MeV)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        print("绘图完成，请查看弹出的窗口。")
        plt.show()
        
    except Exception as e:
        print(f"绘图失败: {e}")


def main():
    if HAS_RICH:
        rprint("[bold green]NuclideQuery 示例程序启动[/bold green]")
    
    demo_basic_usage()
    print()
    demo_theoretical_data()
    print()
    demo_plotting()

if __name__ == "__main__":
    main()
