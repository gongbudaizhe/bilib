from fractions import Fraction


def rectangle_dot_count(vertices):
    """ Count rectangle dot count include edge """
    assert len(vertices) == 2
    width = abs(vertices[0][0] - vertices[1][0])
    height = abs(vertices[0][1] - vertices[1][1])
    dot_count = (width + 1) * (height + 1)
    return dot_count


def diagonal_dot_count(vertices):
    assert len(vertices) == 2
    width = abs(vertices[0][0] - vertices[1][0])
    height = abs(vertices[0][1] - vertices[1][1])

    assert width > 0 and height > 0

    slope = Fraction(height, width)
    dot_count = width / slope.denominator + 1
    return dot_count


def right_triangle_dot_count(vertices):
    """ count right triangle dot count include edge """
    diagonal_point = None
    for i in xrange(len(vertices)):
        v_1 = vertices[i]
        v_2 = vertices[(i + 1)% len(vertices)]
        if v_1[0] - v_2[0] != 0 and v_1[1] - v_2[1] != 0:
            diagonal_point = [v_1, v_2]
            break
    rect_count = rectangle_dot_count(diagonal_point)
    diagonal_count = diagonal_dot_count(diagonal_point)

    dot_count = (rect_count - diagonal_count) / 2 + diagonal_count
    return dot_count


def get_surrounding_rectangle(vertices):
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    x_min = min(xs)
    x_max = max(xs)
    y_min = min(ys)
    y_max = max(ys)
    return x_min, x_max, y_min, y_max


def two_diagonal_down_right_triangle_dot_count(rect_coord, rect_point,
                                               diagonal_point, general_point):
    large_triangle_dots = \
        right_triangle_dot_count(diagonal_point + [rect_point[2]])
    intersect_point_1 = [general_point[0][0], rect_coord[2]]
    intersect_point_2 = [rect_coord[1], general_point[0][1]]
    small_triangle_dots_1 = \
        right_triangle_dot_count([rect_point[0], general_point[0],
                                  intersect_point_1])
    small_triangle_dots_2 = \
        right_triangle_dot_count([rect_point[3], general_point[0],
                                  intersect_point_2])
    rectangle_dots = rectangle_dot_count([[general_point[0][0]+1,
                                           general_point[0][1]-1],
                                          rect_point[2]])
    diagonal_line_dots = diagonal_dot_count(diagonal_point)
    triangle_dots = large_triangle_dots - small_triangle_dots_1 - \
                    small_triangle_dots_2 - rectangle_dots - \
                    diagonal_line_dots + 3
    return triangle_dots


def two_diagonal_vertical_or_horizontal_dot_count(rect_coord,
                                                  rect_point,
                                                  diagonal_point,
                                                  general_point):
    large_rectangle_dots = right_triangle_dot_count(rect_point[::3])
    if rect_coord[0] == general_point[0][0] or \
                    rect_coord[1] == general_point[0][0]:
        small_triangle_dots_1 = \
            right_triangle_dot_count([rect_point[1],
                                      rect_point[3], general_point[0]])
        small_triangle_dots_2 = \
            right_triangle_dot_count([rect_point[0],
                                      rect_point[2], general_point[0]])
        vertical_line_dots = rect_coord[3] - rect_coord[2] + 1
        triangle_dots = large_rectangle_dots - small_triangle_dots_1 - \
                        small_triangle_dots_2 - vertical_line_dots + 3
    else:
        small_triangle_dots_1 = \
            right_triangle_dot_count([rect_point[0],
                                      rect_point[1], general_point[0]])
        small_triangle_dots_2 = \
            right_triangle_dot_count([rect_point[2],
                                      rect_point[3], general_point[0]])
        horizontal_line_dots = rect_coord[1] - rect_coord[0] + 1
        triangle_dots = large_rectangle_dots - small_triangle_dots_1 - \
                        small_triangle_dots_2 - horizontal_line_dots + 3
    return triangle_dots


def two_diagonal_touch_edge_down_right_triangle_dot_count(rect_coord,
                                                          rect_point,
                                                          diagonal_point,
                                                          general_point):
    large_triangle_dots = right_triangle_dot_count(diagonal_point +
                                                   [rect_point[2]])
    small_triangle_dots = right_triangle_dot_count([general_point[0],
                                                    rect_point[2],
                                                    rect_point[3]])
    line_dots_1 = general_point[0][0] - rect_coord[0] + 1
    line_dots_2 = diagonal_dot_count(diagonal_point)
    triangle_dots = large_triangle_dots - small_triangle_dots - \
                    line_dots_1 - line_dots_2 + 3
    return triangle_dots


