from typing import List
from cone_ordering.cone_ordering import order_blue_and_yellow_cones
from core import Cone, ConeArray

import numpy as np
import matplotlib.pyplot as plt
import csv
from NURBS import NURBS
import os

ORIGIN = Cone()

def read_cones(filename: str) -> ConeArray:
    '''
    This will read the csv files that store the data for cones
    and seperate them into a list of blue cones and yellow cones and returns
    them. It will also plot the orange coens as they are not needed but look
    kinda nice.

    Args:
        filename (str): The path to the file to access

    Returns:
        ConeArray: ConeArray of yellow and blue cones
    '''
    blue_cones = ConeArray()
    yellow_cones = ConeArray()
    with open(filename) as f:
        f = csv.reader(f)
        for line in f:
            match line[0]:
                case('blue'):
                    cone = Cone()
                    cone.position.x = float(line[1])
                    cone.position.y = float(line[2])
                    cone.colour = Cone.BLUE
                    blue_cones.cones.append(cone)
                case('yellow'):
                    cone = Cone()
                    cone.position.x = float(line[1])
                    cone.position.y = float(line[2])
                    cone.colour = Cone.YELLOW
                    yellow_cones.cones.append(cone)
                case('big_orange'):
                    # Just plotting orange as it looks nice but is not needed
                    x = float(line[1])
                    y = float(line[2])
                    plt.plot(x,y, 'o', c='orange')
                case('car_start'):
                    ORIGIN.position.x = float(line[1])
                    ORIGIN.position.y = float(line[2])
                case _:
                    continue

    return blue_cones, yellow_cones

def generate_middle_line(blue_cones: List[float], yellow_cones: List[float]) -> None:
    '''
    This will find cones pairs based on proximity and then calculate the mid point between
    that pair and plot a line connecting them. It will then convert the path to a PathVelocityRequest
    to allow it to be used in the NURBS function which i used from the ugrdv_splines node.

    Args:
        blue_cones (List[float]): Ordered list of blue cones
        yellow_cones (List[float]): Ordered list of yellow cones
    '''
    mid_points = []
    bi, yi = 0, 0

    # Plot cones
    plt.plot(np.array(blue_cones)[:, 0], np.array(blue_cones)[:, 1], 'bo', label='Blue Cones')
    plt.plot(np.array(yellow_cones)[:, 0], np.array(yellow_cones)[:, 1], 'yo', label='Yellow Cones')

    while bi < len(blue_cones) and yi < len(yellow_cones):
        blue_point = np.array(blue_cones[bi])
        yellow_point = np.array(yellow_cones[yi])

        # Calculate the midpoint and store
        midpoint = (blue_point + yellow_point) / 2
        mid_points.append(midpoint)

        # Plot line between the current blue and yellow cone
        plt.plot([blue_point[0], yellow_point[0]], [blue_point[1], yellow_point[1]], 'm-', alpha=0.5)

        # Decide which cone pair to consider next based on proximity
        if bi < len(blue_cones) - 1 and yi < len(yellow_cones) - 1:
            next_blue_point = np.array(blue_cones[bi + 1])
            next_yellow_point = np.array(yellow_cones[yi + 1])
            if np.linalg.norm(next_blue_point - yellow_point) < np.linalg.norm(next_yellow_point - blue_point):
                bi += 1
            else:
                yi += 1
        elif bi < len(blue_cones) - 1:
            bi += 1
        elif yi < len(yellow_cones) - 1:
            yi += 1
        else:
            break

    # This will generate a NURBS curve to smooth out
    # nurbs = NURBS()
    # mid_line = nurbs.generateNURBS(mid_points)

    path_x = []
    path_y = []
    for point in mid_points:
        path_x.append(point[0])
        path_y.append(point[1])


    # for point in mid_line.evalpts:
    #     path_x.append(point[0] / point[2])
    #     path_y.append(point[1] / point[2])
    plt.plot(path_x,path_y, '-', c='orange')

def main(filename: str) -> None:
    '''
    This pretty much takes the file and calls the realated functions to get lists
    of the cones and then order them. It will then order the cones and generate the middle line.
    And then plots
    '''
    plt.figure(figsize=(15, 10))
    ax = plt.gca()  # Get the current axes
    ax.set_facecolor("black")
    plt.grid(color = 'teal', linestyle = '-', linewidth = 0.5)
    blue_cones, yellow_cones = read_cones(filename)
    blue_cones, yellow_cones = order_blue_and_yellow_cones(blue_cones, yellow_cones, ORIGIN)
    blue_cones_list = []
    yellow_cones_list = []
    for point in blue_cones.cones:
        blue_cones_list.append([point.position.x, point.position.y])
    for point in yellow_cones.cones:
        yellow_cones_list.append([point.position.x, point.position.y])

    generate_middle_line(blue_cones_list, yellow_cones_list)
    num_graphs = len(os.listdir('graphs'))
    # plt.savefig(f'graphs/track{num_graphs}')
    plt.show()

if __name__ == '__main__':
    for track in os.listdir('tracks'):
        main(f'tracks/{track}')