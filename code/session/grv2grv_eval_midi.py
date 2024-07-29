import os
from note_seq import midi_io
from note_seq.protobuf.music_pb2 import NoteSequence
from museflow.note_sequence_utils import filter_sequence 
from confugue import Configuration
import scipy
from pathlib import Path
import pandas as pd
from groove2groove.eval.style_profiles import extract_all_stats
from groove2groove.eval.notes_chroma_similarity import chroma_similarity


COMPARE_ONLY_MATCHING = True
model_name_dict = {'N':'None', 'V':'Velocity', 'DV':'Drums and Velocity', 'D': 'Drums'}

#pretty_midi.PrettyMIDI
STYLE_PROFILE_DIR = 'experiments/eval/style_profiles'
STYLE_PROFILE_CFG_PATH = os.path.join(STYLE_PROFILE_DIR, 'config.yaml')
STYLE_PROFILE_DRUMS_CFG_PATH = os.path.join(STYLE_PROFILE_DIR, 'config_drums.yaml')
# OUT_PREFIX = 'out/'
# INSTRUMENTS = ['Bass', 'Piano', 'Guitar', 'Strings']
# DRUMS = ['Drums']

with open(STYLE_PROFILE_CFG_PATH, 'rb') as f:
    STYLE_PROFILE_FN = Configuration.from_yaml(f).bind(extract_all_stats)
with open(STYLE_PROFILE_DRUMS_CFG_PATH, 'rb') as f:
    STYLE_PROFILE_DRUMS_FN = Configuration.from_yaml(f).bind(extract_all_stats)


def evaluate_content(sequence, reference):
    """Evaluate the content similarity of a sequence to a reference."""
    # Is filtering the sequence necessary?
    sequence = filter_sequence(sequence, drums=False, copy=True)
    reference = filter_sequence(reference, drums=False, copy=True)
    return {
        'content_score': chroma_similarity(sequence, reference,
                                     sampling_rate=12, window_size=24, stride=12, use_velocity=False)
    }


def cosine_similarity(hist1, hist2):
    return 1. - scipy.spatial.distance.cosine(hist1.reshape(1, -1), hist2.reshape(1, -1))

def filter_sequences(sequences, **kwargs):
    return [filter_sequence(seq, copy=True, **kwargs) for seq in sequences]


def evaluate_style(sequences, ref_stats=None, ref_sequences=None, is_drum=False, separate_drums=False):
    """Evaluate the style similarity of a set of sequences to a reference."""
    sequences = filter_sequences(sequences, drums=is_drum) #programs=[out_program]  # what about seperating each instrument? or each program=track?
    if ref_sequences is not None:
        ref_sequences = filter_sequences(ref_sequences, drums=is_drum)

    extract_fn = STYLE_PROFILE_FN if not is_drum else STYLE_PROFILE_DRUMS_FN
    stats = extract_fn(data=sequences)
    if ref_stats is None:
        ref_stats = extract_fn(data=ref_sequences)
    metrics = {name + ('_drums' if is_drum and separate_drums else ''):
                   cosine_similarity(stats[name], ref_stats[name])
               for name in stats if name in ref_stats}

    return metrics

def analyze_output_name(path):
    output_name_data_dict = {}
    info_list = str(path).rsplit('.',3)
    if len(info_list) >=4:
        output_name_data_dict['part'] = info_list[-3]
    if len(info_list) >= 3:
        model_name, temp_str = info_list[-2].split('_')
        model_name = model_name_dict.get(model_name, model_name)
        output_name_data_dict['model_name'] = model_name
        if temp_str.startswith('T'):
            temp_str = f'{temp_str[1]}.{temp_str[2:]}'
        output_name_data_dict['temperature'] = temp_str
    return output_name_data_dict

def analyze_output(cont_midi_path, style_midi_path, out_midi_path):
    results = {}
    results['output_file'] = Path(out_midi_path).name 
    results['content_file'] = Path(cont_midi_path).name
    results['style_file']  = Path(style_midi_path).name
    results.update(analyze_output_name(out_midi_path))

    cont_midi  = midi_io.midi_file_to_note_sequence(cont_midi_path)
    style_midi = midi_io.midi_file_to_note_sequence(style_midi_path)
    out_midi   = midi_io.midi_file_to_note_sequence(out_midi_path)
    results.update(evaluate_content(out_midi, cont_midi))

    # TODO: understant the drum thing! IMPORTANT

    style_metrics = evaluate_style(sequences=[out_midi], ref_sequences=[style_midi], is_drum = False)
    results.update(style_metrics)
    style_metrics = evaluate_style(sequences=[out_midi], ref_sequences=[style_midi], is_drum = True, separate_drums=True)
    results.update(style_metrics)

    print(f'Evaluating {out_midi_path}:')
    print(f'Content: {Path(cont_midi_path).name}, Style: {Path(style_midi_path).name}')
    
    # delete the following entities:
    for key_to_delete in ['time_pitch_diff_drums', 'onset.velocity_drums']:
        if key_to_delete in results:
            results.pop(key_to_delete)

    return results


