"""
======= OLD SCRIPT =======
===== ASSUMES DIFFERENT FOLDERS FOR STRUCTURE, CHORDS AND MIIDIS ===
This script validates Tamir's excel (containing relevant projects name, etc.),
makes sufe that the relevant Chords, Structure and MIDIs in the folders
"""


from pathlib import Path
import pandas as pd
from session_grv2grv_pipeline_utils import find_structure_invalid_names_in_xls
import numpy as np
from collections import Counter
import difflib
midi_name_valid_pattern = r'[\w\s&-]+\w #\d+ in [A-G][b#]?m?'

id_col_name = 'ID'
midi_col_name = 'Midi Tracks Titles'
midi_file_folder = 'phase2\Midi files exports for Session_s projects'
structure_folder = 'phase2\Structure for Midi Tracks by Session'
chord_folder = 'phase2\Chord Progression Analysis for Midi tracks by Session'

full_data_excel_csv_path = r'phase2\Hitcraft Catalog Upload (Temp Copy! Remove once approved by Tamir) - Sheet1.csv'
out_csv_path = r'phase2\valid_phase2_files.csv'


def validate_all_structue_file_values(fix_part_names=False, strip_part_names=False):
    print('-------------------------')
    print('Structure invalid values:')
    all_values = []
    for structure_file in Path(structure_folder).glob('*.xlsx'):
        all_values += find_structure_invalid_names_in_xls(structure_file, fix_part_names=fix_part_names, strip_part_names=strip_part_names)
    print('--- counter  ----')
    counter = Counter(all_values)
    print(str(counter).replace('Counter({','').replace('})','').replace(', ','\n'))


if __name__ == '__main__': 
    df = pd.read_csv(full_data_excel_csv_path)

    df['is_valid_name'] =  df[midi_col_name].str.fullmatch(midi_name_valid_pattern) & ~df[midi_col_name].str.contains('[ -]{2}') & ~df[midi_col_name].str.contains('[Hh]ip [Hh]op') 
    df['found-mid'] = df[midi_col_name].apply(lambda x: (Path(midi_file_folder) / (x + '.mid')).exists())
    df['found-structure'] = df[midi_col_name].apply(lambda x: (Path(structure_folder) / (x + '.xlsx')).exists())
    df['found-chords'] = df[midi_col_name].apply(lambda x: (Path(chord_folder) / (x + '.xlsx')).exists())

    
    # save full_data_excel_csv_path lines matches to csv
    df[[id_col_name, midi_col_name, *df.columns[df.columns.str.startswith(('is_valid','found'))]]].replace({True: 'V',False: 'x'}).to_csv(out_csv_path, index=False, sep='\t')
    

    # look for additional files not in full_data_excel_csv_path
    additional_midi = [f.name for f in Path(midi_file_folder).glob('*.mid*') if f.stem not in df[midi_col_name].values]
    additional_structure = [f.name for f in Path(structure_folder).glob('*.xlsx') if f.stem not in df[midi_col_name].values]
    additional_chord = [f.name for f in Path(chord_folder).glob('*.xlsx') if f.stem not in df[midi_col_name].values]


    def find_best_match(file_name, list_of_file_names=df[midi_col_name].values):
        # find mismatches up to 3 character:
        best_match = difflib.get_close_matches(file_name, list_of_file_names, n=1, cutoff=1-2/len(file_name))
        return f"(in excel exists: '{best_match[0]}')" if best_match else ""

    additional_midi_with_suggestion = [f"{n} {find_best_match(n.rsplit('.',1)[0])}" for n in additional_midi]
    additional_structure_with_suggestion = [f"{n} {find_best_match(n.rsplit('.',1)[0])}" for n in additional_structure]
    additional_chord_with_suggestion = [f"{n} {find_best_match(n.rsplit('.',1)[0])}" for n in additional_chord]

    txt_lines = ['additional midi files (not matching Tamir\'s excel):', '---------', *additional_midi_with_suggestion, '========','',
                 'additional structure files (not matching Tamir\'s excel):', '---------', *additional_structure_with_suggestion, '========','',
                 'additional chord (not matching Tamir\'s excel):', '---------', *additional_chord_with_suggestion]

    with open(out_csv_path[:-4] + '.txt', 'w') as file:
        file.write('\n'.join(txt_lines))

    print(f"output saved to '{out_csv_path[:-4] + '.txt'}' and '{out_csv_path}'")

    invalid_names_in_excel = [f"'{n}'" for n in df[~df['is_valid_name']][midi_col_name].values]
    print(f"invalid file names in Tamir's excel: ", *invalid_names_in_excel, sep='\n')


    # Validate structure values
    validate_all_structue_file_values(strip_part_names=True)