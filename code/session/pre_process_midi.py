""" Script for preprocessing MIDI files, including cropping, automatic program midi mapping, splitting drums, etc.

Running example: 
python pre_process_midi.py /path/to/input.midi /path/to/structure.xlsx /path/to/output/folder --required_parts Verse Chorus --auto_map_midi True --split_drum True --replace_if_file_exist True --verbose True
"""

import argparse
from typing import List

from session_grv2grv_pipeline_utils import pre_process_midi_file_and_save

# mock
def pre_process_midi_file_and_save_mock(input_midi_path: str, structure_xls_path: str, preprocess_out_folder: str, 
                                   required_parts: List[str] = ['Verse', 'Chorus', 'Pre Chorus'],
                                   auto_map_midi: bool = True, split_drum: bool = True, 
                                   replace_if_file_exist: bool = True, verbose: bool = True) -> List[str]:
    # Your function implementation here
    print(f"Processing MIDI file: {input_midi_path}")
    print(f"Structure XLS path: {structure_xls_path}")
    print(f"Output folder: {preprocess_out_folder}")
    print(f"Required parts: {required_parts}")
    print(f"Auto map MIDI: {auto_map_midi}")
    print(f"Split drum: {split_drum}")
    print(f"Replace if file exists: {replace_if_file_exist}")
    print(f"Verbose: {verbose}")


def get_arguments():
    parser = argparse.ArgumentParser(description='Pre-process a MIDI file and save the output.')
    parser.add_argument('input_midi_path', type=str, help='Path to the input MIDI file.')
    parser.add_argument('structure_xls_path', type=str, help='Path to the structure XLS file.')
    parser.add_argument('preprocess_out_folder', type=str, help='Folder to save the preprocessed output.')
    parser.add_argument('--required_parts', type=str, nargs='*', default=['Verse', 'Chorus', 'Pre Chorus'], 
                        help='List of required structure parts if available. Default is ["Verse", "Chorus", "Pre Chorus"].')
    parser.add_argument('--auto_map_midi', type=bool, default=True, help='Auto program map MIDI. Default is True.')
    parser.add_argument('--split_drum', type=bool, default=True, help='Split drum to a different midi. Default is True.')
    parser.add_argument('--replace_if_file_exist', type=bool, default=True, help='Replace if file exists. Default is True.')
    parser.add_argument('--verbose', type=bool, default=True, help='Verbose output. Default is True.')

    return parser.parse_args()


if __name__ == "__main__":
    args = get_arguments()
    pre_process_midi_file_and_save(
        input_midi_path=args.input_midi_path,
        structure_xls_path=args.structure_xls_path,
        preprocess_out_folder=args.preprocess_out_folder,
        required_parts=args.required_parts,
        auto_map_midi=args.auto_map_midi,
        split_drum=args.split_drum,
        replace_if_file_exist=args.replace_if_file_exist,
        verbose=args.verbose
    )