def two_diagonal_touch_edge_up_right_triangle_dot_count(rect_coord,
                                                        rect_point,
                                                        diagonal_point,
                                                        general_point):
    large_triangle_dots = right_triangle_dot_count(diagonal_point +
                                                   [rect_point[2]])
    small_triangle_dots = right_triangle_dot_count([general_point[0],
                                                    rect_point[0],
                                                    rect_point[2]])
    line_dots_1 = rect_coord[3] - general_point[0][1] + 1
    line_dots_2 = diagonal_dot_count(diagonal_point)
    triangle_dots = large_triangle_dots - small_triangle_dots - \
                    line_dots_1 - line_dots_2 + 3
    return triangle_dots


def one_diagonal_down_left_triangle_dot_count(rect_coord, rect_point,
                                              diagonal_point, general_point):
    general_point = sorted(general_point, cmp=lambda x,y: x[0] - y[0])
    large_rectangle_dots = rectangle_dot_count(rect_point[::3])
    small_triangle_dots_1 = right_triangle_dot_count([rect_point[0],
                                                      rect_point[1],
                                                      general_point[0]])
    small_triangle_dots_2 = right_triangle_dot_count([rect_point[0],
                                                      rect_point[2],
                                                      general_point[1]])
    small_triangle_dots_3 = right_triangle_dot_count([general_point[0],
                                                      general_point[1],
                                                      rect_point[3]])
    triangle_dots = large_rectangle_dots - small_triangle_dots_1 - \
                    small_triangle_dots_2 - small_triangle_dots_3 + 3
    return triangle_dots


