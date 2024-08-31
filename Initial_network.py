from tqdm import tqdm
import airport
import os.path
import geo
import Cst
import QPPTW
import random
import json

APT_FILE = Cst.APT_FILE
airport_cepo = airport.load2(APT_FILE)
airport_init = airport.load(APT_FILE)
turn_lines = {}
# thrust_level = [0.0355, 0.0532, 0.0708, 0.0887, 0.106, 0.106, float('inf'), 0.124]
# thrust_level = [0.0355, 0.04814, 0.06078, 0.07342, 0.08606, 0.0987, 0.11134, 0.124]
thrust_level = [0.0372, 0.0496, 0.062, 0.0744, 0.0868, 0.0992, 0.1116, 0.124]
# thrust_level = [0.101, 0.128, 0.155, 0.182, 0.209, 0.236, 0.263, 0.291]


def calculate_cost(length, speed, fuel_rate):
    """
    Calculate the time and fuel cost for a segment at a given speed.

    :param length: Length of the segment in meters.
    :param speed: Speed in m/s.
    :param fuel_rate: Fuel consumption rate in liters per second.
    :return: Tuple of time cost (in seconds) and fuel cost (in liters).
    """
    # print(speed, fuel_rate)
    time_cost = abs(length / speed)  # Time to travel the segment
    fuel_cost = time_cost * fuel_rate  # Total fuel consumed
    # fuel_cost = 0
    return time_cost, fuel_cost


def check_pushback_times(graph, pushback_edges, source):
    check = 0
    if len(graph[source]) > 1:  # Only one pushback do not think about this
        for edge in graph[source]:
            if edge in pushback_edges:  # Ensure the boolean value
                check += 1
            else:
                continue
    return check


