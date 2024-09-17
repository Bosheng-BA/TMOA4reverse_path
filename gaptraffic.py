import pandas as pd
import Sour_and_Des

Heavy = ["RH", "SH", "TH"]
Middle_and_Light = ["RM", "TM", "TL"]
Waiting = {
    "RH": {"TL": 3, "RM": 2, "TM": 2, "RH": 1, "SH": 1, "TH": 1},
    "SH": {"TL": 3, "RM": 2, "TM": 2, "RH": 1, "SH": 1, "TH": 1},
    "TH": {"TL": 3, "RM": 2, "TM": 2, "RH": 1, "SH": 1, "TH": 1},
    "RM": {"TL": 2, "RM": 1, "TM": 1, "RH": 1, "SH": 1, "TH": 1},
    "TM": {"TL": 2, "RM": 1, "TM": 1, "RH": 1, "SH": 1, "TH": 1},
    "TL": {"TL": 1, "RM": 1, "TM": 1, "RH": 1, "SH": 1, "TH": 1}
}


class Flight:
    def __init__(self, data, callsign, departure, arrivee, ttot, tldt, atot, aldt, type, wingspan, airline, qfu,
                 parking, registration, start_taxi_time):
        self.data = data
        self.callsign = callsign
        self.departure = departure
        self.arrivee = arrivee
        self.ttot = ttot
        self.tldt = tldt
        self.atot = atot
        self.aldt = aldt
        self.type = type
        self.wingspan = wingspan
        self.airline = airline
        self.qfu = qfu
        self.parking = parking
        self.registration = registration
        self.start_taxi_time = start_taxi_time


def squence_csv(df, airc_type_dict, a, b, c, d):
    # 创建一个空列表来存储Flight对象
    new_TTOT = {}
    # 创建新的列
    for i in range(len(df)):
        row = df.loc[i]
        if row['departure'] == 'ZBTJ':
            if airc_type_dict[row['Type']] in Middle_and_Light:
                new_TTOT[str(row['data'] + row['TLDT']) + row['callsign']] = row['TTOT'] + a
            else:
                new_TTOT[str(row['data'] + row['TLDT']) + row['callsign']] = row['TTOT'] + b
        else:
            if airc_type_dict[row['Type']] in Middle_and_Light:
                new_TTOT[str(row['data'] + row['TLDT']) + row['callsign']] = row['ALDT'] + c
            else:
                new_TTOT[str(row['data'] + row['TLDT']) + row['callsign']] = row['ALDT'] + d

    df['start_taxi_time'] = df.apply(lambda row: new_TTOT[str(row['data'] + row['TLDT']) + row['callsign']], axis=1)
    df_new = df.sort_values(by='start_taxi_time')
    return df_new


def read_flights(files_name):
    # 读取Excel文件
    df = pd.read_csv(files_name)
    airc_type_dict = Sour_and_Des.airc_type_dict

    # 创建一个空列表来存储Flight对象
    flights = []

    # df_new = squence_csv(df, airc_type_dict, 60-600, 120-600, -60, -120)
    df_new = squence_csv(df, airc_type_dict, -600, -600, 0, 0)
    df_new.to_csv(files_name + "0000000.csv", index=False)

    df2 = pd.read_csv(files_name + "0000000.csv")
    for i, row in df2.iterrows():
        for j in range(0, i):
            row1 = df2.loc[j]
            wt = Waiting[airc_type_dict[row1['Type']]][airc_type_dict[row['Type']]] * 60
            flight_t2 = row1['TTOT'] if row1['departure'] == 'ZBTJ' else row1['ALDT']

            if row['departure'] == 'ZBTJ' and row['TTOT'] - flight_t2 < wt:
                df2.at[i, 'TTOT'] += wt
            elif row['arrivee'] == 'ZBTJ' and row['ALDT'] - flight_t2 < wt:
                df2.at[i, 'ALDT'] += wt

        # if row['departure'] == 'ZBTJ' and i >= 1:
        #     for j in range(0, i):
        #         row1 = df2.loc[j]
        #         wt = Waiting[airc_type_dict[row1['Type']]][airc_type_dict[row['Type']]] * 60
        #         if row1['departure'] == 'ZBTJ' and row['TTOT'] - row1['TTOT'] < wt:
                    # print(type(row1['Parking']), row1['Parking'])
                    # print(type(row['Parking']), row['Parking'])
                    # if row1['Parking'][0] == row['Parking'][0] and row1['Parking'][1] == row['Parking'][1]:
                    # if str(row1['Parking'])[:2] == str(row['Parking'])[:2]:
                    #     df2.loc[i, 'TTOT'] += wt
                    # elif str(row1['Parking'])[:1] == str(row['Parking'])[:1]:
                    #     df2.loc[i, 'TTOT'] += wt
                    # if str(row1['Parking'])[:1] == str(row['Parking'])[:1]:
                    # df2.loc[i, 'TTOT'] += wt
                    # df2.loc[i, 'TTOT'] += 0
                    # if str(row1['Parking'])[:1] == str(row['Parking'])[:1]:
                    #     df2.loc[i, 'TTOT'] += wt

    df_sorted = squence_csv(df2, airc_type_dict, -600, -600, 0, 0)
    # df_sorted = squence_csv(df2, airc_type_dict, 60-600, 120-600, -60, -120)
    df_sorted['QFU'] = '16R'
    df_sorted.to_csv(files_name + "sorted_file.csv", index=False)

    for index, row in df_sorted.iterrows():
        flight = Flight(row['data'], row['callsign'], row['departure'], row['arrivee'], row['TTOT'], row['TLDT'],
                        row['ATOT'], row['ALDT'], row['Type'], row['Wingspan'], row['Airline'],
                        row['QFU'], row['Parking'], row['registration'], row['start_taxi_time'])
        flights.append(flight)
    return flights
