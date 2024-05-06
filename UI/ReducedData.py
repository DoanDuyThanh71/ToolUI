


from multiprocessing import process
from PyQt6 import QtCore, QtGui, QtWidgets
import subprocess
import csv

    
class Ui_ReducedData(object):
    
    def importData(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Import Data", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file)
                data = list(csv_reader)
            
            if data:
                headers = data[0]
                num_rows = len(data) - 1
                num_cols = len(headers)

                decision_classes = set(row[-1] for row in data[1:])
                num_decision_classes = len(decision_classes)

                self.data = data
                self.tabAns.setColumnCount(num_cols)
                self.tabAns.setRowCount(num_rows)
                self.tabAns.setHorizontalHeaderLabels(map(str, headers))
                for row_idx, row_data in enumerate(data[1:]):
                    for col_idx, cell_value in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(str(cell_value))
                        self.tabAns.setItem(row_idx, col_idx, item)
                
                self.labInfor.setText(f"Data imported successfully.\nRows: {num_rows}\nColumns: {num_cols}\nDecision Classes: {num_decision_classes}")
            else:
                self.labInfor.setText("No file selected.")
    
    
    
    def run_app(self):
        subprocess_process = subprocess.Popen(["python", "app.py"])
    
        subprocess_process.wait()
        self.tabAns.setRowCount(0)
        self.tabAns.setColumnCount(10)
        with open('output.txt', 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row_idx, row in enumerate(reader):
                self.tabAns.insertRow(row_idx)
                for col_idx, cell_value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(cell_value))
                    self.tabAns.setItem(row_idx, col_idx, item)

    
        

    
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(1032, 616)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(mainWindow.sizePolicy().hasHeightForWidth())
        mainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.btnImportData = QtWidgets.QPushButton(parent=self.centralwidget, clicked= lambda: self.importData())
        self.btnImportData.setGeometry(QtCore.QRect(40, 40, 251, 23))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.btnImportData.setFont(font)
        self.btnImportData.setObjectName("btnImportData")
        self.btnProcess = QtWidgets.QPushButton(parent=self.centralwidget, clicked = lambda : self.run_app())
        self.btnProcess.setGeometry(QtCore.QRect(690, 40, 301, 23))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.btnProcess.setFont(font)
        self.btnProcess.setObjectName("btnProcess")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(40, 90, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(40, 140, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.ledAlpha = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.ledAlpha.setGeometry(QtCore.QRect(160, 90, 131, 20))
        self.ledAlpha.setObjectName("ledAlpha")
        self.ledSelectedRow = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.ledSelectedRow.setGeometry(QtCore.QRect(160, 140, 131, 20))
        self.ledSelectedRow.setObjectName("ledSelectedRow")
        self.labInfor = QtWidgets.QLabel(parent=self.centralwidget)
        self.labInfor.setGeometry(QtCore.QRect(690, 80, 301, 81))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.labInfor.setFont(font)
        self.labInfor.setText("")
        self.labInfor.setObjectName("labInfor")
        self.tabAns = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tabAns.setGeometry(QtCore.QRect(30, 190, 991, 381))
        self.tabAns.setObjectName("tabAns")
        self.tabAns.setColumnCount(0)
        self.tabAns.setRowCount(0)
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1032, 21))
        self.menubar.setObjectName("menubar")
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=mainWindow)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "MainWindow"))
        self.btnImportData.setText(_translate("mainWindow", "Import Data"))
        self.btnProcess.setText(_translate("mainWindow", "Process"))
        self.label.setText(_translate("mainWindow", "Mức Alpha"))
        self.label_2.setText(_translate("mainWindow", "Số dòng chọn"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_ReducedData()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec())