def initial_network(airport_cepo):
    graph = {}
    graph_r = {}
    weights = {}
    network = {}
    in_angles = {}
    out_angles = {}
    time_windows = {}
    init_l = {}
    # print("the number of points", len(airport_cepo.points))
    # points, lines, runways = [], [], []
    points = airport_cepo.points
    runways = airport_cepo.runways
    lines = airport_cepo.lines
    init_lines = airport_init.lines
    points0 = airport_init.points
    pushback_edges = []

    for (i, point) in enumerate(points):
        network[point.xy] = {}
        in_angles[point.xy] = {}
        out_angles[point.xy] = {}
        graph[point.xy] = []
        graph_r[point.xy] = []
    for (i, line) in enumerate(lines):
        line_init = init_lines[i]
        length = geo.length(line_init.xys)
        # print(line.speed)

        length_cepo = abs(length / line.speed)
        # if line.speed != 10:
        #     length_cepo = abs(length / 3)

        # print(line_init.xys)
        p11 = line_init.xys[0]
        p22 = line_init.xys[1]
        p33 = line_init.xys[-2]
        p44 = line_init.xys[-1]
        p1 = line.xys[0]
        p4 = line.xys[-1]
        # print(line.speed)

        """此处删掉0.1的长度的line是因为对应于CEPO相同的路网
           CEPO路网中为了提高速度删掉了这个line
           可能这个距离计算不准确存在误差但影响不大
           正常做对比时不需要删掉 如果一定要和CEPO对比，那请细致考虑"""
        # if length_cepo == 0.1:
        #     # print('Line = 0。1', line.oneway, line.taxiway, line.xys, length)
        #     continue
        # if p1 == (22622, 7891) and p4 != (22622, 7892):
        #     p1 = (22622, 7892)
        #     length = length + 1
        # elif p4 == (22622, 7891) and p1 != (22622, 7892):
        #     p4 = (22622, 7892)
        #     length = length + 1
        # else:
        #     length = 0

        if line.speed != 10:
            if (p4, p1) not in turn_lines:
                turn_lines[(p1, p4)] = line.speed
                turn_lines[(p4, p1)] = line.speed
                length = -length
        init_l[(p1, p4)] = length
        init_l[(p4, p1)] = length

        # if length == 0.0:
        #     print('Line = 0', line.oneway, line.taxiway)

        while length != 0.0:  # ignore the line with length '0'
            # network[p1][p4] = length_cepo
            # network[p4][p1] = length_cepo
            if (p1, p4) not in graph[p1]:
                graph[p1].append((p1, p4))
                graph_r[p1].append((p4, p1))
            if (p4, p1) not in graph[p4]:
                graph[p4].append((p4, p1))
                graph_r[p4].append((p1, p4))

            weights[(p1, p4)] = length_cepo
            weights[(p4, p1)] = length_cepo
            time_windows[(p1, p4)] = [(-24 * 60 * 60 * 1.5, 24 * 60 * 60 * 1.5)]
            time_windows[(p4, p1)] = [(-24 * 60 * 60 * 1.5, 24 * 60 * 60 * 1.5)]
            if line.speed < 0:  # Give the angle of every arc and reverse the pushback's outangle
                in_angles[p1][p4] = geo.angle_2p(p11, p22)
                out_angles[p1][p4] = geo.angle_2p(p44, p33)
                in_angles[p4][p1] = geo.angle_2p(p44, p33)
                out_angles[p4][p1] = geo.angle_2p(p22, p11)
                pushback_edges.append((p1, p4))
            else:
                in_angles[p1][p4] = geo.angle_2p(p11, p22)
                out_angles[p1][p4] = geo.angle_2p(p33, p44)
                in_angles[p4][p1] = geo.angle_2p(p44, p33)
                out_angles[p4][p1] = geo.angle_2p(p22, p11)
            length = 0.0  # 注意浮点型
            if line.oneway:  # 处理路网单向路
                graph[p4].remove((p4, p1))
                graph_r[p1].remove((p4, p1))

    for (i, runway) in enumerate(runways):
        p1 = runway.xys[0]
        p2 = runway.xys[1]
        # graph[p1] = {}
        # graph[p2] = {}
        if (p1, p2) not in graph[p1]:
            graph[p1].append((p1, p2))
            graph_r[p2].append((p1, p2))
        if (p2, p1) not in graph[p2]:
            graph[p2].append((p2, p1))
            graph_r[p1].append((p2, p1))
        length = float('inf')
        # init_l[(p1, p2)] = length
        # init_l[(p2, p1)] = length
        weights[(p1, p2)] = length
        weights[(p2, p1)] = length
        time_windows[(p1, p2)] = [(-24 * 60 * 60 * 1.5, 24 * 60 * 60 * 1.5)]
        time_windows[(p2, p1)] = [(-24 * 60 * 60 * 1.5, 24 * 60 * 60 * 1.5)]

        in_angles[p1][p2] = geo.angle_2p(p1, p2)
        out_angles[p1][p2] = geo.angle_2p(p1, p2)
        in_angles[p2][p1] = geo.angle_2p(p2, p1)
        out_angles[p2][p1] = geo.angle_2p(p2, p1)

    # Initialize the cost matrix for each segment
    costs = {}

    # Assuming speeds and fuel_consumption_rate are defined
    # print(fuel_rates)
    fuel_consumption_rate = thrust_level[0]  # Replace with actual value
    # fuel_consumption_rates = [0.291, 0.291*0.75, 0.291*0.5]

    for (i, line) in enumerate(lines):
        line_init = init_lines[i]
        p1 = line.xys[0]
        p4 = line.xys[-1]
        edge = (p1, p4)
        length = geo.length(line_init.xys)  # Assuming this is the length of the segment
        rates = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

        if line.speed < 0:
            # if edge in turn_lines:
            speed = abs(line.speed)  # Speed = -3
            costs[(p4, p1)] = costs[(p1, p4)] = calculate_cost(length, speed, fuel_consumption_rate)
        else:
            # Calculate cost for each speed
            fuel_rates = thrust_level[:line.speed - 2]
            rates = rates[:line.speed - 2]

            costs[(p4, p1)] = costs[(p1, p4)] = [calculate_cost(length, 10 * rate, fuel_conrate) for
                                                 rate, fuel_conrate in zip(rates, fuel_rates)]
    # print(costs)
    # Now, `costs` dictionary contains the time and fuel costs for each segment at different speeds
    return graph, weights, time_windows, in_angles, out_angles, costs, pushback_edges, init_l, turn_lines, graph_r


def cal_fuel(time_cost, path1, weights):
    if time_cost == 0:
        fuel_cost = 0
    elif time_cost != 0 and time_cost != float('inf'):
        fuel_cost = 0
        for i in range(1, len(path1)):
            current_vertex = path1[i - 1]
            next_vertex = path1[i]
            edge = (current_vertex, next_vertex)
            # fuel_cost = 0
            if edge in turn_lines:
                # print( Initial_network.thrust_level[abs(Initial_network.turn_lines[edge]) - 3])
                fuel_cost = fuel_cost + weights[edge] * thrust_level[abs(turn_lines[edge]) - 3]
            else:
                fuel_cost = fuel_cost + weights[edge] * thrust_level[-1]
    elif time_cost == float('inf'):
        fuel_cost = float('inf')
    return fuel_cost


def find_min_in_filtered_list0(COST_list):
    # 将 COST_list 中的所有集合扁平化为一个包含所有成本向量的列表
    # flattened_list = [item for sublist in COST_list if sublist is not None for item in sublist]
    flattened_list = list(COST_list)
    # 过滤掉所有的 None 元素
    filtered_list = [x for x in flattened_list if x is not None]
    if filtered_list:
        # 如果过滤后的列表不为空，则寻找最小成本向量
        min_cost_vector = min(filtered_list, key=lambda x: list(x)[0][0])
    else:
        # 如果过滤后的列表为空，则设置 min_cost_vector 为 None 或其他适当的默认值
        min_cost_vector = None

    return min_cost_vector


