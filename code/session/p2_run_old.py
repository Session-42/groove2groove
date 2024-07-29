import os
from pathlib import Path
import pandas as pd
from session_grv2grv_processing_utils import get_stucture_dict_from_xls, preprocess_midi_file
import numpy as np
from collections import Counter
import json

id_col_name = 'ID'
midi_col_name = 'Midi Tracks Titles'
midi_file_folder = 'phase2\Midi files exports for Session_s projects'
structure_folder = 'phase2\Structure for Midi Tracks by Session'
chord_folder = 'phase2\Chord Progression Analysis for Midi tracks by Session'
preprocess_out_folder = 'phase2\preprocessed'

full_data_excel_csv_path = r'phase2\Hitcraft Catalog Upload (Temp Copy! Remove once approved by Tamir) - Sheet1.csv'
out_csv_path = r'phase2\valid_phase2_files.csv'

if __name__ == '__main__': 
    df = pd.read_csv(full_data_excel_csv_path)

    df['found-mid'] = df[midi_col_name].apply(lambda x: (Path(midi_file_folder) / (x + '.mid')).exists())
    df['found-structure'] = df[midi_col_name].apply(lambda x: (Path(structure_folder) / (x + '.xlsx')).exists())
    

    df = df[df['found-structure'] &  df['found-mid']]
    
    for stem in df[midi_col_name]:

        midi_path = Path(midi_file_folder) / (stem + '.mid')
        structure_xls_path = Path(structure_folder) / (stem + '.xlsx')

        part_struct_first_and_last_bar_dict = get_stucture_dict_from_xls(structure_xls_path, ['Verse','Chorus','Pre Chorus'], remove_last_char_1_in_part_name=True)
        
        # for struct_part in part_struct_first_and_last_bar_dict:
        #     start_bar, end_bar = part_struct_first_and_last_bar_dict[struct_part]
        stream_dict, program_dict, drum_dict = preprocess_midi_file(midi_path, 
                                                                    part_struct_first_and_last_bar_dict, 
                                                                    auto_map_midi = True, 
                                                                    split_drum = True,)

        for part_name, midi_stream in stream_dict.items():
            output_midi_file = Path(preprocess_out_folder) / f'{stem}.{part_name}.mid'
            midi_stream.write('midi', fp=output_midi_file)
            print(f"Preprocessed {part_name} saved to '{output_midi_file}'")

        if program_dict:
            json_file_path =  Path(preprocess_out_folder) / (stem + '.program_dict.json')
            # Save the dictionary to a JSON file
            with open(json_file_path, 'w') as json_file:
                json.dump(program_dict, json_file, indent=4)
                print(f"Program Dict Dictionary saved to {json_file_path}")
        if drum_dict:
            json_file_path =  Path(preprocess_out_folder) / (stem + '.drum_dict.json')
            # Save the dictionary to a JSON file
            with open(json_file_path, 'w') as json_file:
                json.dump(drum_dict, json_file, indent=4)
                print(f"Drum Dict Dictionary saved to {json_file_path}")

        
                1+1
    # structure_file = 
    # # make sure all midis end with mid or midi have links:
    # for midi_file in Path(midi_file_folder).glob('*.mid*'):
    #     # check if file is in the excel:
    #     if midi_file.stem in df[midi_col_name].values:
            
    #         if structure_file.exists():
    #             print(f'midi_file {midi_file} has xls and in excel')
    #             get_stucture_dict_from_xls(structure_file, ['Verse','Chorus','Pre Chorus'], remove_last_char_1_in_part_name=True)

    #     #     midi_name = df[midi_col_name][ix]
        #     midi_id = df[id_col_name][ix]


     ##################################################

    # Validate structure values