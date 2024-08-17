# Preparation
import numpy as np
import pandas as pd
from scipy.spatial import distance

from meshparty import trimesh_io, meshwork, mesh_filters
import navis
import pcg_skel
import pandas as pd

from fanc import auth

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

# Segment ID1 (segment ID of the main neuron on the right side)
segid = 648518346517156901

# Get the skeleton
skeleton = get_pcg_skeleton(segid)

# Flip the skeleton
flipped_skeleton = flip_skeleton_horizontally(skeleton)

# Optionally view the flipped skeleton with Spelunker
url = fanc.statebuilder.render_scene(annotations=flipped_skeleton.vertices, annotation_units='nm')
print(url)

# Save the file
save_swc(flipped_skeleton, 'flipped_skeleton.swc')

# —---------------Repeat the following steps to download 84 left-sided neurons—-----------------

# Segment ID2 (segment ID on the left side)
segid = 648518346475392180

# Get the skeleton
skeleton = get_pcg_skeleton(segid)

# Save the file
save_swc(skeleton, 'skeleton.swc')

#-------------------------------------------End the repetition—---------------------------------------------------

# Read the flipped right side neuron
flipped_right_neuron = navis.read_swc(r"C:\Your\Path\flipped_skeleton.swc"")
flipped_right_neuron.units = 'um'

# Convert neurons to Dotprop objects
flipped_right_dotprop = navis.make_dotprops(flipped_right_neuron)

 —---------------Repeat the following steps to download 84 left-sided neurons—-----------------

# Read the left side neuron
left_neuron1 = navis.read_swc(r"C:\Your\Path\skeleton.swc")
left_neuron1.units = 'um'

# Convert neurons to Dotprop objects
left_dotprop1 = navis.make_dotprops(left_neuron1)

# Make a list of Dotprop objects
dotprops = [flipped_right_dotprop, left_dotprop1]

# Do NBLAST comparison between flipped right side neuron and left side neuron
nblast_scores = navis.nblast_allbyall(dotprops)

# Print the Nblast comparison scores
print(nblast_scores)
#-------------------------------------------End the repetition—---------------------------------------------------

