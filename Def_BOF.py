class Path(object):
    """Path description"""

    def __init__(self, flight, arrive, S, E, length, time_cost, fuel_cost, point, BOT, TOF, TTOF, check):
        self.flight = flight  # Which flight/flightnum
        self.arrive = arrive
        self.length = length  # The length of the path
        self.fuel_cost = fuel_cost  # The path's fuel cost
        self.time_cost = time_cost  # time
        self.point = point  # Path's points
        self.BOT = BOT  # Block off time
        self.TOF = TOF
        self.TTOF = TTOF  # Target takeoff time
        self.S = S  # The start point
        self.E = E  # The end point
        self.check = check

    # def get_BOF(self):
    #     # path, COST, holding_time = MOA.AMOA_star(source, target, costs, graph_copy, time_windows, start_time,
    #     #                                          out_angles,
    #     #                                          in_angles, Stand, weights, cost_of_path, W)

    def get_check(self):
        if self.arrive != 'ZBTJ':
            if self.time_cost + self.BOT == self.TTOF:
                self.check = True
            elif abs(self.time_cost + self.BOT - self.TTOF) >= 5:
                # print("YES")
                self.BOT = self.BOT - (self.time_cost + self.BOT - self.TTOF)
                self.check = False
                # 再次寻路
            else:
                self.check = True


# flight = 0
# S = {"S": (0, 0)}
# E = {"E": (0, 0)}
# length = 0
# time_cost = 0
# fuel_cost = 0
# point = []
# BOT = 0
# TTOF = 0
# paths = []
#
# path = Path(flight, S, E, length, time_cost, fuel_cost, point, BOT, TTOF)
# paths.append(path)
#
# for path in paths:
#     if path.time_cost + path.BOT == path.TTOF:
#         break
#     elif abs(path.time_cost + path.BOT - path.TTOF) >= 5:
#         path.BOT = path.BOT - (path.time_cost + path.BOT - path.TTOF)
#         # 再次寻路
#     else:
#         break

        # path.time_cost + path.BOT - path.TTOF > 5
