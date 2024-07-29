#!/bin/bash

# Function to display usage
usage() {
  echo "Usage: $0 -i input_midi_path -s structure_xls_path -o out_folder [-p required_parts] [-m auto_midi_map] [-r replace_if_file_exist] [-v verbose] [-d add_orig_drum] [-b replace_bpm] [-n model_name] [-t temperature]"
  exit 1
}

# definitions of environments: #TODO: should be given as params
python_grv2grv=/home/ubuntu/.conda/envs/groove2groove/bin/python
python_session=/home/ubuntu/.conda/envs/session/bin/python

# Default values for optional arguments
auto_midi_map=True
replace_if_file_exist=True
verbose=True
add_orig_drum=True
replace_bpm=False
model_name='v01_drums'
temperature='0.4'
required_parts=('Verse' 'Chorus')

# Parse command line arguments
while getopts "i:s:o:p:m:r:v:d:t:n" opt; do
  case $opt in
    i) input_midi_path="$OPTARG" ;;
    s) structure_xls_path="$OPTARG" ;;
    o) out_folder="$OPTARG" ;;
    m) auto_midi_map="$OPTARG" ;;
    r) replace_if_file_exist="$OPTARG" ;;
    v) verbose="$OPTARG" ;;
    d) add_orig_drum="$OPTARG" ;;
    b) replace_bpm="$OPTARG" ;;
    t) temperature="$OPTARG" ;;
    n) model_name="$OPTARG" ;; 
    *) usage ;;
  esac
done

# Check for mandatory arguments
if [ -z "$input_midi_path" ] || [ -z "$structure_xls_path" ] || [ -z "$out_folder" ]; then
  usage
fi


# Check if the input midi file exists
if [ ! -f "$input_midi_path" ]; then
  echo "Midi input file $input_midi_path does not exist."
  exit 1
fi
# Check if the structure xls exists
if [ ! -f "$structure_xls_path" ]; then
  echo "Structure xls $structure_xls_path does not exist."
  exit 1
fi

temp_out_folder="${out_folder}"/temp

if [ ! -d "$temp_out_folder" ]; then
    # If the folder doesn't exist, create it
    mkdir -p "$temp_out_folder"
    if [ "$verbose" = "True" ]; then
        echo "Temp Output Folder created at ${temp_out_folder}"
    fi
fi

base_name=$(basename "$input_midi_path")
base_name_without_extension="${base_name%.*}"
echo "base_name_without_extension: ${base_name_without_extension}"

program_dict_path="${temp_out_folder}/${base_name_without_extension}.program_dict.json"
bpm_path="${temp_out_folder}/${base_name_without_extension}.bpm.txt"


# Call the pre_process_midi script and split the midi by structure parts and drums
$python_session pre_process_midi.py "$input_midi_path" "$structure_xls_path" "$temp_out_folder" --required_parts $required_parts --auto_map_midi "$auto_midi_map" --split_drum "$add_orig_drum" --replace_if_file_exist "$replace_if_file_exist" --verbose "$verbose"

for part in "${required_parts[@]}"; do
  echo "Processing part: $part"
  pre_processed_midi_part_only_drum="${temp_out_folder}/${base_name_without_extension}.${part}_only_drum.mid"
  pre_processed_midi_part_no_drum="${temp_out_folder}/${base_name_without_extension}.${part}_no_drum.mid"

  midi_grv2grv_out_path="${temp_out_folder}/${base_name_without_extension}.${part}_only_drum.grv2grv.mid"
  post_processing_output_midi_path="${out_folder}/${base_name_without_extension}.${part}_self_blended.mid"


  if [ -e "$midi_grv2grv_out_path" ] && [ "$replace_if_file_exist" != "True" ]; then
    if [ "$verbose" = "True" ]; then
      echo "Grv2grv Output file ${midi_grv2grv_out_path} already exists. Skipping..."
    fi
  else
    if [ "$verbose" = "True" ]; then
      echo "Working to create grv2grv output ${midi_grv2grv_out_path} (input is ${pre_processed_midi_part_no_drum})"
    fi

    cd ~/groove2groove
    model_dir=experiments/"$model_name"
    sudo $python_grv2grv -m groove2groove.models.roll2seq_style_transfer --logdir "${model_dir}" run-midi \
    --sample --softmax-temperature "$temperature" \
    "${pre_processed_midi_part_no_drum}" \
    "${pre_processed_midi_part_no_drum}" \
    "${midi_grv2grv_out_path}"
    if [ "$verbose" = "True" ]; then
      echo "done with ${midi_grv2grv_out_path}"
    fi
  fi
  cd ~/groove2groove/code/session
  "$python_session" post_process_midi.py "$midi_grv2grv_out_path" "$post_processing_output_midi_path" --automap_back "$auto_midi_map" --program_dict_path "$program_dict_path" --add_orig_drum "$add_orig_drum" --drum_midi_path "$pre_processed_midi_part_only_drum" --replace_bpm "$replace_bpm" --bpm_path "$bpm_path" --replace_if_file_exist "$replace_if_file_exist" --verbose "$verbose"

done


echo "--------------------------"

# Call the post_process_midi script
