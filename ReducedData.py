from multiprocessing import process
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from Dialog import ErrorDialog
import subprocess
import csv
import sys

    
class Ui_ReducedData(object):
    def __init__(self) -> None:
        self.path = None 
        self.col = None
        self.row = None
        self.delta = None
        
    def importData(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Import Data", "", "CSV Files (*.csv)")
        self.path = file_path
        if file_path:
            file_name = os.path.basename(file_path)
            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file)
                data = list(csv_reader)
            if data:
                headers = data[0]
                num_rows = len(data) - 1
                num_cols = len(headers)
                self.col = num_cols
                self.row = num_rows
                decision_classes = set(row[-1] for row in data[1:])
                num_decision_classes = len(decision_classes)
                self.data = data
                self.tabAns.setColumnCount(num_cols)
                self.tabAns.setRowCount(num_rows)
                self.tabAns.setHorizontalHeaderLabels(map(str, headers))
                for row_idx, row_data in enumerate(data[1:]):
                    for col_idx, cell_value in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(str(cell_value))
                        # Set font and background color for cells
                        item.setFont(QtGui.QFont("Arial", 10))
                        item.setBackground(QtGui.QColor(240, 240, 240))
                        self.tabAns.setItem(row_idx, col_idx, item)
                self.labInfor.setText(f"Data imported successfully from file: \n{file_name}.\nRows: {num_rows}\nColumns: {num_cols}\nDecision Classes: {num_decision_classes}")
                self.labInfor.resize(num_rows, num_cols)
                # self.labInfor.setText(f"Data imported successfully.\nRows: {num_rows}\nColumns: {num_cols}\nDecision Classes: {num_decision_classes}")
                self.tabAns.resizeColumnsToContents()
            else:
                self.labInfor.setText("No file selected.")
            self.tabAns.resizeColumnsToContents()

    def run_app(self):
        alpha_text = self.ledAlpha.text()
        if not self.path:
            error_dialog = ErrorDialog("")
            error_dialog.show_error("No file selected. Please import a CSV file.")
            return
        if not alpha_text:
            error_dialog = ErrorDialog("")
            error_dialog.show_error("Please enter the value of alpha.")
            return

        try:
            alpha = float(alpha_text)
            if not 0 <= alpha <= 1:
                error_dialog = ErrorDialog("")
                error_dialog.show_error("The value of alpha is not within the range from 0 to 1.")
                return
        except ValueError:
            error_dialog = ErrorDialog("")
            error_dialog.show_error("The value of alpha is invalid.")
            return

        delta_text = self.delta.currentText()

        row_selected_text = self.ledSelectedRow.text()
        if not row_selected_text:
            error_dialog = ErrorDialog("")
            error_dialog.show_error("Please enter the number of the selected row..")
            return

        try:
            row_selected = int(row_selected_text)
            row = int(self.row)
            if row_selected <= 0 or row_selected > row:
                error_dialog = ErrorDialog("")
                error_dialog.show_error(f"The selected row is invalid.")
                return
        except ValueError:
            error_dialog = ErrorDialog("")
            error_dialog.show_error("The value of the selected row is invalid.")
            return

        delta = float(self.delta.currentText())
        subprocess_process = subprocess.Popen(["python", "app.py", str(self.path), str(self.col), str(self.row), str(alpha), str(delta),str(row_selected)])
        with open('dataAdd.txt', 'w') as f:
            f.write(f"{self.path}, {self.col}, {self.row}, {alpha}\n")
        subprocess_process.wait()
        
        self.tabAns.setRowCount(0)
        with open('output.txt', 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            column_names = next(reader)
            self.tabAns.setColumnCount(len(column_names))
            self.tabAns.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row in enumerate(reader):
                self.tabAns.insertRow(row_idx)
                for col_idx, cell_value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(cell_value))
                    item.setFont(QtGui.QFont("Arial", 10))
                    item.setBackground(QtGui.QColor(240, 240, 240))
                    self.tabAns.setItem(row_idx, col_idx, item)
        num_columns = self.tabAns.columnCount()

        for col_idx in range(num_columns):
            header_item = self.tabAns.horizontalHeaderItem(col_idx)
            if header_item is not None:
                font = QtGui.QFont()
                font.setBold(True)
                header_item.setFont(font)
        self.tabAns.resizeColumnsToContents()



        
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(1300, 616)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(mainWindow.sizePolicy().hasHeightForWidth())
        mainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Button to import data
        self.btnImportData = QtWidgets.QPushButton(parent=self.centralwidget, clicked=lambda: self.importData())
        self.btnImportData.setGeometry(QtCore.QRect(40, 40, 251, 23))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.btnImportData.setFont(font)
        self.btnImportData.setObjectName("btnImportData")
        
        # Button to process
        self.btnProcess = QtWidgets.QPushButton(parent=self.centralwidget, clicked=lambda: self.run_app())
        self.btnProcess.setGeometry(QtCore.QRect(950, 40, 301, 23))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.btnProcess.setFont(font)
        self.btnProcess.setObjectName("btnProcess")
        
        # Label and Line Edit for Alpha
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(40, 90, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.ledAlpha = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.ledAlpha.setGeometry(QtCore.QRect(160, 90, 131, 20))
        self.ledAlpha.setObjectName("ledAlpha")
        
        # Label and Line Edit for Selected Row
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(40, 140, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.ledSelectedRow = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.ledSelectedRow.setGeometry(QtCore.QRect(160, 140, 131, 20))
        self.ledSelectedRow.setObjectName("ledSelectedRow")
        
        # Combo Box for selecting values
        self.delta = QtWidgets.QComboBox(parent=self.centralwidget)
        self.delta.setGeometry(QtCore.QRect(160, 190, 131, 20))
        self.delta.setObjectName("delta")
        self.delta.addItem("")
        self.delta.addItem("")
        self.delta.addItem("")
        
        self.labelDelta = QtWidgets.QLabel(parent=self.centralwidget)
        self.labelDelta.setGeometry(QtCore.QRect(40, 190, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.labelDelta.setFont(font)
        self.labelDelta.setObjectName("labelDelta")
        self.labelDelta.setText("Delta")
        
        # Information Label
        self.labInfor = QtWidgets.QLabel(parent=self.centralwidget)
        self.labInfor.setGeometry(QtCore.QRect(950, 80, 301, 81))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.labInfor.setFont(font)
        self.labInfor.setText("")
        self.labInfor.setObjectName("labInfor")
        
        # Table Widget
        self.tabAns = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tabAns.setGeometry(QtCore.QRect(30, 240, 1240, 341))
        self.tabAns.setObjectName("tabAns")
        self.tabAns.setColumnCount(0)
        self.tabAns.setRowCount(0)
        
        # Setting up the main window
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
        self.label.setText(_translate("mainWindow", "Alpha Level"))
        self.label_2.setText(_translate("mainWindow", "Rows Selected"))
        self.delta.setItemText(0, _translate("mainWindow", "0"))
        self.delta.setItemText(1, _translate("mainWindow", "0.1"))
        self.delta.setItemText(2, _translate("mainWindow", "0.01"))
        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_ReducedData()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec())