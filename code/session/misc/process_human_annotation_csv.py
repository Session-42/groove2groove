"""Script for parsing human annotation of groove2groove outputs (as done by Jonathan @ MyPart in Google-Sheets).
Written by Natan Bibelnik @ MyPart, 2024"""

import pandas as pd
import numpy as np
from pathlib import Path

# download annotation google-sheet as csv, and process them one by one.
annotation_csv_files = Path('./').glob('Human Annotation Groove2Groove Outputs*.csv')
filtered_csv_files = [f for f in annotation_csv_files if not f.name.endswith('_flat.csv')]

for human_annotation_csv in filtered_csv_files:
    try:
        output_csv = human_annotation_csv.stem + '_flat.csv'
        excel_model_dict = {'v01':'None', 'v01_vel':'Velocity', 'v01_drums_vel':'Drums and Velocity', 'v01_drums': 'Drums'}

        # assuming structure where the model name is within () in the first row of the csv, then in the second row - 4 columns belong to each model name
        df = pd.read_csv(human_annotation_csv, header=0) # read csv
        model_name_per_col = df.columns.str.extract(r'\((.*?)\)', expand=False) # find model names within ()

        model_names_ix = np.where(pd.notna(model_name_per_col))[0]
        model_names = model_name_per_col[model_names_ix].tolist()

        # set the second row [0] as index and drop it.
        df.columns = df.iloc[0]
        df = df.drop(0)
        df = df.drop(1)  # row containing temperature
        df = df.reset_index(drop=True)

        num_of_info_cols = 4

        df_info = df.iloc[:,:num_of_info_cols]

        df_all = pd.DataFrame()
        for ix in model_names_ix: 
            df_mini = df.iloc[:,ix:ix+4]
            model_name = excel_model_dict.get(model_name_per_col[ix],model_name_per_col[ix]) # model name (with mapping if is in dict)
            model_name_series = pd.Series([model_name]*len(df_mini))
            df_mini = pd.concat([df_info, model_name_series, df_mini], axis=1, ignore_index=True)
            df_mini = df_mini[pd.notna(df_mini.iloc[:,-4:]).any(axis=1)] #filter empty grades / comments
            df_all = pd.concat([df_all, df_mini], axis=0, ignore_index=True)    

        df_all.columns = df_info.columns.tolist() + ['model_name'] + df.columns[model_names_ix[0]:model_names_ix[0]+4].tolist()
        df_all.to_csv(output_csv, index=False)
        print(f"csv with {len(df_all)} rows saved to '{output_csv}'")

    except Exception as e:
        print(f'Failed to parse {human_annotation_csv}')