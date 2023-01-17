import os
from inspect import stack

import pandas as pd

"""Module to load csv's to feather files, 
then read feathers as required.
"""

TYPE_MAP = {'Year': 'int16',
            'Month': 'int8',
            'DayofMonth': 'int8',
            'DayOfWeek': 'int8',
            'Cancelled': pd.BooleanDtype(),
            'ArrDelay': 'float32',
            'DepDelay': 'float32',
            'Diverted': pd.BooleanDtype(),
            'Origin': 'category',
            'Dest': 'category',
            'UniqueCarrier': 'category',
            'ActualElapsedTime': 'float32',
            'AirTime': 'float32',
            'Distance': 'float32'}

TO_CAT = {item: 'category' for item in
          ['DayOfWeek', 'UniqueCarrier', 'DayOfMonth',
          'Year','Month', 'Dest', 'Origin']}


def data_to_feather():
    def csv_to_feather(fp):
        temp = pd.read_csv(fp, encoding='cp1252', dtype=TYPE_MAP, usecols=TYPE_MAP.keys())
        new_path = f"{fp.rstrip('csv')}feather"
        temp.rename(columns={'DayofMonth': 'DayOfMonth'}). \
            to_feather(path=new_path)
        print(f'converted {fp} to {new_path}.')

    for i in range(1987, 2009):
        csv_to_feather(f'data/{i}.csv')


def wipe_frames():
    """Delete all DataFrames from memory."""
    g = stack()[1][0].f_globals
    all_variables = [item for item in g]
    for var in all_variables:
        if isinstance(g[var], pd.DataFrame):
            del g[var]


def get_years(*args: int, year_range: tuple[int, int] = None, sample_size=1000) -> pd.DataFrame:
    """Sample specific years from the relevant csv's.
    Use only required columns and optimal dtypes.
    Allow a maximum of 10 years.
    #NOTE - even then its execution time is relatively long.
    :param args: (int) individual years to load data from.
    :param year_range: tuple[int, int] the first and last years to load data from.
    :param sample_size: (int) sample size to draw from each year,
    then from all years combined.
    """

    def read_year(yr):
        return pd.read_feather(f'data/{yr}.feather').sample(sample_size)

    def verify_rng(x: range | tuple):
        if len(list(x)) > 10:
            raise OverflowError('should not include more than 10 years.')
        if any(y not in range(1987, 2009) for y in x):
            raise ValueError('input not in range.')
        return x

    match (bool(args), bool(year_range)):
        case (True, False):
            rng = verify_rng(args)
        case (False, True):
            if len(year_range) != 2:
                raise ValueError('year_range should include start and end years.')
            rng = verify_rng(range(year_range[0], year_range[1] + 1))
        case (False, False):
            raise ValueError('No years are given.')
        case _:
            raise ValueError('Can\'t accept both individual years and range')
    year_slice = [read_year(yr) for yr in rng]
    frame = pd.concat(objs=year_slice, ignore_index=True)
    ordered_frame = frame.astype(TO_CAT)
    ordered_frame['route'] = (ordered_frame['Origin'].astype('str') + '->' +
                              ordered_frame['Dest'].astype('str')).astype('category')
    return ordered_frame


if __name__ == '__main__':
    data_to_feather()
