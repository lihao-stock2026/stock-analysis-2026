"""
项目名称：股票均线策略回测
标的：贵州茅台 600519.SH
时间区间：2023-01-01 ~ 2024-12-31
策略规则：5/20日均线金叉买入，死叉卖出
辅助指标：MACD
数据源：Tushare
输出：回测净值、最大回撤、可视化图片 result_plot.png
"""

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 判断本地缓存文件是否存在
if os.path.exists("stock_data.csv"):
    print("读取本地缓存数据，不调用Tushare")
    df = pd.read_csv("stock_data.csv", encoding="utf-8-sig").reset_index(drop=True)
else:
    print("本地无缓存，从Tushare拉取数据")
    token = os.getenv("TUSHARE_TOKEN")
    # 如果环境变量里面没有存token（返回None）
    if not token:
        # 就弹出输入框，让你手动粘贴token
        token = input('在这里粘贴你的tushare token：')
    ts.set_token(token)
    pro = ts.pro_api()
    df = pro.daily(ts_code="600519.SH", start_date="20230101", end_date="20241231")
    df.to_csv("stock_data.csv", index=False, encoding="utf-8-sig")

df["trade_date"] = pd.to_datetime(df["trade_date"])
df = df.sort_values("trade_date").reset_index(drop=True)
# ======================================================

# ========== 下面继续：计算MACD、均线（不变） ==========
def calc_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2
    return dif, dea, macd

df["ma5"] = df["close"].rolling(window=5).mean()
df["ma20"] = df["close"].rolling(window=20).mean()
df["dif"], df["dea"], df["macd"] = calc_macd(df)

# 删掉空值，并且重置索引为0开始连续数字
df = df.dropna(subset=["ma5","ma20","dif","dea"]).reset_index(drop=True)

# ========== 均线策略：5日均线上穿20日均线买入，下穿卖出 ==========
# 计算金叉、死叉
df["gold_cross"] = (df["ma5"] > df["ma20"]) & (df["ma5"].shift(1) <= df["ma20"].shift(1))
df["dead_cross"] = (df["ma5"] < df["ma20"]) & (df["ma5"].shift(1) >= df["ma20"].shift(1))

df["signal"] = 0
position = 0
for i in range(len(df)):
    if df.loc[i, "gold_cross"]:
        position = 1
    if df.loc[i, "dead_cross"]:
        position = 0
    df.loc[i, "signal"] = position

# 计算每日收益率
df["return"] = df["close"].pct_change()
df = df.dropna(subset=["return"])
# 策略收益率：持仓时才有收益
df["strategy_return"] = df["return"] * df["signal"].shift(1)

# 累积收益
df["benchmark_cum"] = (1 + df["return"]).cumprod()        # 买入持有
df["strategy_cum"] = (1 + df["strategy_return"]).cumprod()# 均线策略

# 最大回撤计算函数
def max_drawdown(series):
    roll_max = series.cummax()
    drawdown = series / roll_max - 1
    return drawdown.min()

benchmark_dd = max_drawdown(df["benchmark_cum"])
strategy_dd = max_drawdown(df["strategy_cum"])

print("\n====回测结果====")
print(f"买入持有最终净值：{df['benchmark_cum'].iloc[-1]:.2f}")
print(f"均线策略最终净值：{df['strategy_cum'].iloc[-1]:.2f}")
print(f"买入持有最大回撤：{benchmark_dd:.2%}")
print(f"均线策略最大回撤：{strategy_dd:.2%}")

# ========== 绘图 ==========
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

fig, (ax1, ax2) = plt.subplots(2,1,figsize=(14,9),sharex=True)

# 上图：股价+均线
ax1.plot(df["trade_date"], df["close"], label="收盘价")
ax1.plot(df["trade_date"], df["ma5"], label="MA5")
ax1.plot(df["trade_date"], df["ma20"], label="MA20")
ax1.set_title("贵州茅台 均线策略回测")
ax1.legend()
ax1.grid(alpha=0.3)

# 下图MACD：dif、dea曲线 + macd柱状
ax2.plot(df["trade_date"], df["dif"], label="DIF")
ax2.plot(df["trade_date"], df["dea"], label="DEA")
# width=1 控制柱子宽度，避免连成大片色块
ax2.bar(df["trade_date"], df["macd"], width=1, color=np.where(df["macd"]>0,"r","g"))
ax2.legend()
ax2.grid(alpha=0.3)
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("result_plot.png", dpi=300, bbox_inches="tight")
plt.show()