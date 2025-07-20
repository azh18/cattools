import pandas as pd
import sys

def main(src_file, target_file, result_file):
    # 读取指定工作表
    df_target = pd.read_excel(target_file, header=0)
    df_src = pd.read_excel(src_file, header=0)

    # 需要对比和补充的字段
    compare_cols = ['决议公告日', '决议类型', '决议内容', '是否通过', '是否通过说明', '赞成份额', '赞成率']

    # 用【代码】和【大会公告日】作为主键合并
    df_merged = pd.merge(
        df_target, df_src, 
        on=['代码', '大会公告日'], 
        how='left', 
        suffixes=('', '_src')
    )

    print("运行中")

    for idx, row in df_merged.iterrows():
        updated = False
        for col in compare_cols:
            val_target = row[col]
            val_src = row.get(col + '_src')
            if pd.isna(val_target) and not pd.isna(val_src):
                df_merged.at[idx, col] = val_src
                print(f'第{idx+1}行已补充')
                updated = True
            elif not pd.isna(val_target) and not pd.isna(val_src) and val_target != val_src:
                print(f'警告：第{idx+1}行【{col}】不一致，target="{val_target}"，src="{val_src}"')
        # 可选：如果你只想打印一次补充信息，可以用 updated 变量

    # 去除带 _src 后缀的辅助列
    df_result = df_merged[df_target.columns]

    # 输出到 result.xlsx
    df_result.to_excel(result_file, index=False)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])