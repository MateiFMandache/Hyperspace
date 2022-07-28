import math
import tkinter as tk
import numpy as np
from itertools import product


VIEW_HEIGHT = 600
VIEW_WIDTH = 800
VIEW_CENTRE_X = VIEW_WIDTH // 2
VIEW_CENTRE_Y = VIEW_HEIGHT // 2
UNIT_LENGTH = 70
START_DIMENSION = 3
MAX_DIMENSION = 7
MIN_DIMENSION = 2


def degrees_of_freedom(dimension):
    return (dimension * (dimension - 1)) // 2


MAX_DOF = degrees_of_freedom(MAX_DIMENSION)


def to_screen(pair):
    x, y = pair
    return VIEW_CENTRE_X + int(x * UNIT_LENGTH), VIEW_CENTRE_Y + int(y * UNIT_LENGTH)


def matrix(dimension, parameters):
    def angle():
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
        mat = matrix(self.dimension, parameters)
        surface.delete('all')
        for v1, v2 in self.edges:
            x1, y1 = to_screen(np.matmul(mat, v1)[:2])
            x2, y2 = to_screen(np.matmul(mat, v2)[:2])
            surface.create_line(x1, y1, x2, y2)


def cube_edges(dimension):
    edges = []
    for direction in range(dimension):
        for pre_vertex in product([-0.5, 0.5], repeat=dimension - 1):
            edges.append((np.array(pre_vertex[0:direction] + (-0.5,) + pre_vertex[direction:]),
                          np.array(pre_vertex[0:direction] + (0.5,) + pre_vertex[direction:])))
    return edges


def main():
    dimension = START_DIMENSION

    win = tk.Tk()
    view = tk.Canvas(win, width=VIEW_WIDTH, height=VIEW_HEIGHT)
    view.grid(row=1, column=0, columnspan=2)

    def update_shape(_):
        shape = Shape(dimension, cube_edges(dimension))
        shape.draw(view, [value.get() for value in values])

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

    def change_dimension(new_dimension):
        if MIN_DIMENSION <= new_dimension <= MAX_DIMENSION:
            nonlocal dimension
            dimension = new_dimension
            dimensions_label['text'] = f"{dimension} dimensions"
            show_sliders()
            update_shape(None)

    dimension_minus_button = tk.Button(settings_frame, text="-",
                                       command=lambda: change_dimension(dimension - 1))
    dimension_minus_button.grid(row=0, column=0, sticky=tk.E)
    dimension_plus_button = tk.Button(settings_frame, text="+",
                                      command=lambda: change_dimension(dimension + 1))
    dimension_plus_button.grid(row=0, column=2, sticky=tk.W)

    update_shape(None)
    win.mainloop()


if __name__ == "__main__":
    main()
