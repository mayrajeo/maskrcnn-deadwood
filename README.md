# Deadwood detection from RGB UAV imagery using Mask R-CNN

## Table of contents

* [About](#about)
* [Getting started](#getting-started)
* [Data](#data)
* [Workflow](#workflow)
  * [EDA and data generation for models](#eda-and-data-generation-for-models)
  * [Comparing annotations with field data](#comparing-annotations-with-field-data)
  * [Model training](#model-training)
  * [Detection results](#detection-results)
  * [Comparing results with field data](#comparing-results-with-field-data)

* [Authors](#authors)

## About



## Getting started

Much of the work relies heavily on [https://github.com/jaeeolma/drone_detector](https://github.com/jaeeolma/drone_detector), and instructions for its installation work here also.

## Data

Examples are using UAV RGB Orthomosaics from either Hiidenportti, Kuhmo, Eastern-Finland or Sudenpesänkangas, Evo, Southern-Finland. Hiidenportti dataset has a spatial resolution of around 4cm, and Sudenpesänkangas dataset has a spatial resolution of 4.85cm. Hiidenportti data contains 9 different UAV mosaics, and Sudenpesänkangas data is one single orthomosaic. From these data, we created virtual plots to use as a training and validation data for the models. From Hiidenportti, we constructed 33 virtual plots of varying sizes in such way that all 9m circular field plots present in the area were covered, and each field plot center had at least 45 meter distance to the edge of the virtual plot. For Sudenpesänkangas, due to the area and orthomosaic being larger, we extracted 100x100m plots in such way that each virtual plot contains only one circular field plot. In total, Hiidenportti data contained 33 virtual plots that cover 71 field plots, and Sudenpesänkangas data contaied 71 virtual plots. 

Deadwood data that was used for training the models was manually annotated using QGIS software. We annotated all visible fallen deadwood trunks and standing deadwood canopies present in the virtual plots, and saved the results as `geojson` files. These data were then tiled and converted to COCO-format using functions from `drone_detector`. Sudenpesäkangas dataset consists of 5334 annotated deadwood instances, and Hiidenportti contains 8479 annotations. 

## Workflow

All steps of the workflow are described either in scripts or Jupyter notebooks.

### EDA and data generation for models

Presented in notebook [1_dataset_description_and_generation](notebooks/1_dataset_description_and_generation.ipynb)

### Comparing annotations with field data

Presented in notebook [2_comparing_annotations_and_field_data](notebooks/2_comparing_annotations_and_field_data.ipynb)

### Model training

Example of model training is presented in [3_mask_rcnn_model_training](notebooks/3_mask_rcnn_model_training.ipynb). All models were trained as a batch job instead of running the notebook.

### Detection results

The results are interpreted in two levels: patch level and virtual plot level. Patch level (512x512 pixel images) are show in [4_patch_level_results](notebooks/4_patch_level_results.ipynb), and virtual plot level results with and without post-processing are show in [5_virtual_plot_level_results](notebooks/5_virtual_plot_level_results.ipynb).


### Comparing results with field data



## Authors

* [Janne Mäyrä](github.com/jaeeolma), Finnish Environment Institute SYKE
* Topi Tanhuanpää, University of Eastern Finland
* 
