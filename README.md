# Deadwood detection from RGB UAV imagery using Mask R-CNN

<img src='repo_images/graph_abstract.png'>

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
  * [Using the models](#using-the-models)
* [Authors](#authors)

<a name="about"></a>
## About

Deadwood and decaying wood are the most important components for the biodiversity of boreal forests, and it has been estimated that around a quarter of all flora and fauna in Finnish forests depend on that. However, there is a severe lack of stand-level deadwood data in Finland, as the operational inventories either focus on the large-scale estimates or omit deadwood altogether. Unmanned Aerial Vehicles (UAVs) are the only method for remotely mapping small objects, such as fallen deadwood, as even the most spatially accurate commercial satellites provide 30cm ground sampling distance, compared to less than 5 cm that is easily achievable with UAVs.

In this work, we utilized Mask R-CNN to detect individual standing and fallen deadwood instances from RGB UAV imagery. We manually annotated over 14 000 deadwood instances from two separate study sites to use as the training and validation data, and also compared these data to field-measured deadwood data. Our models achieved test set Average Precision (AP) of 0.284 for the same geographical area the models were trained on, and AP of 0.220 for geographically distinct area used only for testing.

In addition to instance-level deadwood maps, we also estimated stand-level characteristics for the numbers of deadwood. In addition, we estimated the approximate total volume of fallen deadwood based on the annotated polygons. These stand-level features clearly show the borders of the conserved forest, and the volume estimations are able to distinguish between naturally formed deadwood hotspot and areas with logging remnants. The proposed method enables deadwood mapping for larger areas, complementing the traditional field work.

<a name="getting-started"></a>
## Getting started

Much of the work relies heavily on [https://github.com/jaeeolma/drone_detector](https://github.com/jaeeolma/drone_detector), and instructions for its installation work here also.

<a name="data"></a>
## Data

Examples are using UAV RGB Orthomosaics from either Hiidenportti, Kuhmo, Eastern-Finland or Sudenpesänkangas, Evo, Southern-Finland. Hiidenportti dataset has a spatial resolution of around 4cm, and Sudenpesänkangas dataset has a spatial resolution of 4.85cm. Hiidenportti data contains 9 different UAV mosaics, and Sudenpesänkangas data is one single orthomosaic. From these data, we created virtual plots to use as a training and validation data for the models. From Hiidenportti, we constructed 33 virtual plots of varying sizes in such way that all 9m circular field plots present in the area were covered, and each field plot center had at least 45 meter distance to the edge of the virtual plot. For Sudenpesänkangas, due to the area and orthomosaic being larger, we extracted 100x100m plots in such way that each virtual plot contains only one circular field plot. In total, Hiidenportti data contained 33 virtual plots that cover 71 field plots, and Sudenpesänkangas data contaied 71 virtual plots. 

Deadwood data that was used for training the models was manually annotated using QGIS software. We annotated all visible fallen deadwood trunks and standing deadwood canopies present in the virtual plots, and saved the results as `geojson` files. These data were then tiled and converted to COCO-format using functions from `drone_detector`. Sudenpesäkangas dataset consists of 5334 annotated deadwood instances, and Hiidenportti contains 8479 annotations.

<a name="workflow"></a>
## Workflow

All steps of the workflow are described either in scripts or Jupyter notebooks.

<a name="eda-and-data-generation-for-models"></a>
### EDA and data generation for models

Presented in notebook [1_dataset_description_and_generation](notebooks/1_dataset_description_and_generation.ipynb)

<a name="comparing-annotations-with-field-data"></a>
### Comparing annotations with field data

Presented in notebook [2_comparing_annotations_and_field_data](notebooks/2_comparing_annotations_and_field_data.ipynb)
<a name="model-training"></a>
### Model training

Example of model training is presented in [3_mask_rcnn_model_training](notebooks/3_mask_rcnn_model_training.ipynb). All models were trained as a batch job instead of running the notebook.

<a name="detection-results"></a>
### Detection results

The results were interpreted in two levels: patch level and virtual plot level. Patch level (512x512 pixel images) are show in [4_patch_level_results](notebooks/4_patch_level_results.ipynb), and virtual plot level results with and without post-processing are show in [5_virtual_plot_level_results](notebooks/5_virtual_plot_level_results.ipynb).

<a name="evaluation-with-plot-level-metrics"></a>
### Evaluation with plot-level metrics

In addition to object detection metrics, the results were also compared based on forest charasteristics, such as estimated total volume of fallen deadwood, the distributions for length and DBH estimations and such. These are shown in [6_result_comparison_with_field_data](notebooks/6_result_comparison_with_field_data.ipynb).

<a name="deriving-stand-level-characteristics"></a>
### Deriving stand-level characteristics

Finally, we used our models to derive stand-level characteristics for deadwood: number of deadwood per hectare, number of standing deadwood per hectare, number of fallen deadwood per hectare and estimated volume of fallen deadwood per hectare, as show in [7_deriving_standwise_metrics_for_evo](notebooks/7_deriving_standwise_metrics_for_evo.ipynb).

<a name="using-the-models"></a>
## Using the models

Model configs and weights are available [here](https://huggingface.co/mayrajeo/maskrcnn-deadwood). Note that configs for `WEIGHTS` and `OUTPUT_DIR` need to be changed according to your needs. Example app running R101 backbone without TTA for image patches can be found [here](https://huggingface.co/spaces/mayrajeo/maskrcnn-deadwood). More information is shown in [8_configs](notebooks/8_configs.ipynb).

<a name="authors"></a>
## Authors

* [Janne Mäyrä](github.com/jaeeolma), Finnish Environment Institute SYKE
* Topi Tanhuanpää, University of Eastern Finland
* Anton Kuzmin, University of Eastern Finland
* Timo Kumpula, University of Eastern Finland
* Petteri Vihervaara, Finnish Environment Institute SYKE

This work is as a part of [IBC-CARBON](https://ibccarbon.fi/en-US) WP4.
