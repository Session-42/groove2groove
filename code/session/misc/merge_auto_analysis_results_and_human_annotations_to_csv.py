"""Script for unifying Groove2Groove auto analysis results CSV + Human annotations CSV into a single CSV.
This script should be used after using:
1. code/session/misc/process_human_annotation_csv.py - for processing the human annotation in google-sheets (after downloaded as csv) 
2. code/session/misc/collect_auto_analysis_results_to_csv.py - for collecting grv2grv analysis json results
Written by Natan Bibelnik @ MyPart, 2024"""

import pandas as pd
import numpy as np
from pathlib import Path

def get_merged_annotation_df(human_annotation_flat_csv, grv2grv_analysis_csv):
    
    # Read CSVs
    if type(human_annotation_flat_csv)==list:
        df_human = pd.concat([pd.read_csv(single_csv, header=0) for single_csv in human_annotation_flat_csv], axis=0)
    else:    
        df_human = pd.read_csv(human_annotation_flat_csv, header=0) 

    if type(grv2grv_analysis_csv)==list:
        df_auto = pd.concat([pd.read_csv(single_csv, header=0) for single_csv in grv2grv_analysis_csv], axis=0)
    else:    
        df_auto = pd.read_csv(grv2grv_analysis_csv, header=0) 

    human_column_rename_dict = {'Content similarity 0-5': 'human_content_similarity', 
                                'Style (Ref) similarity 0-5': 'human_style_similarity', 
                                'How good it sounds 0-5':'human_quality',
                                }

    df_human = df_human.rename(columns=human_column_rename_dict)

    df_auto['style_name'] = df_auto['style_file'].apply(lambda x: x.rsplit('.',2)[0].strip())
    df_auto['content_name'] = df_auto['content_file'].apply(lambda x: x.rsplit('.',2)[0].strip())
    df_auto['part'] = df_auto['part'].apply(lambda x: x.replace('_no_drum','').replace('PreChorus','Pre_Chorus'))

    # Specify columns to merge on
    merge_columns =  ['style_name', 'content_name', 'part', 'model_name', 'temperature']
    
    # add 'copy_original_drums' criteria for merging,
    # for specific case of original drums vs varient one (relevant to old files and old annotations). 
    if 'copy_original_drums' in df_human.columns:
        df_human['copy_original_drums'] = df_human['copy_original_drums'].apply(bool) & pd.notna(df_human['copy_original_drums'])
        df_auto['copy_original_drums'] = df_auto['output_file'].str.contains('orig_drum')
        merge_columns += ['copy_original_drums']

    # Merge DataFrames based on identical values in specified columns
    df_merged = pd.merge(df_auto, df_human, on=merge_columns, how='inner')
    return df_merged


if __name__ == '__main__':
    
    # input csv OR csvs 
    human_annotation_flat_csv = [
    'Human Annotation Groove2Groove Outputs - Temparature 0.1 Self_Blend (Rendering)_flat.csv',
    'Human Annotation Groove2Groove Outputs - Temparature 0.01 Self_Blend (Rendering)_flat.csv',
    'Human Annotation Groove2Groove Outputs - Tempature 0.4 Self_Blend (Rendering)_flat.csv',
    'Human Annotation Groove2Groove Outputs - Chorus (Mapped)_flat.csv',
    'Human Annotation Groove2Groove Outputs - Verse (Mapped)_flat.csv',
    'Human Annotation Groove2Groove Outputs - Pre_Chorus (Mapped)_flat.csv',
    'Human Annotation Groove2Groove Outputs - Temparature 0.01 Self_Blend (Mapped)_flat.csv',
    'Human Annotation Groove2Groove Outputs - Temparature 0.1 Self_Blend (with varitented drum) _flat.csv',
     ]

    grv2grv_analysis_csv = [
        'grv2grv_analysis_self_blend.csv',
        'grv2grv_analysis.csv',
        'grv2grv_analysis_self_blend_human_mapping.csv', 
        ]

    # out_merged_csv = f'grv2grv_human_and_auto_annotations_self_blend.csv'
    # out_merged_csv = f'grv2grv_human_and_auto_annotations_mapped.csv'
    # out_merged_csv = f'grv2grv_human_and_auto_annotations_human_mapped_self_blend.csv'
    out_merged_csv = f'grv2grv_human_and_auto_annotations_all.csv'


    df_merged = get_merged_annotation_df(human_annotation_flat_csv, grv2grv_analysis_csv)
    df_merged.to_csv(out_merged_csv, index=False)
    print(f"Human annotation + auto analysis results csv with {len(df_merged)} rows saved to '{out_merged_csv}'")
    