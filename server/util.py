import json
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

__locations = None
__model = None

def get_location_names():
    return __locations

def load_saved_artifacts():
    print("loading saved artifacts....")
    global __locations

    with open("./artifacts/locations.json", "r") as f:
        __locations = json.load(f)['locations']

    global __model
    if __model is None:
        with open('./artifacts/house_price_model.pickle', 'rb') as f:
            __model = pickle.load(f)

    print("loading saved artifacts is done")

def label_encode_multiple(ok_df, columns):
    le = LabelEncoder()
    for column in columns:
        ok_df[column] = le.fit_transform(ok_df[column])
    return ok_df

label_encode_columns = ['location','Transaction','Floor', 'Furnishing', 'facing', 'overlooking', 'Ownership']

def get_estimated_price(price,location,Carpet_Area,Floor,Transaction,Furnishing,facing,overlooking,Bathroom,Balcony,Ownership):
  
    input_data = pd.DataFrame({
        'Price (in rupees)': [price],
        'location': [location],
        'Carpet Area': [Carpet_Area],
        'Floor': [Floor],
        'Transaction': [Transaction],
        'Furnishing': [Furnishing],
        'facing': [facing],
        'overlooking': [overlooking],
        'Bathroom': [Bathroom],
        'Balcony': [Balcony],
        'Ownership': [Ownership]
    })

    # Encode the columns that were label encoded
    le = LabelEncoder()
    for column in label_encode_columns:
        input_data[column] = le.fit_transform(input_data[column])

    # Make the prediction
    estimated_price = __model.predict(input_data)[0]

    return estimated_price

if __name__ == '__main__':
    load_saved_artifacts()
    print(get_location_names())
    print(get_estimated_price(6000,'thane', 1283.153494, '10 out of 11', 'Resale', 'Unfurnished', 'Unknown', 'Unknown', 1.0, 2.0, 'Unknown'))
