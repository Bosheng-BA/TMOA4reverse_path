import geo
import Cst
import os


class Line:
    def __init__(self, number, taxiway, type, oneway, radium, points, label):
        self.number = number
        self.taxiway = taxiway
        self.type = type
        self.oneway = oneway
        self.radium = radium
        self.points = points
        self.label = label


class Line0:
    def __init__(self, taxiway, type, oneway, radium, points):
        self.taxiway = taxiway
        self.type = type
        self.oneway = oneway
        self.radium = radium
        self.points = points


def get_xy_int(str_xy):
    """ Convert a x,y string 'str_xy' to coordinates """
    (str_x, str_y) = str_xy.split(',')
    return int(float(str_x)), int(float(str_y))


def get_xy_float(str_xy):
    """ Convert a x,y string 'str_xy' to coordinates """
    (str_x, str_y) = str_xy.split(',')
    return float(str_x), float(str_y)


def get_xys_float(str_xy_list):
    """ Convert a x,y string list 'str_xy_list' to coordinates """
    return [get_xy_float(str_xy) for str_xy in str_xy_list]


def get_xys_int(str_xy_list):
    """ Convert a x,y string list 'str_xy_list' to coordinates """
    return [get_xy_int(str_xy) for str_xy in str_xy_list]


def split_line(line):
    """将长线段分割成长度不超过60的子线段，确保剩余线段长度至少为50"""
    new_lines = []
    points = line.points
    temp_points = [points[0]]
    current_length = 0

    for i in range(1, len(points)):
        edge = [points[i - 1], points[i]]
        segment_length = geo.length(edge)

        while current_length + segment_length > 60:
            remaining_length = 60 - current_length
            ratio = remaining_length / segment_length
            new_x = points[i - 1][0] + ratio * (points[i][0] - points[i - 1][0])
            new_y = points[i - 1][1] + ratio * (points[i][1] - points[i - 1][1])
            new_point = (new_x, new_y)

            temp_points.append(new_point)
            new_lines.append(Line0(line.taxiway, line.type, line.oneway, line.radium, temp_points))

            points[i - 1] = new_point
            segment_length -= remaining_length
            temp_points = [new_point]
            current_length = 0

        temp_points.append(points[i])
        current_length += segment_length

    if len(temp_points) > 1 and current_length >= 50:
        new_lines.append(Line0(line.taxiway, line.type, line.oneway, line.radium, temp_points))
        # print(temp_points)
    elif len(temp_points) > 1:
        # 如果最后一个片段小于50，和前一个片段合并
        if new_lines:
            # print(temp_points)
            last_line = new_lines.pop()
            last_line.points.extend(temp_points[1:])
            new_lines.append(last_line)
            # print(last_line.points)
        else:
            # print('11111111111111')
            # print(temp_points)
            new_lines.append(Line0(line.number, line.taxiway, line.type, line.oneway, line.radium, temp_points))

    return new_lines


def load(filename):
    """Load an airport description 'file' and return the airport"""
    print('Loading airport:', filename + '...', end='')
    with open(filename, 'r') as file:
        lines = file.readlines()

    new_lines = []
    other_lines = []

    for line in lines:
        words = line.strip().split(' ')
        if words[0] == 'l' and not words[1].isdigit():  # Line description
            if words[2] != 'pushback':
                taxiway = words[1]
                type = words[2]
                oneway = words[3]
                radius = float(words[4])
                xys = get_xys_float(words[5:])
                length = geo.length(xys)

                line_obj = Line0(taxiway, type, oneway, radius, xys)

                if length > 110:
                    new_lines.extend(split_line(line_obj))
                else:
                    # print(xys, length, words)
                    new_lines.append(line_obj)
            else:
                other_lines.append(line.strip())
        else:
            other_lines.append(line.strip())

    with open(filename, 'w') as file:
        for line in new_lines:
            line_str = f"l {line.taxiway} {line.type} {line.oneway} {line.radium} " + \
                       " ".join([f"{p[0]},{p[1]}" for p in line.points])
            file.write(line_str + '\n')

        for line in other_lines:
            file.write(line + '\n')

    print('Done.')


