import os
# 打开并读取文件
weight = [1, 0]
file = '20170803_ZBTJ-PN_MANEX.csv'
# file = 'gaptraffic-2017-08-03-new.csv'
DATA_PATH = "Datas/DATA"
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")

airc_file_name = "Datas/traffic/acft_types.txt"

flight_file_name = "Datas/traffic/" + file

# flight_file_name_list = ['gaptraffic-2017-08-03-new.csv','gaptraffic-2017-08-06-new.csv',
#                          'gaptraffic-2017-08-14-new.csv','gaptraffic-2017-08-17-new.csv',
#                          'gaptraffic-2017-08-19-new.csv','gaptraffic-2018-07-18-new.csv',
#                          'gaptraffic-2018-07-29-new.csv','gaptraffic-2018-09-29-new.csv',
#                          'gaptraffic-2019-02-01-new.csv','gaptraffic-2019-08-07-new.csv',]
flight_file_name_list = ['20170803_ZBTJ-PN_MANEX.csv','20170806_ZBTJ-PN_MANEX.csv',
                         '20170814_ZBTJ-PN_MANEX.csv','20170817_ZBTJ-PN_MANEX.csv',
                         '20170819_ZBTJ-PN_MANEX.csv','20180718_ZBTJ-PN_MANEX.csv',
                         '20180729_ZBTJ-PN_MANEX.csv','20180929_ZBTJ-PN_MANEX.csv',
                         '20190201_ZBTJ-PN_MANEX.csv','20190807_ZBTJ-PN_MANEX.csv',]

# 存储文件的位置
# file = 'gaptraffic-2019-08-07-new'
# 确保目录存在
# os.makedirs(file, exist_ok=True)