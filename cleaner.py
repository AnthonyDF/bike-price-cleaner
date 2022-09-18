from utilities.data import export_to_table, get_table
from utilities.cleaning import clean_raw_master_data, clean_data_before_ml
from utilities.fuzzy_match import fuzzy_match_brand
from utilities.feature_engineering import feature_engineering


def cleaner(verbose=True):
    # Import raw master data and clean
    df = get_table('master', verbose=verbose)
    df = clean_raw_master_data(df, verbose=verbose)
    df_pro = clean_raw_master_data(df, verbose=verbose, vendor_type='pro')

    # Import bike database from postgrSQL server
    df_bikez = get_table('bikez_database', verbose=verbose)

    # Match brand from raw data with bike reference database
    df = fuzzy_match_brand(df.copy(), df_bikez, verbose=verbose)
    df_pro = fuzzy_match_brand(df_pro.copy(), df_bikez, verbose=verbose)

    # Add features
    df = feature_engineering(df, verbose=verbose)
    df_pro = feature_engineering(df_pro, verbose=verbose)

    # Post to Postgresql
    export_to_table(df, 'master_clean', verbose=verbose)
    export_to_table(df_pro, 'master_clean_pro', verbose=verbose)

    # Prepare data before ML and export to postgres db
    df_ml = clean_data_before_ml(df_pro, verbose=verbose)
    export_to_table(df_ml, 'master_ml', verbose=verbose)


if __name__ == "__main__":
    cleaner()
