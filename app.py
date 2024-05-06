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
# from utils_fuzzy import Logging
from operator import itemgetter

warnings.filterwarnings("ignore")
PATH = "C:/Users/Doan Duy Thanh/Desktop/sus/"
LOG_PATH = "logs"


arr_data = [
    ]
min_max_scaler = preprocessing.MinMaxScaler()

# 0 0.01 0.001

def preprocessing(name_file, att_nominal_cate):
    DS  = np.genfromtxt(name_file, delimiter=",", dtype=object)[:, :]
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


def split_data_icr(data, row_selected):
    arrs = []
    data_1 = data[:row_selected]
    data_2 = data[row_selected:]
    
    arrs.append(data_1)
    arrs.append(data_2)
    
    return arrs

    # arrs = []
    # arrs_2 = split_data(data, number=2)
    # arrs.append(arrs_2[0])
    # arrs_2[1] = split_data(arrs_2[1], number=1)
    # for arr in arrs_2[1]:
    #     arrs.append(arr)
    # return arrs


def main(arr_data):
    path = sys.argv[1]
    col = int(sys.argv[2])
    row = int(sys.argv[3])
    alpha = float(sys.argv[4])
    delta = float(sys.argv[5])
    row_selected = int(sys.argv[6])
    new_data = [path, [col-1], delta]
    # print("dap an", row_selected, delta)
    arr_data.append(new_data)
    start = time.time()
    a_sc = [["Data","|C|", "|R_F|", "Acc_O","std_O", "Acc_F", "std_F", "T_F", "Reduct", "Alpha"]]
    n_steps = 2
    B = []
    # F = []
    num_prev = 0
    dis_tg = 0
    
    X = [alpha]
    # Muc alpha
    # X = [0,0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1]
    # HH = []
    for arr in arr_data:
        for x in X:
            F = []
            DS = preprocessing(arr[0], arr[1])             
            st = time.time()
            DS = split_data_icr(DS,row_selected)
            # print(DS)
            # step 1: Compute IFPDs on original dataset.
            IF = IntuitiveFuzzy(DS[0], arr[0], arr[1], arr[2], x, F, num_prev, dis_tg)
            F, dis_tg, time_filter = IF.filter()
            print("F", F)
            sc = IF.evaluate(arr[0], F, time_filter)
            a_sc.append(sc)
            # os.system('cls')
            print (tabulate(a_sc, headers='firstrow', tablefmt='pipe', stralign='center'))
            # os.system('cls')
            U = DS[0]
            column_order = ["Reduct", "Size of the reduct", "Acc_O ± std_O", "Acc_F ± std_F", "Runtime", "Alpha"]            
            column_order = ["Reduct", "Size of the reduct", "Acc_O ± std_O", "Acc_F ± std_F", "Runtime", "Alpha"]            
            with open('output.txt', 'w') as f:
                f.write('\t'.join(column_order) + '\n')
                for i, row in enumerate(a_sc):  
                    if i >= 1: 
                        f.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(row[8], row[2], str(row[3]) + " ± " + str(row[4]), str(row[5]) + " ± " + str(row[6]), row[7], row[9]))





                               
        H = max(filter(lambda x: x[4], a_sc[1:]), key=itemgetter(1))
        # H = H.sorted(a_sc[1:], key=lambda x: x[2], reverse=True)
        H = max(a_sc[1:][::-1], key = lambda x: x[5])
        # H = max(a[4] for a in a_sc[1:])
        print(H)
        F = H[8]
        x = H[9]
        # B = np.copy(F)
        for i in range(1, n_steps):
            dU = DS[i]
            U = np.vstack((U, dU))
            num_delta = dU.shape[0]
            IF.update_dataset(U)
            IF.update_n_objs()
            IF.update_retional_matrices()
            IF.update_dis(dis_tg)
            IF = IntuitiveFuzzy(U, arr[0], arr[1], arr[2], x, F, num_delta, dis_tg)
            F, dis_tg, time_filter = IF.filter_incre()
            print("F", F)
            IF.update_n_attribute(F)
            sc = IF.evaluate(arr[0], F, time_filter)
            a_sc.append(sc)
            # os.system('cls')
            print (tabulate(a_sc, headers='firstrow', tablefmt='pipe', stralign='center'))
            # os.system('cls')
            # with open('output.txt', 'a') as f:
            #     for row in a_sc[1:]:
            #         f.write('\t'.join(map(str, row)) + '\n')

    

    print(time.time()-start)

if __name__ == "__main__":
    main(arr_data)