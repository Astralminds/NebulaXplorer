from .log import Logger
import polars as pl

factorSuffix = '__factor__'
targetSuffix = '__target__'
benchmarkSuffix = '__benchmark__'
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
    return full_data


def getReturnTable(full_data, factor_name, target_name, benchmarks=None, n_groups=10, n_top=[200, 1000], key_name=['date', 'code']):
    if benchmarks is not None:
        bmName, _ = _check_raw_data(benchmarks, key_name[:-1])
        bm_table = benchmarks.pivot(index=key_name[:-1], on=bmName)
        bm_table = bm_table.rename(
            {x: f"{x}{benchmarkSuffix}" for x in bm_table.columns if x not in key_name[:-1]})
    target_name += targetSuffix
    factor_name += factorSuffix
    data = full_data.select('date', 'code', factor_name, target_name)
    labels = list(map(str, range(1, n_groups+1)))
    labels = [f'G{n_groups}N{str(x).zfill(2)}' for x in labels]
    data = data.with_columns([
        pl.col(factor_name)
        .qcut(n_groups, labels=labels, allow_duplicates=True)
        .over(key_name[0])
        .alias('group'), 
        pl.col(factor_name)
        .rank()
        .over(key_name[0])
        .alias('rank')])
    group_data = data.group_by('group', key_name[0]).agg(
        pl.col(target_name).mean().alias('mean_ret'))
    group_data = group_data.pivot(
        on='group', index=key_name[0], maintain_order=True, sort_columns=True).sort('date')
    ls_data = data.group_by(key_name[0]).agg([
        pl.col(target_name)
        .filter(pl.col('rank') >= pl.col('rank').count() - n_stocks)
        .mean()
        .alias(f'l_{n_stocks}') for n_stocks in n_top]+[
        pl.col(target_name)
        .filter(pl.col('rank') < n_stocks)
        .mean()
        .alias(f's_{n_stocks}') for n_stocks in n_top
    ])
    return_table = ls_data.join(group_data, on=key_name[0]).join(bm_table, on=key_name[0], how='left')
    return return_table.sort('date')


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
    