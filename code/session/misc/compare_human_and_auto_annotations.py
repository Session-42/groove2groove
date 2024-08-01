"""Script of analysis of human annotation vs grv2grv metrics - from csv + plotting.
Written by Natan Bibelnik @ MyPart, 2024"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib

SAVE_IMAGES = True 
SHOW_IMAGES = True 
MATCH_REGRESSION = True
# add different colors by column name (vale can also be None or False)
COLOR_CATEGORY_NAME = None  #'temperature' #'model_name' #'style_file' 

human_and_auto_annotations_csv = r'code_for_sync\annotation_and_analysis\grv2grv_human_and_auto_annotations_all.csv'
out_dir = r'code_for_sync\annotation_and_analysis\annotation_figures'

if __name__ == '__main__':
    df = pd.read_csv(human_and_auto_annotations_csv, sep=',')

    compare_list = [['content_score','human_content_similarity'],
                    ['time_pitch_diff','human_style_similarity'],
                    ['onset.duration', 'human_style_similarity'],
                    ['onset.drum_drums','human_style_similarity'],
                    ['onset.velocity', 'human_style_similarity']]

    # convert non-numerics values to nan:
    compare_list_unique_columns = list(set(sum(compare_list, [])))
    df[compare_list_unique_columns] = df[compare_list_unique_columns].apply(pd.to_numeric, errors='coerce')

    # remove drum metrics from files with original drums:
    if 'copy_original_drums' in df.columns:
        df.loc[df['copy_original_drums'], ['onset.drum_drums']] = pd.NA

    xlim = (-0.1,1.1)
    ylim = (-0.5,5.5)

    if SAVE_IMAGES:
        if not Path(out_dir).exists():
            Path(out_dir).mkdir(parents=True, exist_ok=True)
            print(f"fig output dir '{out_dir}' was created")
    # define colors by category name
    if COLOR_CATEGORY_NAME:
        color_category_list = df[COLOR_CATEGORY_NAME].unique()
        # sort if numeric
        if np.issubdtype(color_category_list.dtype, np.number):
            color_category_list.sort()

        cm = matplotlib.colormaps.get_cmap('tab20')
        color_list = [cm(i / len(color_category_list)) for i in range(len(color_category_list))]
        color_map_dict = dict(zip(color_category_list, color_list))
        colors = df[COLOR_CATEGORY_NAME].map(color_map_dict)
        hist_kwargs = dict(stacked=True, 
                    color=color_list,  
                    label=[f'{COLOR_CATEGORY_NAME}: {label}' for label in color_category_list])
    else:
        colors='C0'
        hist_kwargs = {}
    color_save_str = f'_by_{COLOR_CATEGORY_NAME}_color' if COLOR_CATEGORY_NAME else ''

    for x,y in compare_list:
        correlation = df[x].corr(df[y])
        num_valid_data_points = pd.notnull(df[[x,y]]).all(axis=1).sum()
        df.plot(x=x, y=y, kind='scatter', title=f'{y} vs {x}\n(correlation = {correlation:0.2f} @ {num_valid_data_points} data points).',
                xlim=xlim, ylim=ylim, label='data', color=colors)

        if MATCH_REGRESSION:
            try:
                fit = np.polyfit(df[x], df[y], 1)
                fit_fn = np.poly1d(fit)
                plt.plot(df[x], fit_fn(df[x]), color='red', label=f'Regression line (correlation={correlation:.2f})')
            except:
                print(f'could not match regression line for {y} vs {x}')

        if COLOR_CATEGORY_NAME:
            patches = [matplotlib.patches.Patch(color=color, label=f'{COLOR_CATEGORY_NAME}: {label}') for label,color in color_map_dict.items()]
            plt.legend(handles=patches)

        if SAVE_IMAGES:
            plt.savefig(f"{out_dir}/grv2grv_{y}_vs_{x}{color_save_str}.png")

        data_for_y_hist = [df[colors==c][y] for c in color_list] if COLOR_CATEGORY_NAME else df[y]

        plt.figure()
        plt.hist(data_for_y_hist, **hist_kwargs)
        plt.title(y); plt.ylabel('hist count'); plt.xlabel(f'{y} score')
        if COLOR_CATEGORY_NAME:
            plt.legend()
        if SAVE_IMAGES:
            plt.savefig(f'{out_dir}/grv2grv_hist_{y}{color_save_str}.png')

        data_for_x_hist = [df[colors==c][x] for c in color_list] if COLOR_CATEGORY_NAME else df[x]
        plt.figure()
        plt.hist(data_for_x_hist, **hist_kwargs)
        plt.title(x); plt.ylabel('hist count'); plt.xlabel(f'{x} similarity score')
        if COLOR_CATEGORY_NAME:
            plt.legend()
        if SAVE_IMAGES:
            plt.savefig(f'{out_dir}/grv2grv_hist_{x}{color_save_str}.png')

    if SHOW_IMAGES: 
        plt.show()
    else:
        plt.close('all')