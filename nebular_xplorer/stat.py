import polars as pl
from .utils import check_full_data, targetSuffix, benchmarkSuffix, dateSuffix, codeSuffix
import pandas as pd
import numpy as np

def metrics(full_data, factor_name=None):
    factor_names, target_names = check_full_data(full_data)
    dateName = [x for x in full_data.columns if x.endswith(dateSuffix)][0]
    if factor_name is None:
        factor_name = factor_names[0]
    ic_data = full_data.group_by(dateName).agg([
        pl.corr(factor_name, target_name).alias(f"IC_{target_name.replace(targetSuffix, '')}") for target_name in target_names]+[
        pl.corr(factor_name, target_name, method="spearman").alias(f"rankIC_{target_name.replace(targetSuffix, '')}") for target_name in target_names])
    ic_data = ic_data.to_pandas().set_index(dateName)
    ic_data.index = pd.to_datetime(ic_data.index, format='%Y%m%d')
    ic_data = ic_data.sort_index()
    return ic_data

def summaryMetrics(factor_metrics):
    ic_table = {}
    for target_name in factor_metrics.columns:
        target_name = '_'.join(target_name.split('_')[1:])
        _data = {}
        _data['IC'] = factor_metrics[f'IC_{target_name}'].mean()
        _data['rankIC'] = factor_metrics[f'rankIC_{target_name}'].mean()
        _data['IR'] = factor_metrics[f'IC_{target_name}'].mean(
        ) / factor_metrics[f'IC_{target_name}'].std()
        _data['rankIR'] = factor_metrics[f'rankIC_{target_name}'].mean(
        ) / factor_metrics[f'rankIC_{target_name}'].std()
        _data['begin_date'] = factor_metrics.index.min().strftime('%Y-%m-%d')
        _data['end_date'] = factor_metrics.index.max().strftime('%Y-%m-%d')
        ic_table[target_name] = _data
    ic_table = pd.DataFrame.from_dict(ic_table, orient='index').round(4)
    return ic_table.sort_index()

def cal_nav(rtn_table):
    return (1 + rtn_table).cumprod()

def calculate_maxdd(nav_table):
    max_values = np.maximum.accumulate(nav_table)
    drawdowns = 1 - nav_table / max_values
    max_dd = drawdowns.max()
    max_dd_end = drawdowns.idxmax()
    max_dd_start = pd.Series(
        np.nan, index=nav_table.columns, dtype='datetime64[ns]')
    for col in nav_table.columns:
        max_dd_start[col] = drawdowns.loc[:max_dd_end[col], col].idxmax()
    drawdowns.columns = [f'{x}_dd' for x in drawdowns.columns]
    return max_dd, max_dd_start.dt.strftime("%Y-%m-%d"), max_dd_end.dt.strftime("%Y-%m-%d"), drawdowns

def ARR_SI(rtn_table, annl_year=252):
    return rtn_table.sum() / rtn_table.shape[0] * annl_year

def ARR_CI(rtn_table, annl_year=252):
    return rtn_table.add(1).prod() ** (annl_year / rtn_table.shape[0]) - 1

def Volatility(rtn_table, annl_year=252):
    return rtn_table.std() * np.sqrt(annl_year)

def Sharpe(rtn_table, annl_year=252):
    return ARR_SI(rtn_table, annl_year) / Volatility(rtn_table, annl_year)

def Calmar(rtn_table, annl_year=252):
    nav_table = cal_nav(rtn_table)
    max_dd, _, _, _ = calculate_maxdd(nav_table)
    return ARR_SI(rtn_table, annl_year) / max_dd

def WinRate(rtn_table):
    return (rtn_table > 0).mean()

def PLRatio(rtn_table):
    return rtn_table[rtn_table > 0].mean() / -rtn_table[rtn_table < 0].mean()

def MaxDD(rtn_table):
    nav_table = cal_nav(rtn_table)
    max_dd, _, _, _ = calculate_maxdd(nav_table)
    return max_dd

def DDS(rtn_table):
    nav_table = cal_nav(rtn_table)
    _, _, _, drawdowns = calculate_maxdd(nav_table)
    return drawdowns

def getPortStat(return_table, annl_year=252):
    nav_table = (return_table + 1).cumprod()
    max_dd, max_dd_start, max_dd_end, _ = calculate_maxdd(
        nav_table)
    stat_return = {}
    stat_return["ARR_SI"] = ARR_SI(return_table, annl_year)
    stat_return["ARR_CI"] = ARR_CI(return_table, annl_year)
    stat_return["Volatility"] = Volatility(return_table, annl_year)
    stat_return["Sharpe"] = Sharpe(return_table, annl_year)
    stat_return["Calmar"] = Calmar(return_table, annl_year)
    stat_return["Win Rate"] = WinRate(return_table)
    stat_return["PL Ratio"] = PLRatio(return_table)
    stat_return['MaxDD'] = max_dd
    stat_return['MaxDDStart'] = max_dd_start
    stat_return['MaxDDEnd'] = max_dd_end
    return pd.DataFrame(stat_return).round(2)

def dd_details(return_table):
    drawdowns = DDS(return_table)
    value_name = return_table.columns[0]+"_dd"
    split_indices = drawdowns.index[drawdowns[value_name] == 0].tolist()
    split_positions = [drawdowns.index.get_loc(idx) for idx in split_indices]
    split_indices = [-1] + split_positions + [len(drawdowns)]
    dfs = [drawdowns.iloc[split_indices[i]:split_indices[i+1]+1] for i in range(len(split_indices)-1)]
    dfs = [x for x in dfs if len(x[x.values!=0]) > 0]
    return sorted(dfs, key=lambda x: x[value_name].max(), reverse=True)

def worstdd(return_table, n=5):
    ddd = dd_details(return_table)[:n]
    started = [x.index[0].strftime('%Y-%m-%d') for x in ddd]
    ended = [x.index[-1].strftime('%Y-%m-%d') for x in ddd]
    dd = [x.max().values[0] for x in ddd]
    periods = [x.shape[0] for x in ddd]
    return pd.DataFrame({
        'Started': started,
        'Ended': ended,
        'DrawDown': dd,
        'Days': periods
    })