def split_line2(line):
    """将长线段分割成长度不超过60的子线段，确保剩余线段长度至少为50"""
    new_lines = []
    points = line.points
    temp_points = [points[0]]
    current_length = 0

    for i in range(1, len(points)):
        edge = [points[i - 1], points[i]]
        segment_length = geo.length(edge)

        while current_length + segment_length > 60:
            remaining_length = 60 - current_length
            ratio = remaining_length / segment_length
            new_x = points[i - 1][0] + ratio * (points[i][0] - points[i - 1][0])
            new_y = points[i - 1][1] + ratio * (points[i][1] - points[i - 1][1])
            new_point = (new_x, new_y)

            temp_points.append(new_point)
            new_lines.append(
                Line(line.number, line.taxiway, line.type, line.oneway, line.radium, temp_points, line.label))

            points[i - 1] = new_point
            segment_length -= remaining_length
            temp_points = [new_point]
            current_length = 0

        temp_points.append(points[i])
        current_length += segment_length

    if len(temp_points) > 1 and current_length >= 50:
        new_lines.append(Line(line.number, line.taxiway, line.type, line.oneway, line.radium, temp_points, line.label))
    elif len(temp_points) > 1:
        # 如果最后一个片段小于50，和前一个片段合并
        if new_lines:
            last_line = new_lines.pop()
            last_line.points.extend(temp_points[1:])
            new_lines.append(last_line)
        else:
            new_lines.append(
                Line(line.number, line.taxiway, line.type, line.oneway, line.radium, temp_points, line.label))

    return new_lines


def load2(filename):
    """Load an airport description 'file' and return the airport"""
    print('Loading airport:', filename + '...', end='')
    with open(filename, 'r') as file:
        lines = file.readlines()

    new_lines = []
    other_lines = []

    line_index = 0
    for index, line in enumerate(lines):
        words = line.strip().split(' ')
        if words[0] == 'l' and words[2] != 'pushback' and not words[1].isdigit():  # Line description
            taxiway = words[1]
            type = words[2]
            oneway = words[3]
            radius = float(words[4])
            xys = get_xys_float(words[5:-1])
            length = geo.length(xys)
            label = words[-1]

            line_obj = Line(line_index, taxiway, type, oneway, radius, xys, label)

            if length > 110:
                new_lines.extend(split_line2(line_obj))
            else:
                new_lines.append(line_obj)

            line_index += 1
        else:
            other_lines.append(line.strip())

    with open(filename, 'w') as file:
        for line in new_lines:
            line_str = f"l {line.taxiway} {line.type} {line.oneway} {line.radium} " + \
                       " ".join([f"{p[0]},{p[1]}" for p in line.points]) + f" {line.label}"
            file.write(line_str + '\n')

        for line in other_lines:
            file.write(line + '\n')

    print('Done.')


def load_label(filename):
    """Load an airport description 'file' and return the airport"""
    print('Loading airport:', filename + '...', end='')
    with open(filename, 'r') as file:
        lines = file.readlines()

    line_index = 0
    line_numbers = []
    for line in lines:
        words = line.strip().split(' ')
        if words[0] == 'l':
            line_numbers.append(str(line_index))
            line_index += 1
        else:
            line_numbers.append("-")

    with open(filename + '_label', 'w') as file:
        for index, line in enumerate(lines):
            file.write(line.strip() + ' ' + line_numbers[index] + '\n')

    print('Done.')


# 使用示例
DATA_PATH = Cst.DATA_PATH
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")
file_path = APT_FILE
""" first label the origin txt to new txt_label"""
load_label(file_path)

""" cut the txt path """
load(file_path)

""" Cut the txt_label path for the future using in output the simulation file """
file_path = os.path.join(DATA_PATH, "tianjin_new.txt_label")
load2(file_path)