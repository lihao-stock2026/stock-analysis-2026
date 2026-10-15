# 股票数据分析与均线策略回测项目
本项目基于Python、Tushare、Pandas、NumPy、Matplotlib，获取贵州茅台股票历史行情，计算MA5/MA20均线、MACD指标，实现金叉/死叉均线策略回测，对比**买入持有策略**与**均线交易策略**的净值与最大回撤，输出可视化图表。

## 项目技术栈
- pandas：数据清洗、指标计算
- numpy：数值运算
- tushare：股票行情API
- matplotlib：绘图可视化

## 项目文件说明
- stock_analysis.py：主程序代码
- stock_data.csv：本地缓存股票日线行情数据
- result_plot.png：回测净值曲线 + MACD指标可视化图
- .gitignore：Git忽略配置文件

## 环境安装
```bash
pip install tushare pandas numpy matplotlib