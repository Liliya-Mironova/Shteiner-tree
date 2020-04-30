import operator
import os
import sys


class Point:
    def __init__(self, x, y, l, t):
        self.x = x
        self.y = y
        self.type = t
        self.layer = l

class Segment:
    def __init__(self, x1, y1, x2, y2, l):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.layer = l

class Grid:
    def __init__(self, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

###################################################
# builds one Minimum Steiner Tree for an array of
# points by Deikstra's algorithm
###################################################
def MST (P):
    N = len(P)
    M = N * (N - 1) / 2
    edges = []
    for i in range(N):
        for j in range(N):
            if (j > i):
                start = i
                end = j
                weight = abs(P[i].x - P[j].x) + abs(P[i].y - P[j].y)
                edges.append([weight, start, end])

    edges.sort()
    comp = [i for i in range(N)]
    min_weight = 0
    tree = []
    for weight, start, end in edges:
        if comp[start] != comp[end]:
            min_weight += weight
            tree.append([start, end])
            a = comp[start]
            b = comp[end]
            for i in range(N):
                if comp[i] == b:
                    comp[i] = a
    return min_weight, tree

###################################################
# builds MSTs for the tree without the new point 
# and with it and returns true if the weight of 
# the new is less (the new tree is better)
###################################################
def is_better_MST (A, B):
    weightA, treeA = MST(A)
    weigthB, treeB = MST(A + B)

    return weightA - weigthB

###################################################
# parses the original xml
# returns an array of points and an object Grid
###################################################
def parse_xml (filename):
    try:
        f = open(filename)
    except IOError as e:
        print(u'Invalid filename:', filename)
    else:
        with f:
            points = []
            for line in f:
                if line.strip()[1:5] == "grid":
                    min_x = int(line.split('min_x="')[1].split('"')[0])
                    max_x = int(line.split('max_x="')[1].split('"')[0])
                    min_y = int(line.split('min_y="')[1].split('"')[0])
                    max_y = int(line.split('max_y="')[1].split('"')[0])
                if line.strip()[1:6] == "point":
                    x = int(line.split('x="')[1].split('"')[0])
                    y = int(line.split('y="')[1].split('"')[0])
                    layer = line.split('layer="')[1].split('"')[0]
                    type_ = line.split('type="')[1].split('"')[0]
                    points.append(Point(x, y, layer, type_))
            return points, Grid(min_x, max_x, min_y, max_y)

###################################################
# returns an array of all possible pairs of x and y
# for the original points - (Shteiner's points)
###################################################
def fill_coords (points):
    vertical = []
    horizontal = []
    decart_mult = []

    for i in points:
        vertical.append(i.x)
        horizontal.append(i.y)

    vertical = set(vertical)
    horizontal = set(horizontal)

    for i in horizontal:
        for j in vertical:
            decart_mult.append({'x': j, 'y': i})

    return decart_mult

###################################################
# returns an array of all possible pairs of x and y
# for the original points - (Shteiner's points)
###################################################
def construct_a_tree (points, decart_mult):
    S = []
    T = [] 
    pts = points.copy()
    for i in decart_mult:
        pt = Point(i['x'], i['y'], 'pins', 'pin')
        if is_better_MST(pts, [pt]) > 0:
            T.append(pt)
    while len(T) != 0:
        max_xx = -1
        max_delta = 0
        for i in T:
            d = is_better_MST(pts, [i])
            if d > max_delta:
                max_delta = d
                max_xx = i
        if max_xx != -1:
            S.append(max_xx)
        for i in S:
            if i not in pts:
                pts.append(i)
        rem = []
        weight, tree = MST(pts)
        for i in S:
            d = 0
            for t in tree:
                if pts[t[0]] == i or pts[t[1]] == i:
                    d += 1
            if d < 3:
                rem.append(i)
        for i in rem:
            points.remove(i)
        T = [] 
        for i in decart_mult:
            x = []
            pt = Point(i['x'], i['y'], 'pins', 'pin')
            if is_better_MST(pts, [pt]) > 0:
                for k in x:
                    T.append(k)
        min_weight, tree = MST(pts)
    return pts, tree

###################################################
# returns sorted and brushed m2 and m3 layers
###################################################
def sort_and_exclude (m2, m3):
    m2_unique = []
    tmp = []
    m2s = []
    ans = []
    m2 = sorted(m2, key=operator.attrgetter('y1'))

    for i in m2:
        if i.y1 not in m2_unique:
            m2_unique.append(i.y1)
    k = 0
    for i in range(len(m2)):
        if (m2[i].y1 == m2_unique[k]):
            tmp.append(m2[i])
        elif (k < len(m2_unique)):
            m2s.append(tmp)
            tmp = []
            k += 1
            tmp.append(m2[i])
    m2s.append(tmp)

    tmp = []
    for i in range(len(m2s)):
        m2s[i] = sorted(m2s[i], key=operator.attrgetter('x1'))
        for j in range(len(m2s[i])):
            if (len(tmp) == 0):
                tmp.append(m2s[i][j])
            else:
                if (m2s[i][j].x1 > tmp[-1].x2):
                    tmp.append(m2s[i][j])
                else:
                    if m2s[i][j].x2 > tmp[-1].x2:
                        tmp[-1].x2 = m2s[i][j].x2
        for k in tmp:
            ans.append(k)
        tmp = []
    m2 = ans
#-----------------------------------------------------------
    m3_unique = []
    tmp = []
    m3s = []
    ans = []
    m3 = sorted(m3, key=operator.attrgetter('x1'))

    for i in m3:
        if i.y1 not in m3_unique:
            m3_unique.append(i.x1)
    k = 0
    for i in range(len(m3)):
        if (m3[i].x1 == m3_unique[k]):
            tmp.append(m3[i])
        elif (k < len(m3_unique)):
            m3s.append(tmp)
            tmp = []
            k += 1
            tmp.append(m3[i])
    m3s.append(tmp)
    tmp = []
    for i in range(len(m3s)):
        m3s[i] = sorted(m3s[i], key=operator.attrgetter('y1'))
        for j in range(len(m3s[i])):
            if len(tmp) == 0:
                tmp.append(m3s[i][j])
            else:
                if (m3s[i][j].y1 > tmp[-1].y2):
                    tmp.append(m3s[i][j])
                else:
                    if m3s[i][j].y2 > tmp[-1].y2:
                        tmp[-1].y2 = m3s[i][j].y2
        for k in tmp:
            ans.append(k)
        tmp = []
    m3 = ans
    return m2, m3

###################################################
# is invoked after the tree is built,
# compares the coordinates of segment ends and
# decides if it is horizontal (m2), vertical (m3)
# or transitional (m2_m3)
###################################################
def make_layers (P_S, tree):
    m2 = []
    m3 = []
    m2_m3 = []
    pins_m2 = []
    pins_m3 = []

    for i in range(len(points)):
        pins_m2.append(Point(points[i].x, points[i].y, "pins_m2", "via"))

    for i in range (len(tree)):
        p0 = P_S[tree[i][0]]
        p1 = P_S[tree[i][1]]
        if (p0.x != p1.x):
            if (p0.x < p1.x):
                m2.append(Segment(p0.x, p0.y, p1.x, p0.y, 'm2'))
            else:
                m2.append(Segment(p1.x, p0.y, p0.x, p0.y, 'm2'))
        if (p0.y != p1.y):
            if (p0.y < p1.y):
                m3.append(Segment(p1.x, p0.y, p1.x, p1.y, 'm3'))
            else:
                m3.append(Segment(p1.x, p1.y, p1.x, p0.y, 'm3'))
        if ((p0.x != p1.x) & (p0.y != p1.y)):
            pins_m3.append([p1.x, p0.y])

    for i in range(len(m3)):
        pins_m3.append([m3[i].x1, m3[i].y1])
        pins_m3.append([m3[i].x2, m3[i].y2])

    pins_m3_unique = []
    for i in pins_m3:
        if i not in pins_m3_unique:
            pins_m3_unique.append(i)
            m2_m3.append(Point(i[0], i[1], 'm2_m3', 'via'))
            m2.append(Segment(i[0], i[1], i[0], i[1], 'm2'))

    return m2, m3, m2_m3, pins_m2, pins_m3_unique

###################################################
# write the resulting tree with layers to the output
###################################################
def write_to_output (filename, pins, m2, m3, m2_m3, grid):
    f_out = open(filename.split('.xml')[0] + '_out.xml', "w")
    f_out.write("<root>\n")
    f_out.write("<grid min_x=\"%(min_x)s\"  max_x=\"%(max_x)s\" min_y=\"%(min_y)s\" max_y=\"%(max_y)s\"/>\n" % 
                {"min_x": grid.min_x, "max_x": grid.max_x, "min_y": grid.min_y, "max_y": grid.max_y})
    f_out.write("<net>\n")
    for i in range (len(pins)):
        f_out.write("<point x=\"%(x)s\" y=\"%(y)s\" layer=\"pins\" type=\"pin\"/>\n" % 
                    {"x": pins[i].x, "y": pins[i].y})
    for i in range (len(pins_m2)):
        f_out.write("<point x=\"%(x)s\" y=\"%(y)s\" layer=\"pins_m2\" type=\"via\"/>\n" % 
                    {"x": pins_m2[i].x, "y": pins_m2[i].y})
    for i in range (len(m2_m3)):
        f_out.write("<point x=\"%(x)s\" y=\"%(y)s\" layer=\"m2_m3\" type=\"via\"/>\n" % 
                    {"x": m2_m3[i].x, "y": m2_m3[i].y})
    for i in range (len(m2)): 
        f_out.write("<segment x1=\"%(x1)s\" y1=\"%(y1)s\" x2=\"%(x2)s\" y2=\"%(y2)s\" layer=\"m2\"/>\n" % 
                    {"x1": m2[i].x1, "y1": m2[i].y1, "x2": m2[i].x2, "y2": m2[i].y2})
    for i in range (len(m3)):
        f_out.write("<segment x1=\"%(x1)s\" y1=\"%(y1)s\" x2=\"%(x2)s\" y2=\"%(y2)s\" layer=\"m3\"/>\n" % 
                    {"x1": m3[i].x1, "y1": m3[i].y1, "x2": m3[i].x2, "y2": m3[i].y2})
    f_out.write("</net>\n")
    f_out.write("</root>\n")
    f_out.close()


if __name__ == "__main__":
    filename = sys.argv[1]
    points, grid = parse_xml (filename)
    decart_mult = fill_coords (points)
    pts, tree = construct_a_tree (points, decart_mult)
    m2, m3, m2_m3, pins_m2, pins_m3 = make_layers (pts, tree)
    m2, m3 = sort_and_exclude (m2, m3)
    write_to_output (filename, points, m2, m3, m2_m3, grid)