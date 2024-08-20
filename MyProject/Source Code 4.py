# Preparation
import pandas as pd
import numpy as np
import seaborn as sns
import os
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
from sklearn.preprocessing import normalize

import fanc
client = fanc.get_caveclient()

from scipy.spatial import distance

from meshparty import trimesh_io, meshwork, mesh_filters
import navis
import pcg_skel
import pandas as pd

from fanc import auth

version_number=client.materialize.version

def post_neurons_2(neuron_a, sc_limit):
    """
    Find downstream neurons of the neuron_a, which has more than 'sc_limit' synapses with neuron_a.
        Args: 
            neuron_a (int) : segment ID # of a neuron of interest.
            sc_limit (int) : minimum synaps count for cutting off.
        Return: a table of downstream neurons and synaps counts as DataFrame."""
    # Get synapse position table of downstream neurons of neuron_a. Each row represents one synaps position.
    post_df = client.materialize.synapse_query(pre_ids = neuron_a, materialization_version=version_number)
    if len(post_df) == 0:
        print('Check if ID# is current or No downstream neurons of ' + str(neuron_a))
    # Choose oly required columns.
    post_df2 = post_df[['id','pre_pt_root_id', 'post_pt_root_id']]
    # Data type of id#s will be changed from 'int' to 'str' to avoid any problem caused by transformation etc.
    post_df2[['id','pre_pt_root_id','post_pt_root_id' ]] = post_df2[['id','pre_pt_root_id','post_pt_root_id' ]].astype('str')
    # Transform # of rows to synapse count. Then add these numbers to a new column 'synaps_count' and sort them as descending.
    synaps_count = post_df2.groupby('post_pt_root_id').transform(len)['id']
    post_df2['synaps_count'] = synaps_count
    post_df3 = post_df2.sort_values('synaps_count', ascending=False)
    # Make one row represent one downstream neuron. Clean the table by dropping unnecessary columns. 
    # Cut off neurons which have syanpse count fewer than 'sc_limit'.
    post_df4 = post_df3.drop_duplicates(subset='post_pt_root_id', keep='first')
    post_df5 = post_df4.loc[post_df4['synaps_count'] >= sc_limit].drop (columns = 'id')
    
    return post_df5

def pre_neurons(neuron_a, sc_limit):
    """
    Find upstream neurons of the neuron_a, which has more than 'sc_limit' synapses with neuron_a.
        Args: 
            neuron_a (int) : segment ID # of a neuron of interest.
            sc_limit (int) : minimum synaps count for cutting off.

        Return: a table of upstream neurons and synaps counts as DataFrame."""            
    # Get synapse position table of upstream neurons of neuron_a. Each row represents one synaps position.    
    pre_df = client.materialize.synapse_query(post_ids = neuron_a, materialization_version=version_number)
    if len(pre_df) == 0:
        print('Check if ID# is current or No upstream neurons of ' + str(neuron_a))
    # Choose only required columns.
    pre_df2 = pre_df[['id','pre_pt_root_id', 'post_pt_root_id']]
    # Data type of id#s will be changed from 'int' to 'str' to avoid any problem caused by transformation etc.
    pre_df2[['id','pre_pt_root_id','post_pt_root_id' ]] = pre_df2[['id','pre_pt_root_id','post_pt_root_id' ]].astype('str')
    # Transform # of rows to synapse count. Then add these numbers to a new column 'synaps_count' and sort them as descending.
    synaps_count = pre_df2.groupby('pre_pt_root_id').transform(len)['id']
    pre_df2['synaps_count'] = synaps_count
    pre_df3 = pre_df2.sort_values('synaps_count', ascending=False)
    # Make one row represent one downstream neuron. Clean the table by dropping unnecessary columns. 
    # Cut off neurons which have syanpse count fewer than 'sc_limit'.
    pre_df4 = pre_df3.drop_duplicates(subset='pre_pt_root_id', keep='first')
    pre_df5 = pre_df4.loc[pre_df4['synaps_count'] >= sc_limit].drop (columns = 'id')
    
    return pre_df5

# Function to create skeleton
def get_pcg_skeleton(segid, **kwargs):
    try:
        if 'client' not in kwargs:
            kwargs['client'] = auth.get_caveclient()
        return pcg_skel.pcg_skeleton(segid, **kwargs)
    except Exception as e:
        raise Exception(f"Error retrieving skeleton for segment ID {segid}: {e}")

# Function to flip skeleton horizontally
def flip_skeleton_horizontally(skeleton):
    flipped_vertices = skeleton.vertices.copy()
    flipped_vertices[:, 0] = -flipped_vertices[:, 0]
    skeleton.vertices = flipped_vertices
    return skeleton


