from datetime import date


def feature_engineering(df, verbose=True):
    def bike_age(circulation_year, scraped_date, annonce_date):
        if (annonce_date is not None) and (circulation_year is not None):
            return int(annonce_date.year - circulation_year)
        elif (scraped_date is not None) and (circulation_year is not None):
            return int(scraped_date.year - circulation_year)
        else:
            return None

    if verbose:
        print('Start of feature engineering')
    df['bike_age'] = df.apply(lambda x: bike_age(x['circulation_year'],
                                                 x['scraped_date'],
                                                 x['annonce_date']
                                                 ), axis=1)
    if verbose:
        print('Feature engineering done')

    return df
