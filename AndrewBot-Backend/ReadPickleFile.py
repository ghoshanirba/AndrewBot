import pickle
import pandas as pd

data = []

with open("product_name_embeddings.pkl", 'rb') as f1:
    try:
        while True:
            data.append(pickle.load(f1))
    except EOFError:
        pass

df = pd.concat(data, ignore_index=True)

# data = pd.read_pickle("product_description_embeddings.pkl")
print("data1:", len(df))
print("columns:", df.columns)
print("data2:", df)