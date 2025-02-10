class ConeArray:
    def __init__(self, cones=None):
        self.cones = cones if cones else []

    def __repr__(self):
        return f"ConeArray(cones={self.cones})"

    def __eq__(self, other):
        return self.cones == other.cones