import datetime
from .log import Logger
import polars as pl
import pandas as pd

factorSuffix = '__factor__'
targetSuffix = '__target__'
benchmarkSuffix = '__benchmark__'
dateSuffix = '__date__'
codeSuffix = '__code__'


def prepare(factors, targets, key_name=['date', 'code']):
    factorName, _ = _check_raw_data(factors, key_name)
    targetName, _ = _check_raw_data(targets, key_name)
    factor_table = factors.pivot(index=key_name, on=factorName)
    target_table = targets.pivot(index=key_name, on=targetName)
    factor_table = factor_table.rename(
        {x: f"{x}{factorSuffix}" for x in factor_table.columns if x not in key_name})
    target_table = target_table.rename(
        {x: f"{x}{targetSuffix}" for x in target_table.columns if x not in key_name})
    full_data = target_table.join(factor_table, on=key_name, how='left')
    dates = full_data[key_name[0]].unique().to_list()
    dates.sort()
    n_days = len(dates)
    n_codes = full_data.shape[0] // n_days
    logger = Logger('Prepare(nx)')
    logger.info(
        f"\n    Nx full data prepared from {dates[0]} to {dates[-1]}.\n    Shape: {full_data.shape}\n    Days: {n_days} \n    Num of avg codes: {n_codes}")
    full_data = full_data.rename(
        {key_name[0]: f"{key_name[0]}{dateSuffix}", key_name[1]: f"{key_name[1]}{codeSuffix}"})
    return full_data


def getReturnTable(full_data, factor_name=None, target_name=None, benchmarks=None, n_groups=10, n_top=[200, 1000]):
    key_names_suf = [x for x in full_data.columns if x.endswith(
        dateSuffix)]+[x for x in full_data.columns if x.endswith(codeSuffix)]
    key_names = [x.replace(dateSuffix, '').replace(
        codeSuffix, '') for x in key_names_suf]
    if benchmarks is not None:
        bmName, _ = _check_raw_data(benchmarks, key_names[:-1])
        bm_table = benchmarks.pivot(index=key_names[:-1], on=bmName)
        bm_table = bm_table.rename(
            {x: f"{x}{benchmarkSuffix}" for x in bm_table.columns if x not in key_names[:-1]}).rename({key_names[0]: f"{key_names[0]}{dateSuffix}"})
    factor_names, target_names = check_full_data(full_data)
    if factor_name is None:
        factor_name = factor_names[0]
    else:
        factor_name += factorSuffix
    if target_name is None:
        target_name = target_names[0]
    else:
        target_name += targetSuffix
    data = full_data.select(key_names_suf + [factor_name, target_name])
    labels = list(map(str, range(1, n_groups+1)))
    labels = [f'G{n_groups}N{str(x).zfill(2)}' for x in labels]
    data = data.with_columns([
        pl.col(factor_name)
        .qcut(n_groups, labels=labels, allow_duplicates=True)
        .over(key_names_suf[0])
        .alias('group'),
        pl.col(factor_name)
        .rank()
        .over(key_names_suf[0])
        .alias('rank')])
    group_data = data.group_by('group', key_names_suf[0]).agg(
        pl.col(target_name).mean().alias('mean_ret'))
    group_data = group_data.pivot(
        on='group', index=key_names_suf[0], maintain_order=True, sort_columns=True)
    ls_data = data.group_by(key_names_suf[0]).agg([
        pl.col(target_name)
        .filter(pl.col('rank') >= pl.col('rank').count() - n_stocks)
        .mean()
        .alias(f'l_{n_stocks}') for n_stocks in n_top]+[
        pl.col(target_name)
        .filter(pl.col('rank') < n_stocks)
        .mean()
        .alias(f's_{n_stocks}') for n_stocks in n_top
    ])
    return_table = ls_data.join(group_data, on=key_names_suf[0]).join(
        bm_table, on=key_names_suf[0], how='left')
    return_table = return_table.to_pandas().set_index(
        key_names_suf[0]).sort_index()
    return_table.loc[getLagDate(return_table.index[0], 1)] = 0
    return_table.index = pd.to_datetime(
        return_table.index, format='%Y%m%d')
    return_table.sort_index(inplace=True)
    return return_table


def _check_raw_data(df: pl.DataFrame, key_name: list) -> tuple:
    col_names = df.columns
    schema = df.collect_schema()
    assert len(col_names) - \
        len(
            key_name) == 2, f"Expected less than 4 columns, got {len(col_names)}."
    for name in col_names:
        if name not in key_name:
            if schema[name] == pl.String:
                colName = name
            elif schema[name] in [pl.Float64, pl.Float32]:
                colValue = name
            else:
                raise ValueError(
                    f"Column {name} has unexpected type {schema[name]}.")
    return colName, colValue


def check_full_data(full_data: pl.DataFrame) -> tuple:
    factor_names = [x for x in full_data.columns if factorSuffix in x]
    target_names = [x for x in full_data.columns if targetSuffix in x]
    return factor_names, target_names


def getLagDate(date, left_lag=1):
    date = int(str(date).replace("-", ""))
    fullTradeDates = getDates()
    idx = fullTradeDates.index(date)
    return fullTradeDates[idx-left_lag]


def getDates(start_date=19990909, end_date=None):
    start_date = datetime.datetime.strptime(str(start_date), "%Y%m%d")

    if end_date:
        end_date = datetime.datetime.strptime(str(end_date), "%Y%m%d")
    else:
        end_date = datetime.datetime.now()

    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(int(current_date.strftime("%Y%m%d")))
        current_date += datetime.timedelta(days=1)
    return date_list


