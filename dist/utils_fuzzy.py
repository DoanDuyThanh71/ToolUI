import statistics 
from operator import itemgetter


class Logging(object):
    def __init__(self, file_path):
        self.file_path = file_path
        
    def write_line(self, line):
        with open(self.file_path, 'a') as f:
            f.write(line+'\n')

    def logging_fuzzy(self, sc):
        log_size_f = str(sc[2])
        log_size_w = str(sc[3])
        log_acc_o = str(sc[4])
        log_acc_f = str(sc[5])
        log_acc_w = str(sc[6])
        log_time_f = str(sc[7])
        log_time_w = str(sc[8])

        return log_size_f, log_size_w, log_acc_o, log_acc_f, log_acc_w, log_time_f, log_time_w