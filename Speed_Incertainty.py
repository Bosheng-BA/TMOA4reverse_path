import gaptraffic
import Cst
import numpy as np
import random

flight_file_name_list = Cst.flight_file_name
flights = gaptraffic.read_flights(flight_file_name_list)

# 获取 flights 的数量 n
n = len(flights)
n = 810

# 定义速度变化的可能值
speed_changes = [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3]

# 生成 1*n 的矩阵，其中每个元素是从 speed_changes 中随机选择的值
speed_matrix = np.array([[1 - random.choice(speed_changes) for _ in range(n)]])

# 将矩阵保存到文件
output_file = "speed_changes_matrix.txt"
np.savetxt(output_file, speed_matrix, fmt="%.2f", delimiter=",")

print(f"矩阵已保存到 {output_file}")