def answer(vertices):
    # classify triangle types according to the rectangle surrounding
    # the triangle
    rect_coord = get_surrounding_rectangle(vertices)
    rect_point = [[rect_coord[0], rect_coord[2]],  # down-left
                  [rect_coord[0], rect_coord[3]],  # up-left
                  [rect_coord[1], rect_coord[2]],  # down-right
                  [rect_coord[1], rect_coord[3]],  # up-right
                  ]
    x_sum = rect_coord[0] + rect_coord[1]
    y_sum = rect_coord[2] + rect_coord[3]

    diagonal_point = []
    general_point = []
    for v in vertices:
        if v[0] in rect_coord and v[1] in rect_coord:
            diagonal_point.append(v)
        else:
            general_point.append(v)

    if len(diagonal_point) == 1:
        if rect_point[0] in vertices:
            dot_num = one_diagonal_down_left_triangle_dot_count(
                rect_coord, rect_point, diagonal_point, general_point)
        elif rect_point[1] in vertices:
            for p in general_point:
                p[1] = y_sum - p[1]
            diagonal_point[0][1] = y_sum - diagonal_point[0][1]
            dot_num = one_diagonal_down_left_triangle_dot_count(
                rect_coord, rect_point, diagonal_point, general_point)
        elif rect_point[2] in vertices:
            for p in general_point:
                p[0] = x_sum - p[0]
            diagonal_point[0][0] = x_sum - diagonal_point[0][0]
            dot_num = one_diagonal_down_left_triangle_dot_count(
                rect_coord, rect_point, diagonal_point, general_point)
        elif rect_point[3] in vertices:
            for p in general_point:
                p[0] = x_sum - p[0]
                p[1] = y_sum - p[1]
            diagonal_point[0][0] = x_sum - diagonal_point[0][0]
            diagonal_point[0][1] = y_sum - diagonal_point[0][1]
            dot_num = one_diagonal_down_left_triangle_dot_count(
                rect_coord, rect_point, diagonal_point, general_point)
        else:
            raise Exception('Something went wrong!')
    elif len(diagonal_point) == 2:
        if diagonal_point[0][0] - diagonal_point[1][0] == 0 or \
            diagonal_point[0][1] - diagonal_point[1][1] == 0:
            dot_num = two_diagonal_vertical_or_horizontal_dot_count(
                rect_coord, rect_point, diagonal_point, general_point)
        elif general_point[0][0] not in rect_coord and \
             general_point[0][1] not in rect_coord:
            # Two diagonal point triangle case
            y_line = Fraction(diagonal_point[0][1] - diagonal_point[1][1],
                     diagonal_point[0][0] - diagonal_point[1][0]) * \
                    (general_point[0][0] - diagonal_point[0][0]) + \
                    diagonal_point[0][1]
            y_general = general_point[0][1]

            diagonal_point = [rect_point[0], rect_point[3]]
            if y_general > y_line:
                # general point is above the diagonal line
                if rect_point[1] not in vertices:
                    general_point[0][0] = x_sum - general_point[0][0]
                    general_point[0][1] = y_sum - general_point[0][1]
                    dot_num = two_diagonal_down_right_triangle_dot_count(
                        rect_coord, rect_point, diagonal_point, general_point)
                else:
                    general_point[0][1] = y_sum - general_point[0][1]
                    dot_num = two_diagonal_down_right_triangle_dot_count(
                        rect_coord, rect_point, diagonal_point, general_point)
            else:
                if rect_point[2] not in vertices:
                    dot_num = two_diagonal_down_right_triangle_dot_count(
                        rect_coord, rect_point, diagonal_point, general_point)
                else:
                    general_point[0][0] = x_sum - general_point[0][0]
                    dot_num = two_diagonal_down_right_triangle_dot_count(
                        rect_coord, rect_point, diagonal_point, general_point)
        else:
            diagonal_point = [rect_point[0], rect_point[3]]
            if rect_point[0] in vertices:
                if general_point[0][1] == rect_coord[2]:
                    dot_num = \
                        two_diagonal_touch_edge_down_right_triangle_dot_count(
                            rect_coord, rect_point, diagonal_point,
                            general_point)
                elif general_point[0][1] == rect_coord[3]:
                    for p in general_point:
                        p[0] = x_sum - p[0]
                        p[1] = y_sum - p[1]
                    dot_num = \
                        two_diagonal_touch_edge_down_right_triangle_dot_count(
                            rect_coord, rect_point, diagonal_point,
                            general_point)
                elif general_point[0][0] == rect_coord[1]:
                    dot_num = \
                        two_diagonal_touch_edge_up_right_triangle_dot_count(
                            rect_coord, rect_point, diagonal_point,
                            general_point)
                elif general_point[0][0] == rect_coord[0]:
                    for p in general_point:
                        p[0] = x_sum - p[0]
                        p[1] = y_sum - p[1]
                    dot_num = \
                        two_diagonal_touch_edge_up_right_triangle_dot_count(
                            rect_coord, rect_point, diagonal_point,
                            general_point)
            else:
                if general_point[0][1] == rect_coord[2]:  # y_min
                    for p in general_point:
                        p[0] = x_sum - p[0]
                    dot_num = \
                        two_diagonal_touch_edge_down_right_triangle_dot_count(
                            rect_coord, rect_point, diagonal_point,
                            general_point)
                elif general_point[0][1] == rect_coord[3]:  # y_max
                    for p in general_point:
                        p[1] = y_sum - p[1]
                    dot_num = \
                        two_diagonal_touch_edge_down_right_triangle_dot_count(
                            rect_coord, rect_point, diagonal_point,
                            general_point)
                elif general_point[0][0] == rect_coord[1]:  # x_max
                    for p in general_point:
                        p[1] = y_sum - p[1]
                    dot_num = \
                        two_diagonal_touch_edge_up_right_triangle_dot_count(
                            rect_coord, rect_point, diagonal_point,
                            general_point)
                elif general_point[0][0] == rect_coord[0]:  # x_min
                    for p in general_point:
                        p[0] = x_sum - p[0]
                    dot_num = \
                        two_diagonal_touch_edge_up_right_triangle_dot_count(
                            rect_coord, rect_point, diagonal_point,
                            general_point)
    elif len(diagonal_point) == 3:
        diagonal_point = None
        for i in xrange(len(vertices)):
            v_1 = vertices[i]
            v_2 = vertices[(i + 1)% len(vertices)]
            if v_1[0] - v_2[0] != 0 and v_1[1] - v_2[1] != 0:
                diagonal_point = [v_1, v_2]
                break
        horizontal_line_dots = rect_coord[1] - rect_coord[0] + 1
        vertical_line_dots = rect_coord[3] - rect_coord[2] + 1
        diagonal_line_dots = diagonal_dot_count(diagonal_point)
        triangle_dots = right_triangle_dot_count(vertices)
        dot_num = triangle_dots - horizontal_line_dots -vertical_line_dots - \
                  diagonal_line_dots + 3
    else:
        raise Exception('Something went wrong!')
    return dot_num