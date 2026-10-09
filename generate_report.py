"""
考题一：Excel 报表生成脚本
读取 sales_raw.xlsx，完成数据清洗与统计，输出 report.xlsx
"""

import os
import sys

import pandas as pd
from openpyxl import Workbook


REQUIRED_COLUMNS = ['日期', '销售员', '产品', '数量', '单价', '地区']


def load_data(file_path):
    """读取原始 Excel 文件并校验字段。"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到文件: {file_path}")

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except Exception as e:
        raise ValueError(f"读取 Excel 失败: {e}")

    if df.empty:
        raise ValueError("Excel 文件为空，没有数据。")

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必要字段: {', '.join(missing_cols)}")

    return df


def clean_data(df):
    """
    数据清洗：
    1. 删除关键字段缺失的行
    2. 剔除数量 <= 0 的异常行
    3. 按全字段去重
    """
    df = df[REQUIRED_COLUMNS].copy()

    # 关键字段缺失则删除
    df_clean = df.dropna(subset=REQUIRED_COLUMNS).copy()

    # 数值型字段转换
    df_clean['数量'] = pd.to_numeric(df_clean['数量'], errors='coerce')
    df_clean['单价'] = pd.to_numeric(df_clean['单价'], errors='coerce')

    # 数量、单价无法转为有效数字的行删除
    df_clean = df_clean.dropna(subset=['数量', '单价'])

    # 数量 <= 0 视为异常数据，删除
    df_clean = df_clean[df_clean['数量'] > 0]

    # 按全字段去重
    df_clean = df_clean.drop_duplicates()

    if df_clean.empty:
        raise ValueError("清洗后没有有效数据，请检查原始文件。")

    # 计算销售额
    df_clean['销售额'] = df_clean['数量'] * df_clean['单价']

    return df_clean


def generate_statistics(df):
    """
    统计维度：
    1. 按销售员汇总销售额
    2. 按地区汇总销售额
    3. 月度销售额
    4. 总览指标
    """
    # 按销售员
    by_salesperson = (
        df.groupby('销售员', as_index=False)['销售额']
        .sum()
        .sort_values('销售额', ascending=False)
        .reset_index(drop=True)
    )

    # 按地区
    by_region = (
        df.groupby('地区', as_index=False)['销售额']
        .sum()
        .sort_values('销售额', ascending=False)
        .reset_index(drop=True)
    )

    # 月度销售额
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    invalid_dates = df['日期'].isna().sum()
    if invalid_dates > 0:
        print(f"提示: 有 {invalid_dates} 行日期格式无效，月度统计将忽略这些行。")

    df['月份'] = df['日期'].dt.to_period('M').astype(str)
    monthly = (
        df.dropna(subset=['日期'])
        .groupby('月份', as_index=False)['销售额']
        .sum()
        .sort_values('月份')
        .reset_index(drop=True)
    )

    # 总览指标
    total_sales = df['销售额'].sum()
    total_records = len(df)
    salesperson_count = df['销售员'].nunique()
    region_count = df['地区'].nunique()

    overview = pd.DataFrame({
        '指标': ['总销售额', '有效记录数', '销售员数量', '地区数量'],
        '数值': [total_sales, total_records, salesperson_count, region_count]
    })

    return by_salesperson, by_region, monthly, overview


def save_report(df_clean, by_salesperson, by_region, monthly, overview, output_path):
    """将清洗后的明细与统计结果写入 report.xlsx。"""
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # 1. 明细清洗后
        df_clean.to_excel(writer, sheet_name='明细清洗后', index=False)

        # 2. 按销售员
        by_salesperson.to_excel(writer, sheet_name='按销售员', index=False)

        # 3. 按地区
        by_region.to_excel(writer, sheet_name='按地区', index=False)

        # 4. 总览：先写入汇总指标，再追加月度销售额
        overview.to_excel(writer, sheet_name='总览', index=False)
        ws = writer.sheets['总览']

        # 空两行后追加月度数据
        start_row = len(overview) + 3
        ws.cell(row=start_row, column=1, value='月度销售额')
        ws.cell(row=start_row + 1, column=1, value='月份')
        ws.cell(row=start_row + 1, column=2, value='销售额')

        for i, row in monthly.iterrows():
            ws.cell(row=start_row + 2 + i, column=1, value=row['月份'])
            ws.cell(row=start_row + 2 + i, column=2, value=row['销售额'])


def main():
    input_file = 'sales_raw.xlsx'
    output_file = 'report.xlsx'

    try:
        print(f"正在读取 {input_file} ...")
        df = load_data(input_file)

        print("正在清洗数据 ...")
        df_clean = clean_data(df)

        print("正在生成统计报表 ...")
        by_salesperson, by_region, monthly, overview = generate_statistics(df_clean)

        print(f"正在输出 {output_file} ...")
        save_report(df_clean, by_salesperson, by_region, monthly, overview, output_file)

        print("报表生成成功！")
        print(f"  - 有效记录数: {len(df_clean)}")
        print(f"  - 总销售额: {overview.loc[0, '数值']:.2f}")

    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
