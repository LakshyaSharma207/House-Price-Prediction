# %%
from google.colab import drive
drive.mount('/content/drive')

# %%
# importing libraries
import numpy as np
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
import ast

# %%
# Loading dataset
df = pd.read_csv("/content/drive/MyDrive/My docs/house_prices.csv").drop_duplicates()

# %%
# reading dataset
df.head()

# %%
df.info()

# %%
print("\nShape: ", df.shape)

# %%
"""
## **Data Cleaning and Preprocessing**
"""

# %%
df.duplicated().sum()

# %%
house_df = df.copy()
house_df.isnull().sum()

# %%
# We are dropping columns with a high number of missing values
house_df.drop(columns=['Society', 'Car Parking', 'Super Area', 'Dimensions', 'Plot Area'], inplace=True)
house_df.isnull().sum()

# %%
house_df.drop(columns=['Index'],inplace=True)

# %%
# 1. Fill null values in texual cols with 'Unknown'
cols_to_fill = ['Description', 'facing', 'overlooking', 'Ownership']
house_df[cols_to_fill] = house_df[cols_to_fill].fillna('Unknown')

# 2. Fill null values in 'Price (in rupees)' with mean value
mean_price = house_df['Price (in rupees)'].mean()
house_df['Price (in rupees)'].fillna(mean_price, inplace=True)

# 3. Replace null values in numeric columns with mode
cols_to_fill_mode = ['Status', 'Transaction', 'Furnishing']
for col in cols_to_fill_mode:
    mode_val = house_df[col].mode().iloc[0]
    house_df[col].fillna(mode_val, inplace=True)

# 4. Convert 'Bathroom' and 'Balcony' columns to numeric form
house_df['Bathroom'] = pd.to_numeric(house_df['Bathroom'], errors='coerce')
house_df['Balcony'] = pd.to_numeric(house_df['Balcony'], errors='coerce')

# Fill NaN values in 'Bathroom' and 'Balcony' with the mean of their respective columns
mean_bathroom = house_df['Bathroom'].mean()
mean_balcony = house_df['Balcony'].mean()
house_df['Bathroom'].fillna(mean_bathroom, inplace=True)
house_df['Balcony'].fillna(mean_balcony, inplace=True)

# Convert >10 values in 'Bathroom' and 'Balcony' to their respective numeric forms
house_df.loc[house_df['Bathroom'] == '>10', 'Bathroom'] = 11
house_df['Bathroom'] = house_df['Bathroom'].astype(int)

house_df.loc[house_df['Balcony'] == '>10', 'Balcony'] = 11
house_df['Balcony'] = house_df['Balcony'].astype(int)

# %%
# 5. Convert Carpet Area to sqft numeric
def convert_to_sqft(area):
    try:
        if pd.notnull(area):
            if 'sqft' in area:
                area = float(area.replace(' sqft', ''))
            else:
                area = float(area.replace(' sqm', '')) * 10.7639  # Convert square meters to square feet
            return area
    except ValueError:
        return np.nan

house_df['Carpet Area'] = house_df['Carpet Area'].apply(convert_to_sqft)

# Impute missing values in 'Carpet Area' with mean
mean_carpet_area = house_df['Carpet Area'].mean()
house_df['Carpet Area'].fillna(mean_carpet_area, inplace=True)

# 6. Impute missing values in 'Floor' with mode
mode_floor = house_df['Floor'].mode().iloc[0]
house_df['Floor'].fillna(mode_floor, inplace=True)

# Checking if null values still exist
print(house_df.isnull().sum())

# %%
house_df.head()

# %%
house_df.duplicated().sum()

# %%
house_df.drop_duplicates(inplace=True)

# %%
house_df.shape

# %%
# Convert 'Amount(in rupees)' to numerical format
def convert_amount(amount):
    try:
        if 'Lac' in amount:
            amount = amount.replace('Lac', '').strip()
            return float(amount) * 100000
        elif 'Cr' in amount:
            amount = amount.replace('Cr', '').strip()
            return float(amount) * 10000000
        else:
            return float(amount)
    except ValueError:
        return None

house_df['Amount(in rupees)'] = house_df['Amount(in rupees)'].apply(convert_amount)

# %%
house_df.info()

# %%
house_df.head()

# %%
"""
## **Handling Outliers**
"""

# %%
out_df = house_df.copy()

# %%
out_df.describe()
#detecting values that are significantly different from the mean and quartiles

# %%
fig, axes = plt.subplots(ncols=5, nrows=1, figsize=(16, 4))
axes = np.ravel(axes)
col_name = ['Amount(in rupees)','Carpet Area','Price (in rupees)','Bathroom','Balcony']
for i, c in zip(range(5), col_name):
    out_df.plot.scatter(ax=axes[i], x=c, y='Amount(in rupees)', sharey=True, colorbar=False, c='r')