if __name__=='__main__':
#    style_midi_path = 'data/grv2grv_session_data/grv2grv_session_data/Apologize Second verse.mid' 
#    out_midi_path = 'data/grv2grv_session_data/grv2grv_session_data/outputs/zilo_chords_apologize_second_verse.mid'
#   cont_midi_path = 'data/grv2grv_session_data/grv2grv_session_data/zilo_chords.mid'

    cont_midi_dir = 'data/grv2grv_session_data/grv2grv_session_data/content_inputs' 
    style_midi_dir = 'data/grv2grv_session_data/grv2grv_session_data/inputs'
    out_midi_dir = 'data/grv2grv_session_data/grv2grv_session_data/outputs'

    results_file = 'data/grv2grv_session_data/grv2grv_session_data/grv2grv_analysis2.csv'
    all_results_match = []
    if not COMPARE_ONLY_MATCHING:
        results_file_all_content_combinations = 'data/grv2grv_session_data/grv2grv_session_data/grv2grv_analysis_all_content_combinations.csv'
        results_file_all_style_combinations = 'data/grv2grv_session_data/grv2grv_session_data/grv2grv_analysis_all_style_combinations.csv'
        all_results_content_combinations = []
        all_results_content_combinations = []

    # cont_midi_path = 'data/grv2grv_session_data/grv2grv_session_data/zilo_chords.mid' 
    # style_midi_path = 'data/grv2grv_session_data/grv2grv_session_data/Apologize Second verse.mid' 
    # out_midi_path = 'data/grv2grv_session_data/grv2grv_session_data/outputs/zilo_chords_apologize_second_verse.mid'

    for out_midi_path in Path(out_midi_dir).glob('*/*/*/*.mid'):
        try:
            content_name = Path(out_midi_path).name.split('-',1)[0]
            style_name = Path(out_midi_path).name.split('-',1)[1].rsplit('.',2)[0] 
        except Exception as e:
            print(f'Output {out_midi_path} is expected to have "<Content>-<Style>.<folder info>.mid" format, Error {e}')
            continue
    
        # Compare the output to its style and content midi files
        try:
            cont_midi_path = next(Path(cont_midi_dir).glob(content_name + '.*'))
            style_midi_path = next(Path(style_midi_dir).glob(style_name + '.*'))
            print(f'cont_midi_path: {cont_midi_path};  style_midi_path: {style_midi_path}')
        except Exception as e:
            print(f'Could not match input files, {e}')
            continue

        results = analyze_output(cont_midi_path=cont_midi_path, style_midi_path=style_midi_path, out_midi_path=out_midi_path)
        if results:
            all_results_match.append(results)

        if not COMPARE_ONLY_MATCHING:
            # Compare the output to Other Content, Same style:
            for cont_midi_path in Path(cont_midi_dir).glob('*'):
                try:
                    style_midi_path = next(Path(style_midi_dir).glob(style_name + '.*'))
                    
                    print(f'cont_midi_path: {cont_midi_path};  style_midi_path: {style_midi_path}')
                except Exception as e:
                    print(f'Could not match input files, {e}')
                    continue
        
                results = analyze_output(cont_midi_path=cont_midi_path, style_midi_path=style_midi_path, out_midi_path=out_midi_path)
                if results:
                    all_results_content_combinations.append(results)


            for style_midi_path in Path(style_midi_dir).glob('*'):
                # Compare the output to Other Styles, Same content:
                    try:
                        cont_midi_path = next(Path(cont_midi_dir).glob(content_name + '.*'))
                        print(f'cont_midi_path: {cont_midi_path};  style_midi_path: {style_midi_path}')
                    except Exception as e:
                        print(f'Could not match input files, {e}')
                        continue
            
                    results = analyze_output(cont_midi_path=cont_midi_path, style_midi_path=style_midi_path, out_midi_path=out_midi_path)
                    if results:
                        all_results_content_combinations.append(results)

    df_all_results_match = pd.DataFrame(all_results_match)
    df_all_results_match.to_csv(results_file, index=False)
    print(f'matching results saved to: {results_file}')

    if not COMPARE_ONLY_MATCHING:
        df_all_content_combinations = pd.DataFrame(all_results_content_combinations)
        df_all_content_combinations.to_csv(results_file_all_content_combinations, index=False)
        print(f'content combination results saved to: {results_file_all_content_combinations}')

        df_all_style_combinations = pd.DataFrame(all_results_content_combinations)
        df_all_style_combinations.to_csv(results_file_all_style_combinations, index=False)
        print(f'style combination results saved to: {results_file_all_style_combinations}')
