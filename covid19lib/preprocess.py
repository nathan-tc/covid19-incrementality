import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import os

age_intervals = [0, 19, 39, 59, 74, 200]
dtypes = {'annee_comptabilisation': 'int64',
          'sexe': 'int64',
          'age': 'int64', 
          'departement_deces': 'str', 
          'nb_deces': 'int64', 
          'date_deces': 'str'}


def load_preprocess_df(df_filename):
    df = pd.read_csv(df_filename, sep=';', dtype=dtypes)
    df['date_deces'] = pd.to_datetime(df['date_deces'])
    df = df[df['date_deces'] >= '1990-01-01']

    # To take age into account, we will create a new feature `age_bin` based on INSEE standard: (0:19, 20:39, 40:59, 60:74, 75+)
    df['age_bin'] = pd.cut(df['age'], age_intervals, include_lowest=True, labels=np.array(age_intervals[:-1])+1)

    # Aggregate by age_bin rather than age
    df = df.groupby(["date_deces", "age_bin", "sexe", "departement_deces"], as_index=False)["nb_deces"].sum()
    df['nb_deces'] = df['nb_deces'].astype(pd.Int64Dtype())  # pandas int that handle NaN...
    df['departement_deces'] = df['departement_deces'].astype('category')

    return df


# On développe ensuite la variable `date_deces` pour enrichir les données :
def add_features(df):
    df['dayofweek'] = df['date_deces'].dt.dayofweek
    df['day'] = df['date_deces'].dt.day
    df['month'] = df['date_deces'].dt.month
    df['year'] = df['date_deces'].dt.year
    df['weeknumber'] = df['date_deces'].dt.week

    return df


def preprocess_data(filename,
                    inputdir="./data/",
                    outputdir="./preprocessed_data/"):
    """preprocess a file from ./data/ and save it as pickle in  ./preprocessed_data/

    Parameters
    ----------
    filename : str
        name of the .csv file to preprocess without the extension (e.g. "test" for file `test.csv`).
    inputdir : str (default: "./data/")
        folder path containing the file
    outputdir: str (default: "./preprocessed_data/")
`       folder path for the output preprocessed file

    Returns
    -------
    output_filepath: str
        the signal
    """

    Path(outputdir).mkdir(parents=True, exist_ok=True)

    df = load_preprocess_df(os.path.join(inputdir, filename+'.csv'))
    df = add_features(df)
    output_filepath = os.path.join(outputdir, filename+'.pkl')
    df.to_pickle(output_filepath)

    return output_filepath
