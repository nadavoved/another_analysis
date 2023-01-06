import pandas as pd
from pandas import Int16Dtype, BooleanDtype
from inspect import stack

"""Module to allow only one csv DataFrame to exist at 
once and optimize its memory requirement.
"""

TYPE_MAP = {'Year': Int16Dtype(),
            'Month': Int16Dtype(),
            'DayofMonth': Int16Dtype(),
            'DayOfWeek': Int16Dtype(),
            'Cancelled': BooleanDtype(),
            'Diverted': BooleanDtype(),
            'UniqueCarrier': 'object',
            'Origin': 'object',
            'Dest': 'object',
            'FlightNum': 'string',
            'ActualElapsedTime': Int16Dtype(),
            'AirTime': Int16Dtype(),
            'Distance': Int16Dtype()}

FINAL_TYPES = {item: 'category' for item in ['Year', 'Month', 'DayofMonth',
                                             'DayOfWeek', 'UniqueCarrier', 'Origin', 'Dest']}


def wipe_frames():
    """Delete all DataFrames"""
    g = stack()[2][0].f_globals
    all_variables = [item for item in g]
    for var in all_variables:
        if isinstance(g[var], pd.DataFrame):
            del g[var]


def get_years(*args, first_year: int = None, last_year: int = None, wipe=True) -> pd.DataFrame:
    """Read specific years from the relevant csv's.
    Using only required columns and optimal dtypes.
    Allow a maximum of 5 years.
    #NOTE - even then its execution time is relatively long.
    :param first_year: (int) the first year to load data from.
    :param last_year: (int) the last year to load data from.
    :param wipe: (bool) to wipe previous frames or not.
    """
    if wipe:
        wipe_frames()

    def read_year(yr):
        return pd.read_csv(f'data/{yr}.csv', encoding='cp1252',
                           usecols=TYPE_MAP.keys(), dtype=TYPE_MAP)

    def verify_rng(x: range | tuple):
        if len(list(x)) > 5:
            raise OverflowError('should not include more than 5 years.')
        if any(y not in range(1987, 2009) for y in x):
            raise ValueError('input not in range.')
        return x

    if args:
        rng = verify_rng(args)
    else:
        rng = verify_rng(range(first_year, last_year + 1))
    year_slice = [read_year(yr) for yr in rng]
    frame = pd.concat(objs=year_slice, ignore_index=True)
    return frame.astype(dtype=FINAL_TYPES).rename({'DayofMonth': 'DayOfMonth'})
