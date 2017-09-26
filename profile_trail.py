from bokeh.plotting import figure, output_file, show
from bokeh.io import export_svgs
from bokeh.io import export_png
import random
import csv
import json
from math import ceil

import numpy as np


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def get_dist_elevations(elevation_csv):
    elevations = None
    with open(elevation_csv, 'r') as elev_file:
        reader = csv.DictReader(elev_file)
        elevations = [(row['dist'], row['elevation']) for row in reader]

    return elevations



def create_plot(name, elevations):
    # prepare some data
    ordered_elevations = sorted(elevations, key=lambda dist_elev: dist_elev[0])
    smoothing_number = ceil(len(elevations) * 0.015)
    x = [float(r[0]) for r in ordered_elevations]
    y = [float(r[1]) for r in ordered_elevations]
    x = x[smoothing_number - 1:]
    y_smoothed = list(moving_average(np.array(y), smoothing_number))
    y = y_smoothed

    x.insert(0, min(x))
    x.append(max(x))
    y_min = min(y)
    y.insert(0, y_min)
    y.append(y_min)
    # x.append(x[len(x) - 1])


    # output to static HTML file
    output_file("data/{}.html".format(name))

    # create a new plot with a title and axis labels
    p = figure(width=1600, height=600, title=name, x_axis_label='Trail Distance', y_axis_label='Elevation in Meters')
    p.toolbar_location = None
    p.ygrid.grid_line_dash = 'dashed'
    p.ygrid.minor_grid_line_color = '#cccccc'
    p.ygrid.minor_grid_line_alpha = 0.2
    p.ygrid.minor_grid_line_dash = 'dotdash'
    p.xgrid.grid_line_color = None
    # p.ygrid.grid_line_color = None
    p.background_fill_color = 'gray'
    p.border_fill_color = None
    # p.xaxis[0].formatter = NumeralTickFormatter(format="0.0%")
    # p.yaxis[0].formatter = NumeralTickFormatter(format="$0.00")

    # add a line renderer with legend and line thickness
    p.patch(x,
            y,
            fill_alpha=0.6,
            legend=None,
            line_width=3,
            color='#cccccc',
            line_color='#f2f2f2')
    # p.line([x[1], x[len(x) - 2]], [y[1], y[len(y) - 2]], line_width=3, line_color='yellow')
    export_png(p, filename='data/pngs/' + name + '.png')

    # p.output_backend = "svg"
    # export_svgs(p, filename='data/svgs/' + name + '.svg')


    # show the results
    # show(p)


def test_gradient():
    # prepare some data
    N = 10
    # x = np.random.random(size=N) * 100
    # y = np.random.random(size=N) * 100
    x = np.array([1,2,3,4,5,6,7,8,9,10])
    y = np.array([1,4,6,8,10,9,12,13,12,15])
    radii = np.random.random(size=N) * 1.5
    colors = [
        "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(50+2*x, 30+2*y)
    ]

    # output to static HTML file (with CDN resources)
    output_file("color_scatter.html", title="color_scatter.py example", mode="cdn")

    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select"

    # create a new plot with the tools above, and explicit ranges
    p = figure(tools=TOOLS, x_range=(0,100), y_range=(0,100))

    # add a circle renderer with vectorized colors and sizes
    p.circle(x, y, fill_color=colors, fill_alpha=0.6, line_color=None, radius=5)

    # show the results
    show(p)


if __name__ == '__main__':
    route_profiles = None
    json_path = 'data/csvs/elevation_profiles.json'
    with open(json_path, 'r') as json_file:
        route_profiles = json.load(json_file)
    # elevations = get_dist_elevations('data/Long_trail.csv')
    for route in route_profiles:
        create_plot(route, route_profiles[route])
    # test_gradient()
