import sys
import airport
import Initial_network
import datetime
import Sour_and_Des
import json
import os
import Cst
import MOA
import QPPTW
import Draw_path
import copy
from tqdm import tqdm
import pandas as pd
import gaptraffic
import Def_BOF
import csv
import Simulate
# above imported library
import MOA2
import numpy as np

""" Default airport and traffic files """
DATA_PATH = Cst.DATA_PATH
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")
# FPL_FILE = os.path.join(DATA_PATH, "ZBTJ_20210725_Manex_STD.B&B.sim")
FPL_FILE = os.path.join(DATA_PATH, "ZBTJ_20210725_Manex_16R.B&B.sim")


# 函数，将列表写入到json文件
def write_list_to_json(list_name, filename):
    with open(filename, 'w') as f:
        json.dump(list_name, f)


# 函数，将列表写入到文件
def write_list_to_file(list_name, filename):
    with open(filename, 'w') as f:
        for item in list_name:
            f.write("%s\n" % item)


def show_point_name(point, points):
    for p in points:
        if p.xy[0] == point[0] and p.xy[1] == point[1]:
            point_name = p.name
            return point_name


def show_point_coor(point, points):
    for p in points:
        if p.name == point:
            point_xy = p.xy
            return point_xy


def check_pushback_times(graph, pushback_edges, source):
    check = 0
    if len(graph[source]) > 1:  # Only one pushback do not think about this
        for edge in graph[source]:
            if edge not in pushback_edges:  # Ensure the boolean value
                continue
            elif edge in pushback_edges:
                check += 1
    return check


