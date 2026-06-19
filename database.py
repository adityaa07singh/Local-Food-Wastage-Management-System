from sqlalchemy import create_engine

engine = create_engine("postgresql://adityasingh@localhost/food_wastage_db")

print("Database Connected Successfully!")
