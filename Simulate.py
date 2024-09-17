import csv


def get_simulation_file(paths, lines):
    new_path_list = {}
    for path in paths:
        new_path_list[path.BOT] = []
        new_path = []
        for i in range(len(path.point) - 1):
            point0 = path.point[i]
            point1 = path.point[i + 1]
            edge = [point0, point1]
            for j, l in enumerate(lines):
                # print(l.xys)
                if l.xys == edge:
                    # print("YES")
                    new_path.append(j)
                    break
            new_path_list[path.BOT] = new_path
    return new_path_list


def save_as_file(paths, Loop, file_name):
    with open('Results/Simulate_file/output_increased_' + str(Loop) + '_' + file_name + '.csv', 'w',
              newline='') as file:
        writer = csv.writer(file)  # 写入表头
        writer.writerow(['OBT', 'p'])

        # 遍历 Paths 列表中的每个 Path 对象
        for t in paths:
            # 从每个 Path 对象中提取 BOT 和 TTOF 属性
            OBT = t
            p = paths[t]

            # 写入这些属性到 CSV 文件中
            writer.writerow([OBT, p])
        print("Finish")


def calculate_positions(graph, path, pt, interval=5):
    positions = []
    total_time = 0  # 总时间累加器
    wait = 0

    for i in range(1, len(path)):
        segment_start = path[i - 1]
        segment_end = path[i]
        positions.append(segment_start)
        # segment_distance = np.linalg.norm(np.array(segment_end) - np.array(segment_start))
        # segment_speed = graph.get_speed(segment_start, segment_end)
        # taxiing, wait = pt[segment_end]
        # if i != 1:
        #     (_, wait) = pt[i - 2]
        (taxiing, wait) = pt[i - 1]
        if wait != 0:
            segment_time = taxiing - wait
            # total_time += wait
        else:
            segment_time = taxiing  # 当前段路径需要的时间
        # 计算当前段内每个5秒间隔的位置
        while total_time + interval <= taxiing:
            if total_time + interval < wait:
                total_time += interval
                positions.append(segment_start)
            else:
                total_time += interval
                ratio = (total_time - wait) / segment_time
                new_position = (segment_start[0] + ratio * (segment_end[0] - segment_start[0]),
                                segment_start[1] + ratio * (segment_end[1] - segment_start[1]))
                positions.append(new_position)
        # 剩余时间累加到下一段的时间中
        total_time -= taxiing
    return positions


def record_path(graph, path, pt, flight, start_time, file):
    positions = calculate_positions(graph, path, pt)
    traffic_points = ' '.join(f"{int(x)}.{int(y)}.G.142" for x, y in positions)

    # 修改的逻辑部分
    if flight.departure == 'ZBTJ':
        # time_str = flight.ttot - 600
        time_str = start_time + 600
        # print(f"D {flight.callsign} {time_str} {flight.parking} \nP 5 {traffic_points}")
        file.append(f"D {flight.callsign} {time_str} {flight.parking} \nP 5 {traffic_points}")
    else:
        # time_str = flight.aldt
        time_str = start_time
        file.append(f"A {flight.callsign} {time_str} {flight.parking} \nP 5 {traffic_points}")
        # print(f"A {flight.callsign} {time_str} {flight.parking} \nP 5 {traffic_points}")
    return file


def save_to_file(file_content_list, filename):
    # 打开文件以写入
    with open(filename, 'w') as f:
        # 逐行写入列表内容
        for line in file_content_list:
            f.write(line + '\n')  # 在每行内容后添加换行符


# def record_path(graph, path, pt, flight, file):
#     positions = calculate_positions(graph, path, pt)
#     traffic_points = ' '.join(f"{int(x)}.{int(y)}" for x, y in positions)
#
#     # 修改的逻辑部分，将内容添加到file列表中
#     if flight.departure == 'ZBTJ':
#         time_str = flight.ATOT
#         file.append(f"D {flight.callsign} {time_str} {flight.Parking} \nP 5 {traffic_points}")
#     else:
#         time_str = flight.ALDT
#         file.append(f"A {flight.callsign} {time_str} {flight.Parking} \nP 5 {traffic_points}")
#
#     return file
