from geomdl import BSpline, convert, knotvector
import math
class NURBS():
	def __init__(self, degree = 3.0, max_lookahead_distance = 10):
		self.DEGREE = degree
		self.MAX_LOOKAHEAD_DISTANCE = max_lookahead_distance

	def generateNURBS(self, path: list) -> BSpline.Curve:
		'''
		This will take the middle line generate from ugrdv_path_planning and will generate the NURBS based on that.
		The weight is generated for each point and then NURBS is generated using the geomdl libary

		:param: goalPoints: PathVelocity of the middle line generated from ugrdv_path_planning
		:param: crv_rat: The generated NURBS
		'''
		control_points = []
		crv = BSpline.Curve()

		for point in path:
			# using a exponetial decay multiplier for weight
			dist = math.hypot(point[0], point[1])
			weight = math.exp(-(dist / self.MAX_LOOKAHEAD_DISTANCE))
			weighted_point = [point[0] * weight, point[1] * weight, weight]
			control_points.append(weighted_point)
		
		crv.degree = self.DEGREE
		crv.ctrlpts = control_points
		knotvectors = knotvector.generate(crv.degree, len(control_points))
		crv.knotvector = knotvectors
		crv_rat = convert.bspline_to_nurbs(crv)
		return crv_rat