if __name__ == "__main__":
    fpl_file = sys.argv[1] if 1 < len(sys.argv) else FPL_FILE
    # Load the airport and the traffic
    the_airport = airport.load(APT_FILE)
    the_airport2 = airport.load2(APT_FILE)
    points = the_airport2.points
    runways = the_airport2.runways

    # 定义文件路径
    input_file = "speed_changes_matrix.txt"

    # 从文件中读取矩阵
    speed_matrix = np.loadtxt(input_file, delimiter=",")

    stand_dict, runway_dict, stand_list, stand_dict2, runway_list, runway_dict2 \
        = Sour_and_Des.stand_and_runway_points(points=the_airport2.points)

    """遍历一天"""
    # flight_file_name_list = Cst.file
    # print(Cst.file)
    """一次性遍历十天"""
    flight_file_name_list = Cst.flight_file_name_list

    COSTS = []
    Stand = []
    Paths2 = []
    for p in points:
        if p.ptype == 'Stand' or p.ptype == 'Runway':
            Stand.append(p.xy)


    def algorithm(flights, file_name, W, Paths, Loop):
        graph, weights, time_windows, in_angles, out_angles, costs, pushback_edges, init_l, turn_lines, graph_r = \
            Initial_network.initial_network(the_airport2)
        Failure_flight = []

        graph_copy = copy.deepcopy(graph)
        windoew0 = copy.deepcopy(time_windows)

        # 把路网中的cost信息提前预存，每次更换路网只需要运行一次
        # Initial_network.initial_cost(graph, weights, time_windows, in_angles, out_angles, Stand, pushback_edges, graph_copy)

        # with open('cost_of_path.json', 'r') as file:
        cost_of_path = 0
        with open('cost_of_path_cut60.json', 'r') as file:
            cost_of_path = json.load(file)

        Total_cost = 0
        init_Tcost = 0
        turn_times = 0
        Tcost_without_waiting = 0
        Lenth = 0
        totalholding_time = 0

        # 使用tqdm来遍历航班列表，并设置进度条长度(ncols)为100
        for flightnum in tqdm(range(0, len(flights)), ncols=100):
        # for flightnum in range(276, 280):
            # print(flightnum)
            # 多飞机规划路径：初始化开始时间
            # init_time = datetime.datetime(2023, 4, 17, 7, 0)

            results = []
            paths = []
            pts = []
            COST_list = []
            flight = flights[flightnum]

            # 这里是选择确定飞机的推出的时间
            if flight.departure == 'ZBTJ':
                start_time = flight.start_taxi_time
                start_time = flight.ttot
                if Loop:
                    start_time = Paths[flightnum].BOT
            else:
                start_time = flight.start_taxi_time

            # 这里是选择确定飞机的起飞与终点
            source, target = Sour_and_Des.find_the_sour_des(stands=stand_dict, pists=runway_dict, flight=flight)
            name1 = show_point_name(source, points=the_airport2.points)
            name2 = show_point_name(target, points=the_airport2.points)

            if flightnum == 67:
                pass
            # print(start_time, target, flightnum, flight.departure == 'ZBTJ')

            # target = (20095, 6987)
            # source = (22530, 8090)
            # _, path1, new_time_windows, time_cost = QPPTW.QPPTW_algorithm(graph, weights, time_windows, source, target,
            #                                                               start_time, in_angles, out_angles, Stand)
            # print("time:", time_cost)
            # path = []
            # Draw_path.create_matplotlib_figure(graph, path1, name1, name2, flightnum, turn_lines)

            check = check_pushback_times(graph, pushback_edges, source)
            list_edge = graph[source]
            # 在此修改起飞航班反过来
            if flight.departure == 'ZBTJ':
                s = source
                source = target
                target = s
                start_time = flight.ttot
                # if flightnum == 279:
                # if flightnum == 324 or flightnum == 431:
                #     start_time += 60

                if check >= 2:  # When the stand have two ways to pushback, we need choose one
                    for i in range(len(list_edge)):
                        e = list_edge[i-1]
                        if e in pushback_edges:
                            graph_r[e[1]].remove(e)
                            graph[e[0]].remove(e)
                            path, COST, holding_time, pt = MOA2.AMOA_star(source, target, costs, graph_r, time_windows,
                                                                     start_time, out_angles,
                                                                     in_angles, Stand, weights, cost_of_path, W, graph, windoew0, flightnum)
                            graph_r[e[1]].append(e)
                            graph[e[0]].append(e)
                            COST_list.append(COST)
                            paths.append(path)
                            pts.append(pt)

                    if COST_list:
                        COST = Initial_network.find_min_in_filtered_list0(COST_list)
                        path = Initial_network.correspond_path(paths, COST_list, COST)
                        pt = pts[paths.index(path)] if path else None

                else:  # the normal condition
                    path, COST, holding_time, pt = MOA2.AMOA_star(source, target, costs, graph_r, time_windows, start_time,
                                                             out_angles, in_angles,
                                                             Stand, weights, cost_of_path, W, graph, windoew0, flightnum)
                # 为了在形成带有标签的路径的起始时间正确
                if COST is not None:
                    start_time = start_time - list(COST)[0][0]
                source = s

            else:
                # continue
                if check >= 2:  # When the stand have two ways to pushback, we need choose one
                    for e in list_edge:
                        if e in pushback_edges:
                            graph_copy[source].remove(e)
                            path, COST, holding_time, pt = MOA.AMOA_star(source, target, costs, graph_copy, time_windows,
                                                                     start_time, out_angles,
                                                                     in_angles, Stand, weights, cost_of_path,  W, graph, windoew0, flightnum)
                            graph_copy[source].append(e)
                            COST_list.append(COST)
                            paths.append(path)
                            pts.append(pt)

                    if COST_list:
                        COST = Initial_network.find_min_in_filtered_list0(COST_list)
                        path = Initial_network.correspond_path(paths, COST_list, COST)
                        pt = pts[paths.index(path)]
                else:  # the normal condition
                    path, COST, holding_time, pt = MOA.AMOA_star(source, target, costs, graph, time_windows, start_time,
                                                             out_angles, in_angles,
                                                             Stand, weights, cost_of_path, W, graph, windoew0, flightnum)

            if COST is None or path is None:
                Failure_flight.append(flightnum)
                print("NONONONONONO", path, start_time, flight.start_taxi_time, flightnum, flight.departure)
                # if path:
                #     Draw_path.create_matplotlib_figure(graph, path, name1, name2, flightnum, turn_lines)
            elif path:
                """ 输入speed的变化情况 """
                speed_change = speed_matrix[flightnum]
                speed_change = 1
                label_path = QPPTW.construct_labeled_path(graph, weights, time_windows, source, start_time, path, flight, speed_change, pt)
                time_windows = QPPTW.Readjustment_time_windows(graph, weights, time_windows, label_path)
                # graph0, weights0, time_windows0, in_angles0, out_angles0, costs0, pushback_edges0 = \
                #     Initial_network.initial_network(the_airport)
                # print("YESYESYES", path, start_time, flight.start_taxi_time, flightnum, flight.departure)
                # Draw_path.create_matplotlib_figure(graph, path, name1, name2, flightnum, turn_lines)

                # """记录每一个航班的成本"""
                # COSTS.append(list(COST)[0][0])
                Total_cost = Total_cost + list(COST)[0][0]
                init_Tcost = init_Tcost + list(COST)[0][1]
                # 用于结果处理原始路径以及转弯次数
                lenth = 0
                time_lenth = 0
                turn_time = 0
                for i in range(1, len(path)):
                    current_vertex = path[i - 1]
                    next_vertex = path[i]
                    edge = (current_vertex, next_vertex)
                    l = init_l[edge]
                    t = weights[edge]
                    if edge in turn_lines:
                        turn_time += 1
                    lenth = lenth + abs(l)
                    time_lenth = time_lenth + t
                turn_times = turn_times + turn_time
                Lenth = Lenth + lenth
                Tcost_without_waiting = Tcost_without_waiting + time_lenth
                # totalholding_time = totalholding_time + holding_time
                if flight.departure == 'ZBTJ':
                    Path = Def_BOF.Path(flight=flightnum, arrive=flight.arrivee, S=source, E=target, length=lenth,
                                        time_cost=time_lenth, fuel_cost=list(COST)[0][1], point=path, BOT=start_time,
                                        TOF=start_time + list(COST)[0][0], TTOF=flight.ttot, check=True)
                else:
                    Path = Def_BOF.Path(flight=flightnum, arrive=flight.arrivee, S=source, E=target, length=lenth,
                                        time_cost=time_lenth, fuel_cost=list(COST)[0][1], point=path, BOT=start_time,
                                        TOF=start_time + list(COST)[0][0], TTOF=flight.aldt, check=True)
            if Loop:
                Paths2.append(Path)
            else:
                Paths.append(Path)
            # print(COST, time_lenth)
            # print("fligt:", flightnum, "Path:", path)
            # print("Cost:",flightnum, COST, turn_time)
            # print("Cost:", flightnum, turn_time)
        # cost_info = {
        #     "Date": file_name,
        #     "Total cost": Total_cost,
        #     "Fuel cost": init_Tcost,
        #     "Length": Lenth,
        #     "Tcost without waiting": Tcost_without_waiting,
        #     "Total turn times": turn_times,
        #     "False flight number": len(Failure_flight),
        #     "False": Failure_flight,
        # }
        # COSTS.append(cost_info)
        # print(cost_info)
        print("Total cost:", Total_cost, "Fuel_cost ", init_Tcost, "Lenth:", Lenth, "Total_turn_times ", turn_times, W)
        # 现在我们可以调用这些函数将列表写入到文本文件
        # write_list_to_json(COSTS, ' Results/' + file_name + str(Cst.weight) + 'cost.json')
        # 确保目录存在
        # file = Cst.file
        # os.makedirs(file, exist_ok=True)
        if Loop:
            return COSTS, Paths2
        return COSTS, Paths


    for file_name in flight_file_name_list:
        W = Cst.weight
        # W = [0.1, 0,9]
        Loop = 0
        Paths = []
        Paths2 = []
        check_break = False
        if file_name == 'g' or file_name == '2':
            flights = gaptraffic.read_flights("Datas/traffic/" + flight_file_name_list)
            COSTS, Paths = algorithm(flights, flight_file_name_list, W, Paths, Loop)
            check_break = True
        else:
            flights = gaptraffic.read_flights("Datas/traffic/" + file_name)
            COSTS, Paths = algorithm(flights, file_name, W, Paths, Loop)

        # write_list_to_json(COSTS, 'Results/' + 'Total_ten_days' + str(Cst.weight) + 'cost.json')

        """下面用于二次循环确定OBT"""
        # for Path in Paths:
        #     if flights[Path.flight].departure == 'ZBTJ':
        #         # start_time = flights[Path.flight].ttot - 600
        #         Path.get_check()
        #     else:
        #         Path.TOF = flights[Path.flight].ttot
        #         while not Path.check:
        #             start_time = Path.BOT
        # Loop = 1
        # COSTS, Paths = algorithm(flights, file_name, W, Paths, Loop)
        """上面用于二次循环确定OBT"""

        paths4simu = Simulate.get_simulation_file(Paths, the_airport2.lines)
        # print(paths4simu)
        # Simulate.save_as_file(paths4simu, Loop, file_name)

        if check_break:
            break

        """保存OBT信息成CSV文件"""
        # with open('Results/Add_runway_block/output_increased_' + str(Loop) + '_' + file_name + '.csv', 'w',
        # newline='') as file: writer = csv.writer(file)  # 写入表头 if Loop: writer.writerow(['OBT_new', 'TOT_new',
        # 'TTOT', 'TOT_new-TTOT', 'OBT_new-TTOT']) else: writer.writerow(['OBT_old', 'TOT_old', 'TTOT',
        # 'TOT_old-TTOT', 'OBT_old-TTOT'])
        # 遍历 Paths 列表中的每个 Path 对象
        # for path in Paths:
        # 从每个 Path 对象中提取 BOT 和 TTOF 属性
        # bot = path.BOT tof = path.TOF ttof = path.TTOF TT = tof - ttof BT = bot - ttof
        #
        #         # 写入这些属性到 CSV 文件中
        #         writer.writerow([bot, tof, ttof, TT, BT])

    """下面用于将结果保存为EXCEL文件"""
    # 在循环外初始化一个空的DataFrame
    # results = pd.DataFrame(columns=['Weight1', 'Weight2', 'TimeCost', 'FuelCost'])
    # n = 200
    # for i in tqdm(range(n+1), ncols=75):
    #     # 计算权重
    #     weight = [1 - 1/n * i, 0 + 1/n * i]
    #     flights = gaptraffic.read_flights("Datas/traffic/" + flight_file_name_list)
    #     COSTS = algorithm(flights, flight_file_name_list, weight)
    #     timecost = COSTS[i]['Total cost']
    #     fuelcost = COSTS[i]['Fuel cost']
    #
    #     # 将结果追加到DataFrame中
    #     results = results.append({
    #         'Weight1': weight[0],
    #         'Weight2': weight[1],
    #         'TimeCost': timecost,
    #         'FuelCost': fuelcost
    #     }, ignore_index=True)
    #
    # # 确保数据按照Weight1列排序
    # results.sort_values(by='Weight1', inplace=True)
    # # 将结果DataFrame保存到CSV文件中
    # results.to_csv('results单机.csv', index=False)
