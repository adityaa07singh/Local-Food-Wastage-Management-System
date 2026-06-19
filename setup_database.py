import pandas as pd
from database import engine

providers = pd.read_csv("datasets/providers_data.csv")
receivers = pd.read_csv("datasets/receivers_data.csv")
food = pd.read_csv("datasets/food_listings_data.csv")
claims = pd.read_csv("datasets/claims_data.csv")

providers.columns = providers.columns.str.lower()
receivers.columns = receivers.columns.str.lower()
food.columns = food.columns.str.lower()
claims.columns = claims.columns.str.lower()

providers.to_sql("providers", engine, if_exists="replace", index=False)
receivers.to_sql("receivers", engine, if_exists="replace", index=False)
food.to_sql("food_listings", engine, if_exists="replace", index=False)
claims.to_sql("claims", engine, if_exists="replace", index=False)

print("SQLite database created successfully!")
