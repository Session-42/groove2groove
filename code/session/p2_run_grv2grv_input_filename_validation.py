"""
Python Script for running over Session HitCraft - All Files Bank, together with a progress excel (Tamir's).
Finding mismatches in file names / folders, missing files and wrong Excel Structure Values.
Output is CSV/Excel with the relevant attributes, which is used later on in the pre_provessing_on_all_files
"""

from pathlib import Path
import pandas as pd
from session_grv2grv_pipeline_utils import find_structure_invalid_names_in_xls
import numpy as np
import difflib
midi_name_valid_pattern = r'[\w\s&-]+\w #\d+ in [A-G][b#]?m?'

id_col_name = 'ID'
midi_col_name = 'Midi Tracks Titles'
valid_green_col_name = 'Status'
valid_green_col_values = ['Approved'] #  + ['In Proses']

# input/output files and forders
hit_craft_root_folder = 'phase2\HitCraft - All Files Bank'
full_data_excel_csv_path = r'phase2\Hitcraft Catalog Upload  - Hitcraft Catalog Upload .csv'
out_csv_path = r'phase2\valid_phase2_files_all.csv'


# function to calculate for a given folder path
folder_field_func_dict = {'folder_name': lambda folder: folder.name,
                          'correct_st_name': lambda folder: (folder/'Exports'/f'{folder.stem} St.xlsx').exists(),
                          'correct_cp_name': lambda folder: (folder/'Exports'/f'{folder.stem} CP.xlsx').exists(),
                          'correct_midi_name': lambda folder: (folder/'Exports'/f'{folder.stem}.midi').exists(),
                          'has_export_sub_folder': lambda folder: (folder/'Exports').exists(),
                          'sub_genre_folder': lambda folder: folder.parent.name,
                          'genre_folder': lambda folder: folder.parent.parent.name,
                          'structure_invalid_values': lambda folder: ', '.join(find_structure_invalid_names_in_xls(folder/'Exports'/f'{folder.stem} St.xlsx', strip_part_names=True, verbose=False)),
                          'relative_path_folder': lambda folder: str(folder.relative_to(hit_craft_root_folder)),
                          'relative_path_midi': lambda folder: str((folder/'Exports'/f'{folder.stem}.midi').relative_to(hit_craft_root_folder)),
                          'relative_path_st': lambda folder: str((folder/'Exports'/f'{folder.stem} St.xlsx').relative_to(hit_craft_root_folder))
                         }

# fields to include in CSV output
cols_for_output = [id_col_name, midi_col_name, valid_green_col_name, 'has_exact_matching_folder_name', 'correct_st_name', 
                   'correct_cp_name', 'correct_midi_name', 'has_export_sub_folder', 'best_matching_name', 'genre_folder', 
                   'sub_genre_folder','structure_invalid_values','relative_path_midi', 'relative_path_st']
 
def map_hitcraft_files(root_path, sub_folder_glob_pattern = '*/*/*/', folder_field_func_dict=folder_field_func_dict):
    # use the folder name and the folder_field_func_dict to fill all the relevant fields, and return a dataframe
    all_fields_dicts = []
    for folder in Path(root_path).glob(sub_folder_glob_pattern):
        all_fields_dicts.append({key:func(folder) for key,func in folder_field_func_dict.items()})
    return pd.DataFrame(all_fields_dicts)


if __name__ == '__main__': 
    df_xls = pd.read_csv(full_data_excel_csv_path)
    df_files = map_hitcraft_files(root_path=hit_craft_root_folder)

    # get rid of the parent folders for which the genre_folder is '__MACOSX'
    df_files = df_files[df_files['genre_folder'] != '__MACOSX']

    # construct expected folder name from ID + project name. check if the folder name exists.
    df_xls['folder_name'] = df_xls[id_col_name].astype(str) + ' ' + df_xls[midi_col_name]
    df_xls['has_exact_matching_folder_name'] = df_xls['folder_name'].isin(df_files['folder_name'].values)
 
    # if the folder with the expected name does not exist suggest a good option:
    if 'best_matching_name' in cols_for_output:
        file_names_only_alpha_numeric = df_files['folder_name'].str.replace(r'[^a-zA-Z0-9]', '', regex=True).values

        # define a function for finding the best match  
        def find_best_match_non_alphanumeric(name_alpha_numeric, file_names=df_files['folder_name'].values, file_names_only_alpha_numeric=file_names_only_alpha_numeric, max_num_err=1):
            if len(name_alpha_numeric):
                best_match = difflib.get_close_matches(name_alpha_numeric, file_names_only_alpha_numeric, n=1, cutoff=1-max_num_err/len(name_alpha_numeric))
            else: 
                best_match = None
            return "'" + file_names[np.where(file_names_only_alpha_numeric==best_match[0])][0] + "'" if best_match else ''

        df_xls['best_matching_name'] = df_xls['folder_name'].str.replace(r'[^a-zA-Z0-9]', '', regex=True).apply(find_best_match_non_alphanumeric)
        # do not list the best matching name if it is exact:
        df_xls.loc[df_xls['best_matching_name'].str.strip("'") == df_xls['folder_name'], 'best_matching_name'] = 'Exact match'
    
    # merge
    df_xls_with_files_data = pd.merge(df_xls, df_files, on='folder_name', how='left')

    # filter only valid relevant rows:
    df_xls_with_files_data_valid_rows = df_xls_with_files_data[df_xls_with_files_data[valid_green_col_name].isin(valid_green_col_values)]

    # save full_data_excel_csv_path lines matches to csv
    df_for_saving = df_xls_with_files_data_valid_rows[cols_for_output].replace({True: 'V',False: 'x', float('nan'):'-'})
    df_for_saving.to_csv(out_csv_path, index=False)
    df_for_saving.to_excel(out_csv_path[:-3]+'xlsx', index=False)

    print(f"output csv saved to: {out_csv_path}, {out_csv_path[:-3]+'xlsx'}")
