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
