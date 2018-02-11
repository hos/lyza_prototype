from math import pi as pi_val
from pylyza.mesh import Mesh
from pylyza.cells import Quad, Line
import copy

def locate_midpoint(coor1, coor2, percent):
    return [
        coor1[0] + (coor2[0]-coor1[0])*percent,
        coor1[1] + (coor2[1]-coor1[1])*percent,
    ]

def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #Typo was here

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        # import ipdb; ipdb.set_trace()
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

class QuadMesh(Mesh):
    def __init__(self, resolution_x, resolution_y, p0, p1, p2, p3):
        self.res_x = resolution_x
        self.res_y = resolution_y

        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

        super().__init__()

    def construct_mesh(self):

        for y in range(self.res_y+1):
            for x in range(self.res_x+1):
                point_down = locate_midpoint(self.p0, self.p1, x/self.res_x)
                point_up = locate_midpoint(self.p3, self.p2, x/self.res_x)

                point_left = locate_midpoint(self.p0, self.p3, y/self.res_y)
                point_right = locate_midpoint(self.p1, self.p2, y/self.res_y)

                coor = line_intersection((point_left, point_right), (point_down, point_up))
                self.add_node(coor)

        for y in range(self.res_y):
            for x in range(self.res_x):
                n0 = self.nodes[y*(self.res_x+1) + x]
                n1 = self.nodes[y*(self.res_x+1) + x + 1]
                n2 = self.nodes[(y+1)*(self.res_x+1) + x + 1]
                n3 = self.nodes[(y+1)*(self.res_x+1) + x]
                self.add_cell(Quad([n0,n1,n2,n3]))

        for y in range(self.res_y):
            for x in range(self.res_x+1):
                n0 = self.nodes[y*(self.res_x+1) + x]
                n1 = self.nodes[(y+1)*(self.res_x+1) + x]
                self.add_boundary_cell(Line([n0,n1]))

        for y in range(self.res_y+1):
            for x in range(self.res_x):
                n0 = self.nodes[y*(self.res_x+1) + x]
                n1 = self.nodes[y*(self.res_x+1) + x + 1]
                self.add_boundary_cell(Line([n0,n1]))