# Function to save skeleton in SWC format
def save_swc(skeleton, filename):
    with open(filename, 'w') as file:
        for i, vertex in enumerate(skeleton.vertices):
            line = f"{i+1} 3 {vertex[0]} {vertex[1]} {vertex[2]} 1.0 -1\n"
            file.write(line)

# set up threashold of synapse count. Only more than this s.c connection is considered to be meaningful connection.
sc_limit = 10

neuron_1 =  648518346478550356
#IN_011_left change the segment ID

# Find downstream neurons of neuron_1 using function 'post_neurons_2'.
neuron_1_post_df = post_neurons_2(neuron_1,sc_limit )
neuron_1_post_df

# Create output directory if it doesn't exist
output_dir = "left_swc_files"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Assuming neuron_1_post_df is already defined and contains the necessary data
# Get the list of post_pt_root_ids
post_neuron_ids = neuron_1_post_df['post_pt_root_id'].tolist()

# Download and save SWC files for each post_neuron
for idx, neuron_id in enumerate(post_neuron_ids):
    try:
        skeleton = get_pcg_skeleton(int(neuron_id))
        filename = os.path.join(output_dir, f"left_neuron_{neuron_id}.swc")
        save_swc(skeleton, filename)
        print(f"Saved SWC file for neuron {neuron_id} at {filename}")
    except Exception as e:
        print(f"Failed to retrieve or save skeleton for neuron {neuron_id}: {e}")

neuron_1 = 648518346492614075
# Find downstream neurons of neuron_1 using function 'post_neurons_2'
neuron_1_post_df = post_neurons_2(neuron_1, sc_limit)
print(neuron_1_post_df)

# Create output directory if it doesn't exist
output_dir = "right_swc_files"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Assuming neuron_1_post_df is already defined and contains the necessary data
# Get the list of post_pt_root_ids
post_neuron_ids = neuron_1_post_df['post_pt_root_id'].tolist()

# Download, flip, and save SWC files for each post_neuron
for idx, neuron_id in enumerate(post_neuron_ids):
    try:
        skeleton = get_pcg_skeleton(int(neuron_id))
        flipped_skeleton = flip_skeleton_horizontally(skeleton)
        filename = os.path.join(output_dir, f"right_flipped_neuron_{neuron_id}.swc")
        save_swc(flipped_skeleton, filename)
        print(f"Saved SWC file for flipped neuron {neuron_id} at {filename}")
    except Exception as e:
        print(f"Failed to retrieve or save skeleton for neuron {neuron_id}: {e}")

# NBLAST comparison
results = []

# 左側のニューロンが保存されているディレクトリ
left_output_dir = "left_swc_files"

# 反転した右側ニューロンが保存されているディレクトリ
right_flipped_dir = "right_swc_files"

# スコアを格納する空のリストを初期化
min_size = 10

# 右側のニューロンSWCファイルを一つ一つ処理する
for right_file in os.listdir(right_flipped_dir):
    if right_file.endswith(".swc"):
        right_neuron_path = os.path.join(right_flipped_dir, right_file)
        right_neuron = navis.read_swc(right_neuron_path)
        right_neuron.units = 'um'  # 単位が正しく設定されていることを確認
        flipped_right_dotprop = navis.make_dotprops(right_neuron)
        # スコアを格納する空のリストを初期化
        scores = []
        # 左側のニューロンSWCファイルを一つ一つ処理する
        for left_file in os.listdir(left_output_dir):
            if left_file.endswith(".swc"):
                left_neuron_path = os.path.join(left_output_dir, left_file)
                left_neuron = navis.read_swc(left_neuron_path)
                left_neuron.units = 'um'  # 単位が正しく設定されていることを確認
                left_dotprop = navis.make_dotprops(left_neuron)
                # サイズが小さすぎるニューロンをスキップ
                if len(left_dotprop) >= min_size:
                    # 反転した右側のニューロンと現在の左側のニューロンの間でNBLASTスコアを計算
                    nblast_scores_df = navis.nblast(flipped_right_dotprop, left_dotprop)
                    if not nblast_scores_df.empty:
                        # すべてのスコアを取得する
                        for query_id in nblast_scores_df.index:
                            score = nblast_scores_df.loc[query_id].values[0]
                            scores.append({
                                'Right_Flipped_Neuron': right_file,
                                'Left_Neuron': left_file,
                                'Score': score
                            })
                else:
                    print(f"Skipping {left_file} due to insufficient size")
        # スコアのリストをDataFrameに変換
        all_scores_df = pd.DataFrame(scores)
        # CSVファイルの保存
        right_neuron_id = os.path.splitext(right_file)[0].split("_")[-1]
        csv_filename = f'nblast_scores_{right_neuron_id}.csv'
        all_scores_df.to_csv(csv_filename, index=False)
        print(f"NBLASTスコアが '{csv_filename}' に保存されました")

