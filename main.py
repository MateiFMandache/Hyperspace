import math
import tkinter as tk
import numpy as np
import enum
from math import sqrt
from itertools import product, combinations
from random import random


VIEW_HEIGHT = 600
VIEW_WIDTH = 800
VIEW_CENTRE_X = VIEW_WIDTH // 2
VIEW_CENTRE_Y = VIEW_HEIGHT // 2
UNIT_LENGTH = 150
START_DIMENSION = 3
MAX_DIMENSION = 7
MIN_DIMENSION = 2


def degrees_of_freedom(dimension):
    """Number of independent 'axes' about which we can rotate"""
    return (dimension * (dimension - 1)) // 2


MAX_DOF = degrees_of_freedom(MAX_DIMENSION)
RANDOM_OFFSETS = [random() for _ in range(MAX_DOF)]


class Form(enum.Enum):
    CUBE = "Cube"
    CROSS = "Cross"
    SIMPLEX = "Simplex"


def to_screen(pair):
    """Converts a pair of cartesian coordinates to screen
    coordinates"""
    x, y = pair
    return VIEW_CENTRE_X + int(x * UNIT_LENGTH), VIEW_CENTRE_Y + int(y * UNIT_LENGTH)


def matrix(dimension, parameters):
    """Creates the orthogonal matrix corresponding to the rotations
    given by the parameters"""
    def angle():
        """Generator for angles used"""
        for parameter in parameters:
            yield parameter * 2 * math.pi
    angle_generator = angle()

    result = np.identity(dimension)
    for pas in range(1, dimension):
        for dim in range(pas, 0, -1):
            multiplier = np.identity(dimension)
            next_angle = next(angle_generator)
            multiplier[dim-1][dim-1] = math.cos(next_angle)
            multiplier[dim][dim-1] = math.sin(next_angle)
            multiplier[dim-1][dim] = -math.sin(next_angle)
            multiplier[dim][dim] = math.cos(next_angle)
            result = np.matmul(multiplier, result)

    return result


class Shape:
    def __init__(self, dimension, edges):
        self.dimension = dimension
        self.edges = edges

    def draw(self, surface, parameters):
        """Displays the shape on the given surface"""
        mat = matrix(self.dimension, parameters)
        surface.delete('all')
        for v1, v2 in self.edges:
            x1, y1 = to_screen(np.matmul(mat, v1)[:2])
            x2, y2 = to_screen(np.matmul(mat, v2)[:2])
            surface.create_line(x1, y1, x2, y2)

    @classmethod
    def make(cls, dimension, form):
        """Alternative constructor: specify form rather than edges"""
        if form == Form.CUBE:
            return cls(dimension, cube_edges(dimension))
        if form == Form.CROSS:
            return cls(dimension, cross_edges(dimension))
        if form == Form.SIMPLEX:
            return cls(dimension, simplex_edges(dimension))


def cube_edges(dimension):
    """Generates the edges for the cube of the given dimension"""
    edges = []
    for direction in range(dimension):
        for pre_vertex in product([-0.5, 0.5], repeat=dimension - 1):
            edges.append((np.array(pre_vertex[0:direction] + (-0.5,) + pre_vertex[direction:]),
                          np.array(pre_vertex[0:direction] + (0.5,) + pre_vertex[direction:])))
    return edges


def cross_edges(dimension):
    """Generates the edges for the cross of the given dimension"""
    pre_vertices = np.identity(dimension)
    vertices_plus = [pre_vertices[i] for i in range(dimension)]
    vertices_minus = [-pre_vertices[i] for i in range(dimension)]
    vertices = vertices_plus + vertices_minus
    edges = filter(lambda edge: any(-edge[0] != edge[1]), combinations(vertices, 2))
    return list(edges)


def simplex_edges(dimension):
    """Generates the edges for the simplex of the given dimension"""
    vertex = [1] + [0] * (dimension - 1)
    vertices = [np.array(vertex)]
    sum_of_squares = 0
    for i in range(dimension):
        vertex[i] = - vertex[i] / (dimension - i)
        sum_of_squares += vertex[i] ** 2
        if i+1 < dimension:
            vertex[i+1] = sqrt(1-sum_of_squares)
        vertices.append(np.array(vertex))
    return list(combinations(vertices, 2))


def main():
    dimension = START_DIMENSION
    form = Form.CUBE
    shape = Shape.make(dimension, form)

    win = tk.Tk()
    view = tk.Canvas(win, width=VIEW_WIDTH, height=VIEW_HEIGHT)
    view.grid(row=1, column=0, columnspan=2)

    def update_shape(_):
        shape.draw(view, [value.get() + offset for value, offset in zip(values, RANDOM_OFFSETS)])

    slider_frame = tk.Frame(win)
    slider_frame.grid(row=0, column=1)
    values = [tk.DoubleVar() for _ in range(MAX_DOF)]
    sliders = [tk.Scale(slider_frame, from_=0.0, to=1.0, resolution=0.01, showvalue=False,
                        variable=values[i], command=update_shape) for i in range(MAX_DOF)]

    def show_sliders():
        for i, slider in enumerate(sliders):
            if i < degrees_of_freedom(dimension):
                slider.pack(side=tk.LEFT)
            else:
                slider.pack_forget()
    show_sliders()

    settings_frame = tk.Frame(win)
    settings_frame.grid(row=0, column=0)
    dimensions_label = tk.Label(settings_frame, text=f"{dimension} dimensions")
    dimensions_label.grid(row=0, column=1)
    shape_choice = tk.Frame(settings_frame)
    shape_choice.grid(row=1, column=0, columnspan=2)

    def change_dimension(new_dimension):
        if MIN_DIMENSION <= new_dimension <= MAX_DIMENSION:
            nonlocal dimension, shape
            dimension = new_dimension
            dimensions_label['text'] = f"{dimension} dimensions"
            show_sliders()
            shape = Shape.make(dimension, form)
            update_shape(None)

    def change_form(new_form):
        nonlocal form, shape
        form = new_form
        shape = Shape.make(dimension, form)
        update_shape(None)

    dimension_minus_button = tk.Button(settings_frame, text="-",
                                       command=lambda: change_dimension(dimension - 1))
    dimension_minus_button.grid(row=0, column=0, sticky=tk.E)
    dimension_plus_button = tk.Button(settings_frame, text="+",
                                      command=lambda: change_dimension(dimension + 1))
    dimension_plus_button.grid(row=0, column=2, sticky=tk.W)

    form_var = tk.StringVar(shape_choice, "Cube")
    tk.Radiobutton(shape_choice, text="Cube", variable=form_var, value="Cube",
                   command=lambda: change_form(Form.CUBE)).pack()
    tk.Radiobutton(shape_choice, text="Cross", variable=form_var, value="Cross",
                   command=lambda: change_form(Form.CROSS)).pack()
    tk.Radiobutton(shape_choice, text="Simplex", variable=form_var, value="Simplex",
                   command=lambda: change_form(Form.SIMPLEX)).pack()

    update_shape(None)
    win.mainloop()


if __name__ == "__main__":
    main()