def find_min_in_filtered_list(time_list):
    filtered_list = [x for x in time_list if x is not None]
    if filtered_list:
        min_cost_vector = min(filtered_list)
        # print(min_cost_vector, time_list)
    else:
        min_cost_vector = None
    return min_cost_vector


def correspond_path(path_list1, time_list1, time_cost):
    if time_cost:
        path1 = path_list1[time_list1.index(time_cost)]
    else:
        path1 = None
    return path1


# Initial_cost of the all points, and the cost is the smallest weight between the two points
def initial_cost(graph, weights, time_windows, in_angles, out_angles, Stand, pushback_edges, graph_c):
    # points = airport_init.points
    start_time = 0
    points0 = airport_cepo.points
    cost_of_path = {}
    runway_points = [p for p in points0 if p.ptype == 'Stand' or p.ptype == 'Runway']
    # n_points = [p for p in points0 if p.ptype != 'Stand' and p.ptype != 'Runway']
    # stand_points = [p for p in points0 if p.ptype == 'Stand']
    # with open('cost_of_path.json', 'r') as file:
    #     cost_of_path = json.load(file)
    for s in tqdm(points0, ncols=100):
        source = s.xy
        ss = str(s.xy)
        for d in runway_points:
            if s.ptype == 'Stand' and d.ptype == 'Runway':  # 避免重复的一种情况
                continue
            # elif s.ptype == 'Stand' and d.ptype == 'Stand':
            #     continue
            # elif s.ptype == 'Runway' and d.ptype == 'Runway':
            #     continue

            # if s.xy == (22232, 8079) or d.xy == (22232, 8079):
            #     if d.xy == (20095, 6987) or s.xy == (20095, 6987):
            #         print('s:', s.xy, s.ptype, 'd:', d.xy, d.ptype)
            #     else:
            #         continue
            # else:
            #     continue

            target = d.xy
            tt = str(d.xy)

            check = check_pushback_times(graph, pushback_edges, target)
            list_edge = graph_c[target]
            # print(check)
            if check >= 2:  # When the stand have two ways to pushback, we need choose one
                time_list1 = []
                time_list2 = []
                path_list1 = []
                path_list2 = []
                for e in list_edge:
                    if e in pushback_edges:
                        graph[target].remove(e)
                        _, path1, new_time_windows, time_cost = QPPTW.QPPTW_algorithm(graph, weights, time_windows,
                                                                                      source,
                                                                                      target,
                                                                                      start_time, in_angles, out_angles,
                                                                                      Stand)
                        _, path2, new_time_windows, time_cost2 = QPPTW.QPPTW_algorithm(graph, weights, time_windows,
                                                                                       target,
                                                                                       source,
                                                                                       start_time, in_angles,
                                                                                       out_angles, Stand)
                        graph[target].append(e)
                        time_list1.append(time_cost)
                        time_list2.append(time_cost2)
                        path_list1.append(path1)
                        path_list2.append(path2)
                # print("check1", check, len(time_list1), len(time_list2), list_edge)
                if time_list1 and time_list2:
                    time_cost = find_min_in_filtered_list(time_list1)
                    time_cost2 = find_min_in_filtered_list(time_list2)

                path1 = correspond_path(path_list1, time_list1, time_cost)
                path2 = correspond_path(path_list2, time_list2, time_cost2)
                # print("check2", check, time_list1, time_list2, '\n')

            else:
                _, path1, new_time_windows, time_cost = QPPTW.QPPTW_algorithm(graph, weights, time_windows, source,
                                                                              target,
                                                                              start_time, in_angles, out_angles, Stand)
                _, path2, new_time_windows, time_cost2 = QPPTW.QPPTW_algorithm(graph, weights, time_windows, target,
                                                                               source,
                                                                               start_time, in_angles, out_angles, Stand)

            fuel_cost = cal_fuel(time_cost, path1, weights)
            fuel_cost2 = cal_fuel(time_cost2, path2, weights)

            if ss not in cost_of_path.keys():
                cost_of_path[ss] = {}
            if tt not in cost_of_path.keys():
                cost_of_path[tt] = {}
            if d == s:
                cost_of_path[ss][tt] = cost_of_path[tt][ss] = 0
                continue

            cost_of_path[ss][tt] = (time_cost, fuel_cost)
            cost_of_path[tt][ss] = (time_cost2, fuel_cost2)

    with open('cost_of_path_cut60.json', 'w') as file:
        json.dump(cost_of_path, file, indent=4)
    # with open('cost_of_path.json', 'w') as file:
    #     json.dump(cost_of_path, file, indent=4)

# with open('cost_of_path.json', 'r') as file:
#     cost_of_path = json.load(file)
# 调用函数
# initial_cost(graph, weights, time_windows, source, target, start_time, in_angles, out_angles, Stand)
