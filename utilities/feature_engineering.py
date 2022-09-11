from datetime import date
import datetime
import pandas as pd


def feature_engineering(df, verbose=True):
    def bike_age(circulation_year: int, annonce_date, scraped_date):
        if circulation_year is None:
            return None
        elif (type(annonce_date) is datetime.datetime) or (type(annonce_date) is pd.Timestamp):
            return annonce_date.year - circulation_year
        elif (type(scraped_date) is datetime.datetime) or (type(scraped_date) is pd.Timestamp):
            return scraped_date.year - circulation_year
        else:
            date.today().year - circulation_year

    if verbose:
        print('Start of feature engineering')
    df['bike_age'] = df.apply(lambda x: bike_age(x.circulation_year, x.annonce_date, x.scraped_date), axis=1)
    if verbose:
        print('Feature engineering done')

    return df


if __name__ == "__main__":
    pass
