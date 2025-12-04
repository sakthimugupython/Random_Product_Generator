import pandas as pd

try:
    products = pd.read_csv("products.csv")
    users = pd.read_csv("users.csv")
    transactions = pd.read_csv("transactions.csv")
    ratings = pd.read_csv("ratings.csv")

    print("\n=== PRODUCTS DATA ===")
    print(products.head())
    print("Total products:", len(products))

    print("\n=== USERS DATA ===")
    print(users.head())
    print("Total users:", len(users))

    print("\n=== TRANSACTIONS DATA ===")
    print(transactions.head())
    print("Total transactions:", len(transactions))

    print("\n=== RATINGS DATA ===")
    print(ratings.head())
    print("Total ratings:", len(ratings))

    print("\n=== NULL VALUES CHECK ===")
    print(products.isnull().sum())
    print(users.isnull().sum())
    print(transactions.isnull().sum())
    print(ratings.isnull().sum())
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
