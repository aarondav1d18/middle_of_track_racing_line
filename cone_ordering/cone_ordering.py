import math
import heapq
import numpy as np
from typing import List, Tuple
from core import Cone, ConeArray

MAX_DISTANCE_BETWEEN_CONES = 10

# The _onSegment, _orientation, doIntersect are from the following link
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/

def _onSegment(cone1: Cone, cone2: Cone, cone3: Cone) -> bool: 
    """
    Determine if point2 lies on the line segment from point1 to point3.

    Args:
        cone1 (Cone): Starting point of the segment.
        cone2 (Cone): Point to check.
        cone3 (Cone): Ending point of the segment.

    Returns:
        bool: True if point2 is on the segment, False otherwise.
    """
    return ((cone2.position.x <= max(cone1.position.x, cone3.position.x)) and (cone2.position.x >= min(cone1.position.x, cone3.position.x)) and 
           (cone2.position.y <= max(cone1.position.y, cone3.position.y)) and (cone2.position.y >= min(cone1.position.y, cone3.position.y)))
  
def _orientation(start_point: Cone, mid_point: Cone, end_point: Cone) -> int:
    """Calculate the orientation of the triplet (start_point, mid_point, end_point).

    Args:
        start_point (Cone): First point in the triplet.
        mid_point (Cone): Second point in the triplet.
        end_point (Cone): Third point in the triplet.

    Returns:
        int: 0 if collinear, 1 if clockwise, 2 if counterclockwise.
    """
    val = ((mid_point.position.y - start_point.position.y) * (end_point.position.x - mid_point.position.x) -
           (mid_point.position.x - start_point.position.x) * (end_point.position.y - mid_point.position.y))
    if val > 0:
        return 1  # Clockwise
    elif val < 0:
        return 2  # Counterclockwise
    else:
        return 0  # Collinear
  
def doIntersect(cone1: Cone, cone2: Cone, cone3: Cone, cone4: Cone, tolerance: float = 1e-3) -> bool:
    """
    Check if two line segments (cone1 to cone2 and cone3 to cone4) intersect.

    Args:
        cone1, cone2 (Cone): Endpoints of the first line segment.
        cone3, cone4 (Cone): Endpoints of the second line segment.
        tolerance (float): Distance tolerance under which intersection is considered.

    Returns:
        bool: True if the segments intersect, False otherwise.
    """
    if euclidean_distance_between_cones(cone1, cone2) < tolerance or euclidean_distance_between_cones(cone3, cone4) < tolerance:
        return False

    # Find the four orientations needed for the general and special cases
    o1 = _orientation(cone1, cone2, cone3)
    o2 = _orientation(cone1, cone2, cone4)
    o3 = _orientation(cone3, cone4, cone1)
    o4 = _orientation(cone3, cone4, cone2)

    # General case
    if (o1 != o2 and o3 != o4):
        return True

    # Special Cases
    if (o1 == 0 and _onSegment(cone1, cone3, cone2)):
        return True
    if (o2 == 0 and _onSegment(cone1, cone4, cone2)):
        return True
    if (o3 == 0 and _onSegment(cone3, cone1, cone4)):
        return True
    if (o4 == 0 and _onSegment(cone3, cone2, cone4)):
        return True

    return False

def euclidean_distance_between_cones(cone1: Cone, cone2: Cone) -> float:
    return math.sqrt((cone1.position.x - cone2.position.x) ** 2 + (cone1.position.y - cone2.position.y) ** 2)

def compute_distance_matrix(cones: ConeArray) -> np.ndarray:
    position = np.array([(cone.position.x, cone.position.y) for cone in cones])
    return np.linalg.norm(position[:, np.newaxis, :] - position[np.newaxis, :, :], axis=-1)


def filter_valid_cones(cones: list, distance_matrix: np.ndarray) -> list:
    """
    Filter cones to find those within a certain distance from at least one other cone.

    Args:
        cones (ConeArray): List of cones to filter.
        distance_matrix (np.ndarray): Precomputed distances between cones.

    Returns:
        ConeArray: List of cones that are within the specified maximum distance.
    """
    max_distance = MAX_DISTANCE_BETWEEN_CONES
    return list(np.array(cones)[
            np.where(
                (distance_matrix < max_distance).any(axis=1)
            )
        ])



def compute_neighbouring_cones_matrix(cones: ConeArray, distance_matrix: np.ndarray) -> List[List[Tuple[int, float]]]:
    """
    Compute a matrix of neighboring cones for each cone based on a distance threshold.

    Args:
        cones (ConeArray): List of cones.
        distance_matrix (np.ndarray): Precomputed distance matrix for the cones.

    Returns:
        List[List[Tuple[int, float]]]: A matrix listing neighboring cones for each cone.
    """
    max_distance = MAX_DISTANCE_BETWEEN_CONES 
    neighbors = []
    for i, cone in enumerate(cones):
        nearby_cones_and_dists = sorted(
            filter(lambda cd: cd[1] <= max_distance, enumerate(distance_matrix[i])),
            key=lambda cd: cd[1]
        )
        neighbors.append(nearby_cones_and_dists)
    return neighbors


