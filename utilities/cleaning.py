from datetime import datetime
import string
import re

words_to_clean = ['eligible',
                  ' au ',
                  'financement',
                  'euros',
                  'finition',
                  'revisee',
                  ' et ',
                  'garantie',
                  'garanti',

                  'constructeur',
                  'etat',
                  'neuf',
                  ' mois',
                  'nouveau',
                  'model', 'ans', 'contrat', 'dentretien',
                  'kms', 'pro', 'bm16', 'perigueux', 'motorrad',
                  'occasions', 'occasion', 'mois', 'gps', 'akrapovic', 'bagagerie', 'prepa', 'preparee', 'motos',
                  'option',
                  'unique', ' a ', 'partir', ' de ', ]
models_to_drop = ['z', 'r 1200', 'cb', 'r', '', None, 'g', 'x', 'k', 'f']


def remove_punctuations(text):
    """
    remove punctuation in a string
    """
    if text is None:
        return None
    for punctuation in string.punctuation:
        text = text.replace(punctuation, '')
    return text


def clean_raw_master_data(data, verbose=True, vendor_type='all'):
    """
    Clean the master sql table right after import.
    """

    if verbose:
        print('Raw data cleaning in progress...')
    df = data.copy()
    # drop nan
    if verbose:
        print("Data size before drop nan: " + str(df.shape))
    df.dropna(subset=['brand', 'model', 'circulation_year', 'mileage', 'price'], inplace=True)

    # thresholds
    if verbose:
        print("Data size before thresholds: " + str(df.shape))
    df = df[(df["circulation_year"] >= 1950) & (df["circulation_year"] <= datetime.now().year + 1)]
    df = df[((df["mileage"] >= 100) & (df["mileage"] <= 150000))]
    df = df[(df["price"] >= 100) & (df["price"] < 80000)]
    df = df[((df["engine_size"] <= 2500) | (df["engine_size"].isna()))]
    if vendor_type == 'pro':
        df = df[(df["vendor_type"].isin(['pro', 'professionel', 'professionnel']))]
    df = df[df.source.isin(
        ['lepoledeloccasion', '4en1', 'fulloccaz', 'seb-moto', 'motoservices', 'motovente', 'montoconcess',
         'moto-station', 'autoscoot24', 'leparking'])]

    # # Clean same bike with multiple prices (keep last scrapped price)
    if verbose:
        print("Data size before bike duplicates: " + str(df.shape))
    df.sort_values('price', ascending=False, inplace=True)
    # df.drop_duplicates(subset=['id'], keep='first', inplace=True)

    df.drop_duplicates(subset=['brand', 'model', 'circulation_year', 'mileage', 'price'], inplace=True)

    # remove accents
    df.category = df.category.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df.brand = df.brand.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df.model = df.model.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df.comment = df.comment.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    # lower and strip
    df.category = df.category.str.lower().str.strip()
    df.brand = df.brand.str.lower().str.strip()
    df.model = df.model.str.lower().str.strip()

    # remove punctuacion
    df.brand = df.brand.apply(remove_punctuations)
    df.model = df.model.apply(remove_punctuations)

    # specific cleaning for leparking.fr
    def leparking_return_model(source, brand, model, comment):
        if (source == 'leparking') and (comment is not None):
            comment = comment.lower().strip()
            comment = remove_punctuations(comment)

            text = comment.split(' annee')[0].replace(brand, '')
            text = re.sub(r'(?=.*?(19[56789]|20\d{2}).*)\d{4}', '', text)
            text = re.sub(r'/(\d{4,})/', '', text)

            # Extra words to remove
            for word in words_to_clean:
                text = text.replace(word, '').strip()
            return text.strip()
        else:
            return model

    df['model'] = df.apply(lambda x: leparking_return_model(x['source'], x['brand'], x['model'], x['comment']),
                           axis=1)

    # specific cleaning for moto-station
    def moto_station(brand, model, source):
        if (brand == 'yamaha') and (model == 't') and (source == 'moto-station'):
            return 'tmax'
        if (brand == 'honda') and (model == 'x') and (source == 'moto-station'):
            return 'xadv'
        else:
            return model

    df['model'] = df.apply(lambda x: moto_station(x['brand'], x['model'], x['source']), axis=1)

    # clean categories
    def clean_category(category):
        if (category is None) or (category == 'autres motos') or (category in ['coupa', 'moto 125',
                                                                               'vahicules utilitaires',
                                                                               'vehicules utilitaires',
                                                                               'utilitaire']):
            return 'autres'
        elif category in ['routia re', 'routiare', 'routiere & gt', 'routia re gt', 'routiere  gt', 'routiere']:
            return 'routiere'
        elif category in ['quad utilitaire', 'quad loisirs', 'quad']:
            return 'quad'
        elif category in ['motocross mx', 'cross']:
            return 'cross'
        elif category in ['super motard', 'supermotard']:
            return 'supermotard'
        elif category in ['valomoteur', 'velomoteur']:
            return 'velomoteur'
        elif category == 'roadster':
            return 'roadster'
        elif category == 'scooter':
            return 'scooter'
        elif category == 'maxi scooter':
            return 'maxi scooter'
        elif category == 'trail':
            return 'trail'
        elif category == 'trial':
            return 'trial'
        elif category == 'trail-supermotard':
            return 'trail-supermotard'
        elif category == 'sportive':
            return 'sportive'
        elif category in ['custom', 'chopper']:
            return 'custom'
        elif category in ['retro', 'collection']:
            return 'collection'
        elif category in ['enduro', 'cross &amp; enduro']:
            return 'enduro'
        elif category in ['trike']:
            return 'trike'
        else:
            return 'autres'

    # Extract postal code 5 digits:
    def extract_postal_code(raw_text):
        m = re.search(r"\d{5}", str(raw_text))
        if m is not None:
            text = m.group(0)
            if text[:2] == '97':
                return int(text[:3])
            else:
                return int(text[:2])
        else:
            m = re.search(r"\d{3}", str(raw_text))
            if m is not None:
                text = m.group(0)
                if text[:2] == '97':
                    return int(text[:3])
                else:
                    return int(text[:2])
            else:
                m = re.search(r"\d{2}", str(raw_text))
                if m is not None:
                    text = m.group(0)
                    return int(text)
                else:
                    return None

    df['postal_code'] = df['localisation'].apply(lambda x: extract_postal_code(x))

    if verbose:
        print("Data size before bike cleaning categories: " + str(df.shape))
    df.category = df.category.apply(clean_category)
    df = df[df.category != 'autres']
    if verbose:
        print('Raw data cleaning finished', str(df.shape))

    for model_to_drop in models_to_drop:
        df = df[df.model != model_to_drop]

    return df