# %%
# the function to replace outliers with nan
def replace_outliers_with_nan_iqr(out_df, feature, inplace=False):
    desired_feature = out_df[feature]

    Q1, Q3 = desired_feature.quantile([0.25, 0.75])
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    lower_bound = Q1 - 1.5 * IQR

    indices = (desired_feature[(desired_feature > upper_bound) | (desired_feature < lower_bound)]).index
    if not inplace:
        return desired_feature.replace(desired_feature[indices].values, np.nan)
    return desired_feature.replace(desired_feature[indices].values, np.nan, inplace=True)

# %%
features_with_outlier = ['Amount(in rupees)','Carpet Area','Price (in rupees)','Bathroom','Balcony']
features_means = out_df[features_with_outlier].mean()
# iterate through features with outliers
for i in features_with_outlier:
    replace_outliers_with_nan_iqr(out_df, i, inplace=True)

# replace np.nan by the mean values
out_df.fillna(features_means, inplace=True)
out_df.isnull().sum()

# %%
"""
## **EDA**
"""

# %%
ok_df = out_df.copy()

# %%
# Bivariate analysis for numeric vs. numeric variables
numeric_vs_numeric_columns = ['Amount(in rupees)', 'Price (in rupees)', 'Carpet Area', 'Bathroom', 'Balcony']
for column1 in numeric_vs_numeric_columns:
    for column2 in numeric_vs_numeric_columns:
        if column1 != column2:
            plt.figure(figsize=(8, 6))
            plt.scatter(ok_df[column1], ok_df[column2])
            plt.title(f"{column1} vs. {column2}")
            plt.xlabel(column1)
            plt.ylabel(column2)
            plt.show()

# %%
# correlation Heatmap
import seaborn as sns

plt.figure(figsize=(10, 8))
sns.heatmap(house_df.corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title("Correlation Heatmap")
plt.show()

# %%
"""
## **Feature Engineering**
"""

# %%
ok_df.drop(columns=['Title','Description','Status'],inplace=True)

# %%
ok_df.head()

# %%
ok_df.isnull().sum()

# %%
len(ok_df['location'].unique())

# %%
ok_df['location'] = ok_df['location'].apply(lambda x: x.strip())
location_stats = ok_df['location'].value_counts(ascending=False)
location_stats

# %%
"""
## **Encoding Data**
"""

# %%
from sklearn.preprocessing import LabelEncoder
# Function to perform Label Encoding for multiple columns
def label_encode_multiple(ok_df, columns):
    le = LabelEncoder()
    for column in columns:
        ok_df[column] = le.fit_transform(ok_df[column])
    return ok_df

label_encode_columns = ['location','Transaction','Floor', 'Furnishing', 'facing', 'overlooking', 'Ownership']
ok_df = label_encode_multiple(ok_df, label_encode_columns)

# %%
ok_df.head()

# %%
"""
## **Standard Scaling**
"""

# %%
final_df = ok_df.copy()

# %%
from sklearn.preprocessing import StandardScaler
# Standardization
standard_scaler = StandardScaler()
df_standardized = standard_scaler.fit_transform(final_df)
final_df = pd.DataFrame(df_standardized, columns=final_df.columns)

# %%
X = final_df.drop(columns=['Amount(in rupees)'])
y = final_df['Amount(in rupees)']

# %%
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=4)

# %%
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# %%
models = {
    'Support Vector Machine': SVR(C=10, kernel ='linear'),
    'Random Forest': RandomForestRegressor(random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(random_state=42)
}

for model_name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Evaluate the model
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f'{model_name}:')
    print(f'R-squared: {r2:.2f}')
    print(f'Mean Absolute Error (MAE): {mae:.2f}')
    print(f'Root Mean Squared Error (RMSE): {rmse:.2f}')
    print('----------------------------------------')

# %%
# Random Forest has the highest R-squared value and least errors. Thus random forest is THE model for our dataset.

# %%
final_model = RandomForestRegressor(random_state=42)

def predict_price(price,location,Carpet_Area,Floor,Transaction,Furnishing,facing,overlooking,Bathroom,Balcony,Ownership):

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
    final_model.fit(X_train, y_train)
    estimated_price = final_model.predict(input_data)[0]

    return estimated_price

# %%
# Assuming you have a trained model named 'model'
estimated_price = predict_price(6000,'thane', 1283.153494, '10 out of 11', 'Resale', 'Unfurnished', 'Unknown', 'Unknown', 1.0, 2.0, 'Unknown')
print(f"Estimated Amount: {estimated_price}")

# %%


# %%
"""
## **Exporting Modules**
"""

# %%
import pickle
with open('house_price_model.pickle','wb') as f:
    pickle.dump(final_model,f)

# %%
import json
columns = {
    'data_columns' : [col.lower() for col in X.columns]
}
with open("columns.json","w") as f:
    f.write(json.dumps(columns))

# %%
locations = {
    'locations' : df['location'].unique().tolist()
}
with open("locations.json","w") as f:
  f.write(json.dumps(locations))