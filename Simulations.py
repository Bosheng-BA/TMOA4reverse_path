

def calculate_positions(graph, path, pt,interval=5):
    positions = []
    total_time = 0  # 总时间累加器

    for i in range(1, len(path)):
        segment_start = path[i - 1]
        segment_end = path[i]
        positions.append(segment_start)
        # segment_distance = np.linalg.norm(np.array(segment_end) - np.array(segment_start))
        # segment_speed = graph.get_speed(segment_start, segment_end)
        taxiing, wait = pt[segment_end]
        if wait != 0:
            segment_time = taxiing - wait
            # total_time += wait
        else:
            segment_time = pt[segment_end][0]  # 当前段路径需要的时间
        # 计算当前段内每个5秒间隔的位置
        while total_time + interval <= taxiing:
            if total_time + interval < wait:
                total_time += interval
                positions.append(segment_start)
            else:
                total_time += interval
                ratio = total_time / segment_time
                new_position = (segment_start[0] + ratio * (segment_end[0] - segment_start[0]),
                                segment_start[1] + ratio * (segment_end[1] - segment_start[1]))
                positions.append(new_position)
        # 剩余时间累加到下一段的时间中
        total_time -= taxiing
    return positions



def record_path(graph, path, pt, file):
    positions = calculate_positions(graph, path, pt)
    traffic_points = ' '.join(f"{int(x)}.{int(y)}" for x, y in positions)

    # 修改的逻辑部分
    if plane_data['departure'] == 'ZBTJ':
        time_str = plane_data['ATOT']
        print(f"D {plane_data['callsign']} {time_str} {plane_data['Parking']} \nP 5 {traffic_points}")
    elif plane_data['arrival'] == 'ZBTJ':
        time_str = plane_data['ALDT']
        print(f"A {plane_data['callsign']} {time_str} {plane_data['Parking']} \nP 5 {traffic_points}")

    return file