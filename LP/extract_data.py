import pulp
import pandas as pd


def create_constraints():
    path = "./test.xlsx"
    df = pd.read_excel(path)
    print(df.head)
