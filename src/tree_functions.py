from shapely.geometry import LineString, box, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points
import numpy as np
from copy import copy
import geopandas as gpd

"""
Functions to derive tree- and plotwise metrics: length, diameter and volume
"""

def get_len(geom:Polygon) -> float:
    "Get the estimated length of a polygon (longest line of the minimum rotated rectangle)"
    mrr = geom.minimum_rotated_rectangle
    x, y = mrr.exterior.coords.xy
    edge_len = (Point(x[0], y[0]).distance(Point(x[1], y[1])), Point(x[1], y[1]).distance(Point(x[2], y[2])))
    return max(edge_len)

def get_rpoint_diam(geom:Polygon) -> float:
    """Approximate polygon diameter by extending a line that goes through the representative point 
    of a polygon and nearest point of the minimum rotated rectangle to go through the full polygon
    and finally intersecting it with original polygon
    """
    p1, p2 = nearest_points(geom.minimum_rotated_rectangle.exterior, geom.representative_point())
    minx, miny, maxx, maxy = geom.bounds
    line = LineString([p1,p2])
    bbox = box(*geom.bounds)
    a, b = line.boundary
    if a.x == b.x: # line is vertical
        extended_line = LineString([(a.x, miny), (a.x, maxy)])
    elif a.y == b.y: # line is horizontal
        extended_line = LineString([(minx, a.y), (maxx, a.y)])
    else: # solve y = k*x + m
        k = (b.y - a.y) / (b.x - a.x)
        m = a.y - k * a.x
        y0 = k * minx + m
        y1 = k * maxx + m
        x0 = (miny - m) / k
        x1 = (maxy - m) / k
        points_on_boundary_lines = [Point(minx, y0), Point(maxx, y1), 
                                    Point(x0, miny), Point(x1, maxy)]
        points_sorted_by_distance = sorted(points_on_boundary_lines, key=bbox.distance)
        extended_line = LineString(points_sorted_by_distance[:2])
    return extended_line.intersection(geom).length

