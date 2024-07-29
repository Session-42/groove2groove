import os
import subprocess

# Define the path to the conda environment
CONDA_ENV_PATH = "groove2groove3"
GRV2GRV_PATH = "hello_world.py"  


def run_grv2grv(content_midi, style_midi, output_file, model_dir_name, temperature, conda_env = ''):

    grv2grv_command = f"echo python -m groove2groove.models.roll2seq_style_transfer --logdir '{model_dir_name}' run-midi \
        --sample --softmax-temperature {temperature} '{content_midi}' '{style_midi}' '{output_file}'"
    
    if conda_env:
        grv2grv_command = f'conda activate {conda_env}; ' + grv2grv_command
    
    print(grv2grv_command)


if __name__=='__main__':
    grv2grv_kwargs = dict(content_midi='cc.mid', style_midi='ss.mid', output_file='o', model_dir_name='v01_drums', temperature='0.01', conda_env=CONDA_ENV_PATH)
    run_grv2grv(**grv2grv_kwargs)



if __name__ == '__main__':
    # Construct the command to activate the conda environment and run the script
    command = f"conda activate {CONDA_ENV_PATH} ; python {GRV2GRV_PATH}"

    # Run the command using subprocess
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if the command was successful
    if result.returncode == 0:
        print("Script execution successful.")
    else:
        print("Script execution failed.")

    # Print the output and any errors
    print(result.stdout.decode())
    print(result.stderr.decode())

# 
# import os
# import music21


# def run_grv2grv(content_midi, style_midi, output_file, model_dir_name, temperature):

#     grv2grv_command = f"python -m groove2groove.models.roll2seq_style_transfer --logdir '{model_dir_name}' run-midi \
#         --sample --softmax-temperature {temperature} '{content_midi}' '{style_midi}' '{output_file}'"
    
#     print(grv2grv_command)


# if __name__=='__main__':
#     grv2grv_kwargs = dict(content_midi='cc.mid', style_midi='ss.mid', output_file='o', model_dir_name='v01_drums', temperature='0.01')
#     run_grv2grv(**grv2grv_kwargs)