def clean_data_before_ml(data, verbose=True):
    """
    return clean dataframe before machine leanring
    """
    df = data.copy()

    # data size before
    if verbose:
        print("Data size before ML cleaning: " + str(df.shape))

    # cleaning
    category_count_threshold = 200
    groupby_category = df.groupby('category').agg(Mean=('price', 'mean'), Std=('price', 'std'),
                                                  Count=('price', 'count'))
    drop_category = groupby_category[groupby_category.Count < category_count_threshold].index.to_list()
    drop_category.append('unspecified category')
    df = df[df.category.isin(drop_category) == False]

    brand_count_threshold = 200
    groupby_brand = df.groupby('brand').agg(Mean=('price', 'mean'), Std=('price', 'std'), Count=('price', 'count'))
    drop_brand = groupby_brand[groupby_brand.Count < brand_count_threshold].index.to_list()
    df = df[df.brand.isin(drop_brand) == False]

    # df = df.drop_duplicates()
    # df = df[(df["bike_year"] >= (-df["bike_year"].std() * 3 + df["bike_year"].mean())) & (df["bike_year"] <= 2022)]
    # df = df[(df["mileage"] >= 1000) & (df["mileage"] <= (df["mileage"].mean() + 3 * df["mileage"].std()))]
    # df = df[(df["price"] >= 1000) & (df["price"] < (df["price"].mean() + 4 * df["price"].std()))]
    # df = df[(df["engine_size"] >= 49) & (df["engine_size"] < (df["engine_size"].mean() + 3 * df["engine_size"].std()))]
    # df = df[~df["category_db"].isnull()]
    # df = df[df["brand_db"].isin(list(pd.DataFrame(df["brand_db"].value_counts())[0:50].index))]

    # remove duplicates
    df.drop_duplicates(subset=['model', 'brand', 'price', 'mileage', 'circulation_year'], inplace=True)

    df = df[['brand', "category", 'engine_size', 'mileage', 'circulation_year', 'bike_age', "price"]]
    df.dropna(inplace=True)

    # data size after
    if verbose:
        print("Data size after ML cleaning: " + str(df.shape))
        print('Data ready for ML')

    return df
