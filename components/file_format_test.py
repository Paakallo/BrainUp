
import pandas as pd


def check_columns(import_data:pd.DataFrame):
    df = import_data.select_dtypes(include=['number'])
    columns = list(df.columns)
    channels_info = [] # output

    is_string = False # check if there is a string
    for i,col in enumerate(columns):
        if any(char.isalpha() for char in col): # check if there is a letter
            channels_info.append(col)
            is_string = True
        else:
            channels_info.append(i) # electrode number

    if not is_string: # move numeric columns to a row 
        column_names_row = pd.DataFrame([df.columns.tolist()], columns=df.columns)
        df = pd.concat([column_names_row, df], ignore_index=True)

    df.columns = channels_info
    return df, channels_info


raw_data = pd.read_csv("data/przyklad.csv")

# print(raw_data)
cos, cols = check_columns(raw_data)

print(cos.head())