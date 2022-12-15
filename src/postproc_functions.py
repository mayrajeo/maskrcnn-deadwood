import geopandas as gpd
import rasterio as rio
import itertools
from shapely.geometry import Polygon
import numpy as np
import pandas as pd
from shapely.ops import unary_union
from drone_detector.utils import fix_multipolys
from tqdm import tqdm

def make_grid(path, gridsize_x:int=640, gridsize_y:int=480, 
              overlap=(100,100)) -> gpd.GeoDataFrame:
    """
    Creates a grid template with `gridsize_x` times `gridsize_y` cells, with `overlap` pixels of overlap based on geotiff file in `path`. Returns a gpd.GeoDataFrame with `RyyCxx` identifier for each geometry BUGGED and replaced with rio_windows in tile_raster
    """
    with rio.open(path) as src:
        tfm = src.transform
        x_size = src.width
        y_size = src.height
    xres = tfm[0]
    ulx = tfm[2]
    yres = tfm[4]
    uly = tfm[5]
    lrx = ulx + (x_size * xres)
    lry = uly + (y_size * yres)
    # number of output cells is calculated like conv output
    ncols = int(np.ceil((np.ceil((lrx - ulx) / xres)) - gridsize_x) / (gridsize_x - overlap[0]) + 1)
    nrows = int(np.ceil((np.ceil((lry - uly) / yres)) - gridsize_y) / (gridsize_y - overlap[1]) + 1)
    polys = []
    names = []
    for col, row in (itertools.product(range(ncols), range(nrows))):
        ytop = lry - row * (yres * (gridsize_y - overlap[1]))
        ybot = ytop - (yres * gridsize_y)
        xleft = ulx + col * (xres * (gridsize_x - overlap[0]))
        xright = xleft + (xres * gridsize_x)
        polys.append(Polygon([(xleft,ytop), (xright,ytop), (xright,ybot), (xleft,ybot)]))
        names.append(f'R{row}C{col}')
    grid = gpd.GeoDataFrame({'cell': names, 'geometry':polys})
    
    with rio.open(path) as src:
        crs = src.crs
    grid.crs = crs
    
    return grid


def intersection_over_area(poly_1:Polygon, poly_2:Polygon) -> float:
    "Proportion of the overlap of poly_1 and poly_2 of the area of poly_1"
    area_intersection = poly_1.intersection(poly_2).area
    return area_intersection / poly_1.area

def merge_polys(gdf:gpd.GeoDataFrame, area_threshold:float=0.2) -> gpd.GeoDataFrame:
    """For each polygon, do the following:
    1. Check whether the ratio of the area of the intersection with any other polygon 
       and the area of the polygon is larger than area_threshold
    2. If not, add poly to the list `polys_to_keep`
    3. If yes, add the polygon and all sufficiently overlapping polygons to a dict where
       key is the polygon and values are all the sufficiently overlapping polygons
    4. Process each key-val -pair to a list of polygons to merge
    5. For each list to merge, set the prediction confidence to the mean of merged polygons, 
       label to the most common label (though usually the merging is done label-wise) and merge them.
    6. Drop duplicate geometries that for some reason exist.
    
    """
    polys_to_merge = {}
    polys_to_keep = []
    gdf = gdf.copy()
    gdf.reset_index(drop=True, inplace=True)
    for ann in tqdm(gdf.itertuples()):
        overlaps = gdf[gdf.geometry.intersects(ann.geometry)].copy()
        if len(overlaps) == 1: 
            polys_to_keep.append(ann.Index)
            continue
        overlaps = overlaps[overlaps.index != ann.Index]
        overlaps['pcts'] = overlaps.apply(lambda row: intersection_over_area(ann.geometry, row.geometry), axis=1)
        to_merge = overlaps[overlaps.pcts > area_threshold] # merge if intersection over area is larger than threshold
        if len(to_merge) > 0:
            polys_to_merge[ann.Index] = [i for i in to_merge.index]
        else:
            polys_to_keep.append(ann.Index)
            
    merge_pairs = []
    for key, val in polys_to_merge.items():
        other_vals = ([polys_to_merge[k] for k in val if k in polys_to_merge.keys()])
        other_vals = [i for s in other_vals for i in s]
        merge_vals = [val]
        merge_vals.append(list(set([key] + other_vals)))
        merge_vals = sorted([v for s in merge_vals for v in s])
        merge_pairs.append(tuple(merge_vals))
        
    new_polys = {'label': [], 'score': [], 'geometry': []}
    for ixs in list(set(merge_pairs)):
        tempdf = gdf.iloc[list(ixs)]
        label = tempdf.label.mode()[0]
        scores = tempdf.score.unique()
        avg_score = np.mean(scores)
        geoms = tempdf.geometry
        new_polys['label'].append(label)
        new_polys['score'].append(avg_score)
        new_polys['geometry'].append(unary_union(geoms))
    final_gdf = pd.concat([gdf.iloc[polys_to_keep], gpd.GeoDataFrame(new_polys, crs=gdf.crs)])
    final_gdf['geometry'] = final_gdf.apply(lambda row: fix_multipolys(row.geometry) 
                                            if row.geometry.type == 'MultiPolygon' 
                                            else Polygon(row.geometry.exterior), axis=1)
    final_gdf.drop_duplicates(subset=['geometry'], inplace=True)
    return final_gdf