def would_cross_existing_path(tip: Cone, new_cone: Cone, path: ConeArray) -> bool:
    """
    Check if a new cone added to a path would cross any existing segment in the path.

    Args:
        tip (Cone): The last cone on the existing path.
        new_cone (Cone): The cone to be added.
        path (ConeArray): The existing path of cones.

    Returns:
        bool: True if adding the new cone would cross the path, False otherwise.
    """
    if len(path) < 2:  # No path to check if fewer than 2 points
        return False
    for cone1, cone2 in zip(path, path[1:]):
        if doIntersect(cone1, cone2, tip, new_cone, tolerance=8):
            return True
    return False


def compute_angle(coneA: Cone, coneB: Cone, coneC: Cone) -> float:
    """
    Compute the angle (in radians) between the vectors BA and BC.

    Args:
        a (Cone): The first cone.
        b (Cone): The middle cone.
        c (Cone): The third cone.

    Returns:
        float: The angle in radians.
    """
    # Vectors BA and BC
    ba_x, ba_y = coneA.position.x - coneB.position.x, coneA.position.y - coneB.position.y
    bc_x, bc_y = coneC.position.x - coneB.position.x, coneC.position.y - coneB.position.y

    # Lengths of BA and BC
    ba_len = math.sqrt(ba_x**2 + ba_y**2)
    bc_len = math.sqrt(bc_x**2 + bc_y**2)

    # Handle potential division by zero
    if ba_len == 0 or bc_len == 0:
        return 0  # Treat as invalid (angle of 0)

    # Dot product and angle between BA and BC
    dot_product = (ba_x * bc_x + ba_y * bc_y) / (ba_len * bc_len)
    dot_product = max(-1.0, min(1.0, dot_product))  # Clamp to avoid floating-point issues
    angle = math.acos(dot_product)
    return angle


def get_ordered_list_of_cones(cones: ConeArray, start_cone: Cone) -> ConeArray:
    """
    Orders a list of cones starting from the specified `start_cone`.

    Args:
        cones (List[Cone]): The list of cones to order.
        start_cone (Cone): The starting cone for this set of cones.

    Returns:
        List[Cone]: The ordered list of cones.
    """
    # Compute the distance matrix for all cones
    distance_matrix = compute_distance_matrix(cones)

    # Filter invalid cones based on distance criteria
    valid_cones = filter_valid_cones(cones, distance_matrix)

    visited = [start_cone]
    path = [start_cone]

    # Priority queue to explore neighbors
    neighbors = compute_neighbouring_cones_matrix(valid_cones, distance_matrix)
    priority_queue = []
    for neighbor_idx, dist in neighbors[valid_cones.index(start_cone)]:
        heapq.heappush(priority_queue, (dist, neighbor_idx, valid_cones[neighbor_idx]))

    # Process the priority queue
    while priority_queue:
        _, _, current_cone = heapq.heappop(priority_queue)
        if current_cone in visited:
            continue

        # Validate angle if path has at least two previous cones
        if len(path) >= 2:
            coneA, coneB = path[-2], path[-1]
            angle = compute_angle(coneA, coneB, current_cone)
            min_angle = math.radians(30)  
            if angle < min_angle:
                continue  # Skip cones that cause sharp turns

        # Validate and add cone
        if not would_cross_existing_path(path[-1], current_cone, path):
            path.append(current_cone)
            visited.append(current_cone)

            # Add current cone's neighbors to the queue
            for neighbor_idx, dist in neighbors[valid_cones.index(current_cone)]:
                neighbor_cone = valid_cones[neighbor_idx]
                if neighbor_cone not in visited:
                    heapq.heappush(priority_queue, (dist, neighbor_idx, neighbor_cone))

    # Ensure path loops back to the start if possible
    if len(path) > 1 and euclidean_distance_between_cones(path[-1], path[0]) < MAX_DISTANCE_BETWEEN_CONES:
        path.append(path[0])

    return path

def order_cones(cones: list, max_cones: int) -> list:
    '''
    This function will take in a list of cones and call the
    functions needed to sort the coens and then it will return them.
    '''
    start_cone = min(cones, key=lambda cone: euclidean_distance_between_cones(cone, ORIGIN))
    ordered_cones = get_ordered_list_of_cones(cones, start_cone)
    ordered_cones_array = ConeArray()
    ordered_cones_array.cones = ordered_cones[:max_cones]
    return ordered_cones_array


def order_blue_and_yellow_cones(blue_cones: ConeArray, yellow_cones: ConeArray, origin: Cone) -> Tuple[ConeArray, ConeArray]:
    """
    Orders blue and yellow cones into separate tracks, considering angle constraints.

    Args:
        blue_cones (List[Cone]): The list of blue cones.
        yellow_cones (List[Cone]): The list of yellow cones.

    Returns:
        Tuple[List[Cone], List[Cone]]: Ordered lists for blue and yellow cones.
    """
    # max_cones = GET_COMMON_CONFIG_INT("ugrdv_nurbs", "number_of_cones")
    global ORIGIN
    ORIGIN = origin
    ordered_blue = order_cones(blue_cones.cones, 400)
    ordered_yellow = order_cones(yellow_cones.cones, 400)
    
    
    return ordered_blue, ordered_yellow