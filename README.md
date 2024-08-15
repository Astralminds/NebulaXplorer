# NebulaXplorer: Analyzing and Visualizing Quantitative Factors.
Inspired by [https://github.com/Lumiwealth/quantstats_lumi](https://github.com/Lumiwealth/quantstats_lumi).

## Quick Start
### Input
Supports DataFrames in Polars format; Pandas format will be considered in the future.
- dataframe of factors

| date       | code | factor_value | factor_name |
|------------|------|----------|----------|
| 20240102 | 1 | 0.123    | factor1    |
| 20240102 | 1 | 0.321    | factor2  |
| ... | ... | ...   | ...    |

- dataframe of targets

| date       | code | target_value | target_name |
|------------|------|----------|----------|
| 20240102 | 1 | 0.123    | target1    |
| 20240102 | 2 | 0.321    | target2   |
| ... | ... | ...   | ...    |
- dataframe of benchmarks(same format with return_table)

| date       | name | return_value |
|------------|------|----------|
| 20240102 | benchmark1 | 0.123    | 
| 20240102 | benchmark2 | 0.321    |
| ... | ... | ...   |

#### DataProcess
```python
import nebula_xplorer as nx
full_data = nx.utils.prepare(factor, targets)
return_table = nx.utils.getReturnTable(full_data, benchmarks=None, n_groups=10, n_top=[200, 1000])

```

### Stat
```python
import nebula_xplorer as nx
nx.stats.sharpe(return_table) # return float or polars.Series
```

```python
factor_metrics = nx.stats.metrics(full_data) # IC, rankIC...is there any other daily stats?
nx.stats.summaryMetrics(factor_metrics)
```

### Plot
```python
import nebula_xplorer as nx
nx.plots.snapshot(return_table, title="Portfollio Performance") # pnl and maxdd
nx.plots.metrics(factor_metrics, title="Factor Metrics Performance") # IC performance and ?...
```

### Report
```python
import nebula_xplorer as nx
nx.reports.info(return_table, factor_metrics) # summary tables
nx.reports.html(factors, targets, benchmarks) # pics
```
