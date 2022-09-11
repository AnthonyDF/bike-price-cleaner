from rapidfuzz import process


def fuzzy_match_brand(df, bike_db, verbose=True):
    if verbose:
        print('Fuzzy match in progress, matching brands...')

    # fuzzy match brand
    def match_brand(choices, to_match):
        return process.extractOne(to_match, choices, score_cutoff=80)

    list_of_unmatched_brand = df.brand.unique().tolist()
    list_of_matched_brand = []

    for unmatched_brand in list_of_unmatched_brand:
        try:
            result = match_brand(bike_db.brand.unique().tolist(), unmatched_brand)[0]
            list_of_matched_brand.append(result)
        except:
            list_of_matched_brand.append(None)

    def replace(brand_column, list_of_matched_brand_, list_of_unmatched_brand_):
        position_index = list_of_unmatched_brand_.index(brand_column)
        return list_of_matched_brand_[position_index]

    df.brand = df.brand.apply(lambda x: replace(x, list_of_matched_brand, list_of_unmatched_brand))

    shape_before_drop = df.shape[0]
    df.dropna(subset=['brand'], inplace=True)
    if verbose:
        print('count of unmatched rows for the brand: ', shape_before_drop - df.shape[0])
        print('Fuzzy match finished')

    return df
