import os
import os.path
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column
from bokeh.models import Slider, Button
import Cst
import matplotlib.pyplot as plt


# 可视化路网寻路的过程
def create_matplotlib_figure(graph, path, stand, runway, flightnum, turn_lines):
    # 创建保存图像的文件夹
    # save_dir = 'new_QPPTW_saved_figures_2019-08-07-new-考虑修改时间窗'
    # save_dir = 'Draw/TEST-' + Cst.file + '/' + str(Cst.weight)
    save_dir = 'Draw/TEST-0828-2' + Cst.file
    # path = []
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 创建一个新的figure对象
    fig, ax = plt.subplots(figsize=(18, 12))

    # 绘制线路
    for node, connections in graph.items():
        for connection in connections:
            # print(connection[-1])
            point1 = node
            point2 = connection[-1]
            # print(point1, point2)
            if point2 == (21057, 9026) and point1 == (24108, 9026):
                ax.plot([point1[0], point2[0]], [point1[1], point2[1]], color='black', linewidth=3.5)
            elif point2 == (20155, 6926) and point1 == (23610, 6926):
                ax.plot([point1[0], point2[0]], [point1[1], point2[1]], color='black', linewidth=3.5)
            else:
                ax.plot([point1[0], point2[0]], [point1[1], point2[1]], color='gray')

    # 绘制节点
    for node in graph.keys():
        ax.scatter(node[0], node[1], color='gray', s=10)

    # Draw the source point and the target point
    if path:
        ax.scatter(path[0][0], path[0][1], color='red', s=60)
        ax.scatter(path[-1][0], path[-1][1], color='green', s=60)

    added_red_label = False
    added_blue_label = False

    for i in range(1, len(path)):
        current_vertex = path[i - 1]
        next_vertex = path[i]
        edge = (current_vertex, next_vertex)
        if edge in turn_lines:
            path_x = [point[0] for point in edge]
            path_y = [point[1] for point in edge]
            if not added_red_label:
                ax.plot(path_x, path_y, color='red', linewidth=2, label='Turn Line')
                added_red_label = True
            else:
                ax.plot(path_x, path_y, color='red', linewidth=2)

        else:
            path_x = [point[0] for point in edge]
            path_y = [point[1] for point in edge]
            if not added_blue_label:
                ax.plot(path_x, path_y, color='blue', linewidth=2, label='Straight Line')
                added_blue_label = True
            else:
                ax.plot(path_x, path_y, color='blue', linewidth=2)

        # 绘制特殊想查看的线路
        # pll = [(22622, 8111), (22622, 8107)]
        # for i in range(1, len(pll)):
        #     current_vertex = pll[i - 1]
        #     next_vertex = pll[i]
        #     pl = [current_vertex, next_vertex]
        #     ax.plot([pl[0][0], pl[1][0]], [pl[0][1], pl[1][1]], color='green', linewidth=3.5)


    # path = [(0, 0), (100, 0), (200, 0)]
    # 绘制最后得到的路径
    # path_x = [point[0] for point in path]
    # path_y = [point[1] for point in path]
    # # print(path_y)
    # ax.plot(path_x, path_y, color='blue', label="Final Path", linewidth=2)

    # 设置图例和标题
    plt.legend()
    plt.title("Matplotlib Animation")

    # 使用stand和runway作为文件名的一部分
    filename = f'flight_{flightnum}_stand_{stand}_runway_{runway}_{Cst.weight}.png'
    save_path = os.path.join(save_dir, filename)

    # 保存图像
    plt.savefig(save_path)
    # plt.show()

    # 关闭图像，以免占用过多资源
    plt.close(fig)

# network = {(0, 0): {(100, 0):100, (0, 100):100}, (100, 0): {(200, 0):200}, (0, 100): {(0, 200):100}}
# pointcoordlist = [(0, 0), (100, 0), (200, 0), (0, 100), (0, 200)]
# create_matplotlib_figure(network, pointcoordlist)


# 圆形障碍物情况
def create_bokeh_animation_with_path(network_point, network, pointcoordlist, t, v, path, pathpoint):
    output_file("bokeh_animation_with_path.html")

    p = figure(title="Bokeh Animation", x_range=(20000, 26000), y_range=(6000, 9500), width=1200, height=600)

    for point, connections in network_point.items():
        for connected_point, _ in connections.items():
            p.line(
                x=[point[0], connected_point[0]],
                y=[point[1], connected_point[1]],
                line_color='gray', line_width=3
            )

    x_coords = [coord[0] for coord in pointcoordlist]
    y_coords = [coord[1] for coord in pointcoordlist]
    p.circle(x=x_coords, y=y_coords, size=5, color='blackgrey', legend_label="Nodes")

    path_cost = [0]
    for i in range(len(path) - 1):
        start_node, end_node = path[i], path[i + 1]
        distance = network[start_node][end_node]
        path_cost.append(path_cost[-1] + distance)

    path_x = [pathpoint[i][0] for i in range(len(pathpoint))]
    path_y = [pathpoint[i][1] for i in range(len(pathpoint))]
    path_source = ColumnDataSource(data=dict(x=[], y=[]))
    p.line(x='x', y='y', line_color='red', line_width=3, legend_label="Path", source=path_source)

    end_t = t * v
    slider = Slider(start=0, end=end_t, value=0, step=1, title="Time")

    # 使用JavaScript回调
    slider_callback = CustomJS(
        args=dict(slider=slider, path_source=path_source, path_x=path_x,
                  path_y=path_y, path_cost=path_cost, v=v), code="""
        const time = slider.value;

        // Update path based on current time
        const visible_x = [];
        const visible_y = [];
        for (let i = 0; i < path_cost.length - 1; i++) {
            if (time * v >= path_cost[i]) {
                visible_x.push(path_x[i]);
                visible_y.push(path_y[i]);
            if (i < path_cost.length - 2 && time * v < path_cost[i + 1]) {
                visible_x.push(path_x[i + 1]);
                visible_y.push(path_y[i + 1]);
               }
        }
    }

         // Check if the last point of the path should be visible
         if (time * v >= path_cost[path_cost.length - 1]) {
             visible_x.push(path_x[path_x.length - 1]);
             visible_y.push(path_y[path_y.length - 1]);
          }

        path_source.data = {x: visible_x, y: visible_y};
        path_source.change.emit();
    """)

    slider.js_on_change('value', slider_callback)

    button = Button(label="Reset")
    button_callback = CustomJS(args=dict(slider=slider, path_source=path_source), code="""
            slider.value = 0;

            path_source.data = {x: [], y: []};
        path_source.change.emit();
    """)
    button.js_on_click(button_callback)

    layout = column(p, slider, button)
    show(layout)


