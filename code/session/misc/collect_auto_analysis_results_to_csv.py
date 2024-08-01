"""Script for collecting auto groove2groove analysis.json results into a single csv
Written by Natan Bibelnik @ MyPart, 2024"""

import pandas as pd
from pathlib import Path
import json

if __name__ == '__main__': 
    root_folder = r'phase2\final_self_blend_outputs_w_bpm'
    out_auto_analysis_csv = 'grv2grv_analysis_self_blend.csv'
    data_list = []

    for analysis_json in Path(root_folder).glob('**/*.analysis.json'):

        with open(analysis_json, 'r') as file:
            data = json.load(file)
            data_list.append(data)

    df_auto_analysis = pd.DataFrame(data_list)
    df_auto_analysis.to_csv(out_auto_analysis_csv, index=False)
    print(f"results csv with {len(df_auto_analysis)} rows saved to '{out_auto_analysis_csv}'")