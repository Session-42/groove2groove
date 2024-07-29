""" Script for post-processing groove2groove outputs MIDI files, including reversing auto program midi mapping, 
adding original drums, etc.

Running example: 
python post_process_midi.py /path/to/midi_grv2grv_output.midi /path/to/post_processed_output.midi --automap_back True --program_dict_path /path/to/program_dict.json --add_orig_drum True --drum_midi_path /path/to/drum.midi --replace_bpm False --bpm_path /path/to/bpm.txt --replace_if_file_exist True --verbose True
"""

import argparse
from typing import List, Optional
from session_grv2grv_pipeline_utils import post_process_midi_file_and_save

# mock
def get_arguments():
    parser = argparse.ArgumentParser(description='Post-process MIDI files and save the output.')

    parser.add_argument('midi_grv2grv_out_path', type=str, help='Path to the MIDI GRV2GRV output file.')
    parser.add_argument('post_processing_output_midi_path', type=str, help='Path to save the post-processed MIDI file.')
    parser.add_argument('--automap_back', type=bool, default=False, help='Automap back.')
    parser.add_argument('--program_dict_path', type=str, help='Path to the program dictionary file.', default=None)
    parser.add_argument('--add_orig_drum', type=bool, default=True, help='Add original drum. Default is True.')
    parser.add_argument('--drum_midi_path', type=str, help='Path to the drum MIDI file.', default=None)
    parser.add_argument('--replace_bpm', type=bool, default=False, help='Replace BPM. Default is False.')
    parser.add_argument('--bpm_path', type=str, help='Path to the BPM file.', default=None)
    parser.add_argument('--replace_if_file_exist', type=bool, default=True, help='Replace if file exists. Default is True.')
    parser.add_argument('--verbose', type=bool, default=True, help='Verbose output. Default is True.')

    return parser.parse_args()

def post_process_midi_file_and_save_mock(midi_grv2grv_out_path: str, 
                                     post_processing_output_midi_path: str, 
                                     automap_back: bool,
                                     program_dict_path: Optional[str] = None,
                                     add_orig_drum: bool = True,
                                     drum_midi_path: Optional[str] = None,
                                     replace_bpm: bool = False,
                                     bpm_path: Optional[str] = None,
                                     replace_if_file_exist: bool = True,
                                     verbose: bool = True):
    
    # Your function implementation here
    print(f"Processing MIDI GRV2GRV output file: {midi_grv2grv_out_path}")
    print(f"Post-processing output MIDI path: {post_processing_output_midi_path}")
    print(f"Automap back: {automap_back}")
    print(f"Program dictionary path: {program_dict_path}")
    print(f"Add original drum: {add_orig_drum}")
    print(f"Drum MIDI path: {drum_midi_path}")
    print(f"Replace BPM: {replace_bpm}")
    print(f"BPM path: {bpm_path}")
    print(f"Replace if file exists: {replace_if_file_exist}")
    print(f"Verbose: {verbose}")


if __name__ == "__main__":
    args = get_arguments()
    post_process_midi_file_and_save(
        midi_grv2grv_out_path=args.midi_grv2grv_out_path,
        post_processing_output_midi_path=args.post_processing_output_midi_path,
        automap_back=args.automap_back,
        program_dict_path=args.program_dict_path,
        add_orig_drum=args.add_orig_drum,
        drum_midi_path=args.drum_midi_path,
        replace_bpm=args.replace_bpm,
        bpm_path=args.bpm_path,
        replace_if_file_exist=args.replace_if_file_exist,
        verbose=args.verbose
    )
    