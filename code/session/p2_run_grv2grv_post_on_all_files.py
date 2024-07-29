from pathlib import Path
from session_grv2grv_pipeline_utils import post_process_midi_file_and_save
import shutil

drum_folder = 'grv2grv_session_data\phase2\preprocessed'
program_dict_folder = 'grv2grv_session_data\phase2\preprocessed'
bpm_folder = 'grv2grv_session_data\phase2\preprocessed_bpm'

post_grv2grv_folder = 'grv2grv_session_data\phase2\self_blend_outputs'
post_grv2grv_folder_sub_folder = 'v0_style_with_v0_content'
output_sub_folder = r'v0_style_with_v0_content_and_v0_drums'

output_root = r'phase2\final_self_blend_outputs_w_bpm2'

RECOMPUTE = False
VERBOSE = True



if __name__ == '__main__':
    automap_back = True
    add_orig_drum = True
    replace_bpm = True

    for midi_grv2grv_out_path in Path(post_grv2grv_folder).glob('v01_drums_vel/*/' + post_grv2grv_folder_sub_folder + '/*.mid'):   
        # create output path
        suffix = 'post_orig_drum' if add_orig_drum else 'post'
        output_midi_file_name = midi_grv2grv_out_path.stem.split('.X.')[-1] + f'.{suffix}.midi'
        
        # define output folder
        ## add subfolder in the existing tree stucture
        # output_folder = midi_grv2grv_out_path.parent.parent / output_sub_folder
        
        # OR create identical tree + add sub folder with the project name (file-name up to the first dot):
        output_folder = Path(str(midi_grv2grv_out_path.parent).replace(post_grv2grv_folder, output_root)) / output_midi_file_name.split('.')[0]
        post_processing_output_midi_path = output_folder / output_midi_file_name

        if not RECOMPUTE and post_processing_output_midi_path.exists():
            print(f"output post-processes file '{post_processing_output_midi_path}' exists. skipping")
            continue

        # file names:
        # take the drum file from content #in principle should be from the style:
        program_dict_path = Path(program_dict_folder) / (midi_grv2grv_out_path.stem.split('.X.')[0].rsplit('.',2)[0] + '.program_dict.json') if automap_back else None

        # take the drum file from content:
        drum_midi_path = Path(drum_folder) / (midi_grv2grv_out_path.stem.split('.X.')[0].replace('no_drum','only_drum') + '.mid') if add_orig_drum else None
                
        # use bpm for replacing bpm in midi and also copy to the output folder
        bpm_path =  Path(bpm_folder) / (midi_grv2grv_out_path.stem.split('.X.')[0].rsplit('.',2)[0] + '.bpm.txt') if replace_bpm else None

        # copy bpm file
        if bpm_path.exists():
            bpm_new_path = post_processing_output_midi_path.parent / bpm_path.name
            # create output folder if required
            if not Path(post_processing_output_midi_path).parent.exists():
                if VERBOSE:
                    print(f"Creating post-processing output folder: '{Path(post_processing_output_midi_path).parent}'")
                Path(post_processing_output_midi_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(bpm_path), str(bpm_new_path))
            if VERBOSE:
                print(f'copy {bpm_path} -> {bpm_new_path}')

        post_process_midi_file_and_save(midi_grv2grv_out_path = midi_grv2grv_out_path, 
                                         post_processing_output_midi_path = post_processing_output_midi_path, 
                                         automap_back = automap_back,
                                         program_dict_path = program_dict_path,
                                         add_orig_drum = add_orig_drum,
                                         drum_midi_path= drum_midi_path,
                                         replace_bpm = replace_bpm,
                                         bpm_path = bpm_path,
                                         replace_if_file_exist = RECOMPUTE, 
                                         verbose = VERBOSE)

