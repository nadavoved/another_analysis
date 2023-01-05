import pandas as pd
from pandas import Int16Dtype
from inspect import stack

"""Module to allow only one csv DataFrame to exist at 
once and optimize its memory requirement.
"""

TYPE_MAP = {'Year': Int16Dtype(),
            'Month': Int16Dtype(),
            'DayofMonth': Int16Dtype(),
            'DayOfWeek': Int16Dtype(),
            'Cancelled': Int16Dtype(),
            'Diverted': Int16Dtype(),
            'UniqueCarrier': 'category',
            'Origin': 'category',
            'Dest': 'category',
            'FlightNum': Int16Dtype(),
            'ActualElapsedTime': Int16Dtype(),
            'AirTime': Int16Dtype(),
            'Distance': Int16Dtype()}


def wipe_frames():
    """Delete all DataFrames"""
    g = stack()[2][0].f_globals
    all_variables = [item for item in g]
    for var in all_variables:
        if isinstance(g[var], pd.DataFrame):
            del g[var]


def get_years(first_year: int, last_year: int = None) -> pd.DataFrame:
    """Read specific years from the relevant csv's.
    Using only required columns and optimal dtypes.
    Allow a maximum of 5 years.
    #NOTE - even then its execution time is relatively long.
    :param first_year: (int) the first year to load data from.
    :param last_year: (int) the last year to load data from.
    """
    wipe_frames()

    def read_year(yr):
        return pd.read_csv(f'data/{yr}.csv', encoding='cp1252',
                           usecols=TYPE_MAP.keys(), dtype=TYPE_MAP)

    def verify_yr(y):
        return y in range(1987, 2009)

    if not verify_yr(first_year):
        raise ValueError('first year not in range.')
    if last_year is None:
        return read_year(first_year)
    else:
        if not verify_yr(last_year):
            raise ValueError('last year not in range.')
        if not 0 < last_year - first_year < 5:
            raise ValueError('Years gap should positive and less than 5.')
        year_slice = [read_year(yr) for yr in
                      range(first_year, last_year + 1)]
        return pd.concat(objs=year_slice, ignore_index=True)



