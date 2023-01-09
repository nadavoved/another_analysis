import os
from inspect import stack

import pandas as pd



"""Module to allow only one csv DataFrame to exist at 
once and optimize its memory requirement.
"""

TYPE_MAP = {'Year': 'category',
            'Month': 'category',
            'DayofMonth': 'category',
            'DayOfWeek': 'category',
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

FINAL_TYPES = {item: 'category' for item in TYPE_MAP
               if TYPE_MAP[item] == 'category'}
COLS = ['UniqueCarrier'] + [label for label in TYPE_MAP.keys()
                            if label != 'UniqueCarrier']


def data_to_feather():
    def csv_to_feather(fp):
        temp = pd.read_csv(fp, encoding='cp1252',
                           usecols=COLS, dtype=TYPE_MAP)
        os.remove(fp)
        new_path = f"{fp.rstrip('csv')}feather"
        temp.to_feather(path=new_path)
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
    :param sample_size: (int) sample size to draw from each year.
    """

    def read_year(yr):
        return pd.read_feather(f'data/{yr}.feather',
                               columns=COLS).sample(sample_size)

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
    frame = pd.concat(objs=year_slice, ignore_index=True).sample(sample_size)
    return frame.astype(dtype=FINAL_TYPES).reindex(columns=COLS).\
        rename(columns={'DayofMonth': 'DayOfMonth'})

if __name__ == '__main__':
    data_to_feather()

