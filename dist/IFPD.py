import numpy as np

from intuition_fuzzy3 import IntuitiveFuzzy
from sklearn.preprocessing import LabelEncoder
from sklearn import preprocessing
from tabulate import tabulate
import warnings, os, time
from sklearn.model_selection import KFold
import sys
from operator import itemgetter
from utils_fuzzy import Logging
from operator import itemgetter

warnings.filterwarnings("ignore")
PATH = "C:/Users/Doan Duy Thanh/Desktop/FW_ICIFPD2_DEL/"
LOG_PATH = "logs"

arr_data = []

min_max_scaler = preprocessing.MinMaxScaler()



def preprocessing(name_file, att_nominal_cate):
    DS = np.genfromtxt(name_file, delimiter=",", dtype=object)[:, :]
    att = DS[0].astype(int)
    
    att_nominal_cate = np.array(att_nominal_cate)
    att_real = np.setdiff1d(att, att_nominal_cate)

    DS[0] = att
    
    #list_index_cate = [list(DS[0]).index(i) for i in att_nominal_cate]
    for i in att_nominal_cate:
        DS[1:, i] = LabelEncoder().fit_transform(DS[1:,i])

    DS[1:,:] = DS[1:,:]
    #if len(att_real) > 0 :
        #list_index_real = [list(DS[0]).index(i) for i in att_real]
    DS[1:,att_real] = min_max_scaler.fit_transform(DS[1:,att_real])
    return DS[1:]

def split_data(data, number: int = 1, start_fold: int=1):
    if number == 1:
        return [data]
    ldt = len(data)
    spt = int(ldt / number)
    blk = spt * number
    n_indices = number-start_fold+1
    split_indices = np.arange(ldt, ldt-spt*n_indices, -spt)
    return split_indices

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
    dis_tg_B = float(data_line[9])
    dis_tg_C = float(data_line[10])
    return F, x, dis_tg, row, dis_tg_B, dis_tg_C


def main(arr_data):
    
    path = sys.argv[1]
    col = int(sys.argv[2])
    row_selected = int(sys.argv[3])
    delta = float(sys.argv[4])
    new_data = [path, [col - 1], delta]
    arr_data.append(new_data)
    
    start = time.time()
    a_sc = [["Data","|C|", "|R_F|", "Acc_O","std_O", "Acc_F", "std_F", "T_F", "Reduct", "alpha"]]
    B = []
    # F = []
    num_prev = 0
    dis_tg_C = 0
    dis_tg_B = 0
    # max_dis
    X = [0.8]
    # X = [0,0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1]
    # HH = []
    for arr in arr_data:
        for x in X:
            F = []
            DS = preprocessing(arr[0], arr[1])
            file_name = os.path.splitext(os.path.basename(arr[0]))[0] + "_output.txt"
            # st = time.time()
            # split_indices = split_data(DS, number=10, start_fold=5)
            # print(split_indices)
            # split_indice = split_indices[0]
            # print("ABCD", split_indice)
            # # step 1: Compute IFPDs on original dataset.
            # IF = IntuitiveFuzzy(DS, split_indice, arr[0], arr[1], arr[2], x, F, num_prev, dis_tg_C, dis_tg_B)
            # F, dis_tg_C, dis_tg_B, time_filter = IF.filter()
            # print("F", F)
            # sc = IF.evaluate(arr[0], F, time_filter)
            # a_sc.append(sc)
            # # os.system('cls')
            # print (tabulate(a_sc, headers='firstrow', tablefmt='pipe', stralign='center'))
            F, x, dis_tg, row, dis_tg_B, dis_tg_C = read_file(file_name)

        # H = max(a_sc[1:][::-1], key = lambda x: x[5])
        # # H = max(a[4] for a in a_sc[1:])
        # print(H)
        # F = H[8]
        # x = H[9]
        # IF.update_dis(dis_tg)
        # B = np.copy(F)
        # for i in range(1, n_steps):
            # split_indice = split_indices[i]
            # print("ht", split_indices[i])
            # print("QK", split_indices[i-1])
            # print("DIS C", dis_tg_C)
            # print("DIS B", dis_tg_B)
        IF = IntuitiveFuzzy(DS, row_selected, arr[0], arr[1], arr[2], x, F, row , dis_tg_C, dis_tg_B)
        F, dis_tg_C, dis_tg_B, time_filter = IF.filter_incre()
        
        sc = IF.evaluate(arr[0], F, time_filter)
        a_sc.append(sc)
        # print (tabulate(a_sc, headers='firstrow', tablefmt='pipe', stralign='center'))
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
    

    # print(time.time()-start)

if __name__ == "__main__":
    main(arr_data)