def get_three_point_diams(geom:Polygon) -> float:
    """Approximate polygon diameter by creating three lines that intersect the polygon by """
    d = get_len(geom)
    mrr = geom.minimum_rotated_rectangle
    mrr = orient(mrr)
    mrr_x, mrr_y = mrr.exterior.coords.xy
    a_ix = list(mrr_y).index(min(mrr_y))
    b_ix = a_ix + 1 if a_ix < 3 else 0
    c_ix = b_ix + 1 if b_ix < 3 else 0
    d_ix = c_ix + 1 if c_ix < 3 else 0 
    ab = LineString([Point(mrr_x[a_ix], mrr_y[a_ix]), Point(mrr_x[b_ix], mrr_y[b_ix])])
    ad = LineString([Point(mrr_x[a_ix], mrr_y[a_ix]), Point(mrr_x[d_ix], mrr_y[d_ix])])
    if ab.length > ad.length:
        maxline = ab
        max_ort = LineString([Point(mrr_x[d_ix], mrr_y[d_ix]), Point(mrr_x[c_ix], mrr_y[c_ix])])
    else:
        maxline = ad
        max_ort = LineString([Point(mrr_x[b_ix], mrr_y[b_ix]), Point(mrr_x[c_ix], mrr_y[c_ix])]) 
    bot_a, bot_b = maxline.boundary
    top_a, top_b = max_ort.boundary
    if top_a.y == top_b.y: # horizontal
        line_10 = LineString([Point(min(top_a.x, top_b.x) + 0.10*d, top_a.y), 
                              Point(min(bot_a.x, bot_b.x) + 0.10*d, bot_a.y)])
        line_50 = LineString([Point(min(top_a.x, top_b.x) + 0.5*d, top_a.y), 
                              Point(min(bot_a.x, bot_b.x) + 0.5*d, bot_a.y)])
        line_90 = LineString([Point(max(top_a.x, top_b.x) - 0.10*d, top_b.y),
                              Point(max(bot_a.x, bot_b.x) - 0.10*d, bot_b.y)])
    elif top_a.x == top_b.x: # vertical
        line_10 = LineString([Point(top_a.x, min(top_a.y,  top_b.y) + 0.10*d), 
                              Point(bot_a.x, min(bot_a.y,  bot_b.y) + 0.10*d)])
        line_50 = LineString([Point(top_a.x, min(top_a.y,  top_b.y) + 0.5*d), 
                              Point(bot_a.x, min(bot_a.y,  bot_b.y) + 0.5*d)])
        line_90 = LineString([Point(top_b.x, max(top_a.y,  top_b.y) - 0.10*d), 
                              Point(bot_b.x, max(bot_a.y,  bot_b.y) - 0.10*d)])
    else: # we do geometry, solve <x,y> = <x_1,y_1> + t<1,m>
        k = (bot_b.y - bot_a.y) / (bot_b.x - bot_a.x)
        mul = 1 if k > 0 else -1
        top_x_10 = top_a.x + mul * np.sqrt(((0.10*d)**2)/(1+k**2))
        top_x_50 = top_a.x + mul * np.sqrt(((0.5*d)**2)/(1+k**2))
        top_x_90 = top_a.x + mul * np.sqrt(((0.90*d)**2)/(1+k**2))
        top_y_10 = top_a.y + np.sqrt(((0.10*d*k)**2)/(1+k**2))
        top_y_50 = top_a.y + np.sqrt(((0.5*d*k)**2)/(1+k**2))
        top_y_90 = top_a.y + np.sqrt(((0.90*d*k)**2)/(1+k**2))
        bot_x_10 = bot_a.x + mul * np.sqrt(((0.10*d)**2)/(1+k**2))
        bot_x_50 = bot_a.x + mul * np.sqrt(((0.5*d)**2)/(1+k**2))
        bot_x_90 = bot_a.x + mul * np.sqrt(((0.90*d)**2)/(1+k**2))
        bot_y_10 = bot_a.y + np.sqrt(((0.10*d*k)**2)/(1+k**2))
        bot_y_50 = bot_a.y + np.sqrt(((0.5*d*k)**2)/(1+k**2))
        bot_y_90 = bot_a.y + np.sqrt(((0.90*d*k)**2)/(1+k**2))
        line_10 = LineString([Point(top_x_10, top_y_10), Point(bot_x_10, bot_y_10)])
        line_50 = LineString([Point(top_x_50, top_y_50), Point(bot_x_50, bot_y_50)])
        line_90 = LineString([Point(top_x_90, top_y_90), Point(bot_x_90, bot_y_90)])
        
    return line_10.intersection(geom).length, line_50.intersection(geom).length, line_90.intersection(geom).length

def cut_cone_volume(geom:Polygon) -> float:
    """Estimate the volume for the polygon by assuming that it is constructed from two 
    truncated right circular truncated cones.
    """
    h = get_len(geom)/2
    d_10, d_50, d_90 = get_three_point_diams(geom)
    r_10 = d_10/2
    r_50 = d_50/2
    r_90 = d_90/2
    V_1 = (np.pi*h*(r_10**2 + r_10*r_50 + r_50**2))/3
    V_2 = (np.pi*h*(r_90**2 + r_90*r_50 + r_50**2))/3
    return V_1 + V_2

def get_len_in_plot(geom:Polygon, circles:gpd.GeoDataFrame):
    "Use the longest side of the minimum rotated rectangle around a polygon as the proxy for trunk length"
    matching_circle = circles[circles.intersects(geom)].iloc[0].geometry
    geom = copy(geom.intersection(matching_circle))
    mrr = geom.minimum_rotated_rectangle
    x, y = mrr.exterior.coords.xy
    edge_len = (Point(x[0], y[0]).distance(Point(x[1], y[1])), Point(x[1], y[1]).distance(Point(x[2], y[2])))
    return max(edge_len)