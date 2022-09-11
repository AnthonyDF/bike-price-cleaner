from utilities.data import export_to_table, get_table
from utilities.cleaning import clean_raw_master_data, clean_data_before_ml
from utilities.fuzzy_match import fuzzy_match_brand
from utilities.feature_engineering import feature_engineering


def cleaner(verbose=True):
    # Import raw master data and clean
    df = get_table('master', verbose=verbose)
    df = clean_raw_master_data(df, verbose=verbose)

    # Import bike database from postgrSQL server
    bike_db = get_table('bikez_database', verbose=verbose)

    # Match brand from raw data with bike reference database
    df = fuzzy_match_brand(df, bike_db, verbose=verbose)

    # Add features
    df = feature_engineering(df, verbose=verbose)

    # Post to Postgresql
    export_to_table(df, 'master_clean', verbose=verbose)

    # Prepare data before ML and export to postgres db
    df_ml = clean_data_before_ml(df, verbose=verbose)
    export_to_table(df_ml, 'master_ml', verbose=verbose)


if __name__ == "__main__":
    cleaner()
