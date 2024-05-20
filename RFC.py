import sys
import numpy as np

from intuition_fuzzy2 import IntuitiveFuzzy
from sklearn.preprocessing import LabelEncoder
from sklearn import preprocessing
from tabulate import tabulate
import warnings, os, time
from sklearn.model_selection import KFold
import statistics
from operator import itemgetter

warnings.filterwarnings("ignore")
PATH = "C:/Users/Doan Duy Thanh/Desktop/sus/"
LOG_PATH = "logs"

arr_data = []
min_max_scaler = preprocessing.MinMaxScaler()


def preprocessing(name_file, att_nominal_cate):
    DS = np.genfromtxt(name_file, delimiter=",", dtype=object)[:, :]
    att = DS[0].astype(int)
    att_nominal_cate = np.array(att_nominal_cate)
    att_real = np.setdiff1d(att, att_nominal_cate)
    DS[0] = att
    for i in att_nominal_cate:
        DS[1:, i] = LabelEncoder().fit_transform(DS[1:, i])
    DS[1:, att_real] = min_max_scaler.fit_transform(DS[1:, att_real])
    return DS[1:]


def split_data_icr(data, row_selected):
    data_1 = data[:row_selected]
    data_2 = data[row_selected:]
    return [np.array(data_1), np.array(data_2)]


def read_file(file_name):
    with open(file_name, "r") as f:
        lines = f.readlines()
    data_line = lines[1]
    arr_str = data_line.split("[")[1].split("]")[0].split(", ")
    F = [int(x) for x in arr_str]
    data_line = lines[1].split("\t")
    x = float(data_line[5])
    dis_tg = float(data_line[6])
    row = int(data_line[7])
    return F, x, dis_tg, row


def main(arr_data):
    path = sys.argv[1]
    col = int(sys.argv[2])
    row_selected = int(sys.argv[3])
    delta = float(sys.argv[4])
    new_data = [path, [col - 1], delta]
    arr_data.append(new_data)

    start = time.time()
    a_sc = [
        [
            "Data",
            "|C|",
            "|R_F|",
            "Acc_O",
            "std_O",
            "Acc_F",
            "std_F",
            "T_F",
            "Reduct",
            "Alpha",
        ]
    ]
    n_steps = 2
    num_prev = 0
    dis_tg = 0
    X = [1]

    for arr in arr_data:
        for x in X:
            F = []
            DS = preprocessing(arr[0], arr[1])
            file_name = os.path.splitext(os.path.basename(arr[0]))[0] + "_output.txt"

            # with open(file_name, 'r') as f:
            #     lines = f.readlines()
            # data_line = lines[1]
            # arr_str = data_line.split("[")[1].split("]")[0].split(", ")
            # F = [int(x) for x in arr_str]
            # data_line = lines[1].split("\t")
            # x = float(data_line[5])
            # dis_tg = float(data_line[6])
            F, x, dis_tg, row = read_file(file_name)

            st = time.time()
            H = []

            DS = split_data_icr(DS, row_selected + row)
            U = np.vstack(DS)

            # IF = IntuitiveFuzzy(DS[0], arr[0], arr[1], arr[2], x, F, num_prev, dis_tg)

            num_delta = row_selected
            # IF.update_dataset(U)
            # IF.update_n_objs()
            # IF.update_retional_matrices()
            # IF.update_dis(dis_tg)
            IF = IntuitiveFuzzy(U, arr[0], arr[1], arr[2], x, F, num_delta, dis_tg)
            F, dis_tg, time_filter = IF.filter_incre()
            print("F", F)
            IF.update_n_attribute(F)
            sc = IF.evaluate(arr[0], F, time_filter)
            a_sc.append(sc)
            print(
                tabulate(a_sc, headers="firstrow", tablefmt="pipe", stralign="center")
            )
            column_order = [
                "Reduct",
                "Size of the reduct",
                "Acc_O ± std_O",
                "Acc_F ± std_F",
                "Runtime",
                "Alpha",
                "Dis_Tg",
                "Row_select",
                "Delta"
            ]

            with open(file_name, 'a') as f:
                for i, row in enumerate(a_sc):
                    if i >= 1:  # Bỏ qua tiêu đề
                        f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                            row[8], row[2], str(row[3]) + " ± " + str(row[4]),
                            str(row[5]) + " ± " + str(row[6]), row[7],
                            row[9], dis_tg, row_selected, delta
                        ))

    print(time.time() - start)


if __name__ == "__main__":
    main(arr_data)
