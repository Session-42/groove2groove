from pathlib import Path
import pandas as pd
from session_grv2grv_pipeline_utils import pre_process_midi_file_and_save

id_col_name = 'ID'
midi_col_name = 'Midi Tracks Titles'

midi_path_col_name = 'relative_path_midi'
st_path_col_name = 'relative_path_st'


midi_root_folder = r'phase2\HitCraft - All Files Bank'

# output excel with valid paths, the output of "p2_run_grv2grv_input_filename_validation.py"
valid_excel_csv_path = r'phase2\valid_phase2_files_all.csv'

preprocess_out_folder = r'grv2grv_session_data\phase2\preprocessed_bpm2'

out_csv_path = r'phase2\valid_phase2_files.csv'
RECOMPUTE=True
SKIP_IF_ANY_FILE=False
VERBOSE=True


if __name__ == '__main__': 
    df = pd.read_csv(valid_excel_csv_path)
    
    for index, row in df.iterrows():
        try:
            midi_path = Path(midi_root_folder) / row[midi_path_col_name]
            structure_xls_path = Path(midi_root_folder) / row[st_path_col_name]
            if not midi_path.exists():
                print(f'skipping.. midi file {midi_path} cannot be found.')
                continue
            if not structure_xls_path.exists():
                print(f'skipping.. structure xls file {structure_xls_path} cannot be found.')
                continue

            stem_out = Path(midi_path).stem
            if SKIP_IF_ANY_FILE and len(list(Path(preprocess_out_folder).glob(stem_out + '.*.mid'))):
                if VERBOSE:
                    print(f"skipping, existing:", [str(a) for a in Path(preprocess_out_folder).glob(stem_out + '.*.mid')])
                continue

            pre_process_midi_file_and_save(midi_path, structure_xls_path, preprocess_out_folder, required_parts=['Verse','Chorus','Pre Chorus'],
                                 auto_map_midi = True, split_drum = True, replace_if_file_exist = RECOMPUTE, verbose=VERBOSE)

        except Exception as e:
            print(f'Error for: {Path(row[midi_path_col_name]).name}, Exception {e}')
