from multiprocessing import process
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from UI_Dialog import ErrorDialog
import subprocess
import csv
import sys
from UI_ProgressDialog import ProgressDialog


class Worker(QtCore.QThread):
    finished = QtCore.pyqtSignal()

    def __init__(self, path, col, row_selected, delta):
        super().__init__()
        self.path = path
        self.col = col
        self.row_selected = row_selected
        self.delta = delta

    def run(self):
        command =  [
                "python",
                "IFPD.py",
                str(self.path),
                str(self.col),
                str(self.row_selected),
                str(self.delta),
            ]
        
        subprocess_process = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess_process.wait()  # Chờ cho quá trình kết thúc
        self.finished.emit()
        
class Ui_Reinforcement(object):
    def __init__(self) -> None:
        self.path = None
        self.col = None
        self.row = None
        self.delta = None
        self.row_selected = 0
    def go_back(self):
        from UI_Home import Ui_MainWindow

        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.show()
        QtCore.QTimer.singleShot(
            0, QtWidgets.QApplication.instance().activeWindow().close
        )

    def importData(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Import Data", "", "CSV Files (*.csv)"
        )
        self.path = file_path
        if file_path:
            # Kiểm tra xem file output đã tồn tại hay không
            file_name = os.path.splitext(file_path)[0] + "_output.txt"
            if os.path.exists(file_name):
                with open(file_name, "r") as f:
                    lines = f.readlines()
                data_line = lines[1].split("\t")
                self.delta.setText(str(data_line[8]))
                self.ledAlpha.setText(str(data_line[5]))
                x = float(data_line[5])
                self.delta = float(data_line[8])

                data = []
                file_name = os.path.basename(file_path)
                with open(file_path, "r") as file:
                    csv_reader = csv.reader(file)
                    data = list(csv_reader)

                if data:
                    headers = data[0]
                    num_rows = len(data) - 1
                    num_rows_View = len(data) - 1
                    num_cols = len(headers)
                    self.col = num_cols
                    self.row = int(data_line[7])
                    decision_classes = set(row[-1] for row in data[1:])
                    num_decision_classes = len(decision_classes)
                    self.data = data
                    self.tabAns.setHorizontalHeaderLabels(map(str, headers))
                    self.labInfor.setText(
                        f"Data imported successfully from file: \n{file_name}.\nRows: {num_rows}\nColumns: {num_cols}\nDecision Classes: {num_decision_classes}"
                    )
                    # self.labInfor.setText(f"Data imported successfully.\nRows: {num_rows}\nColumns: {num_cols}\nDecision Classes: {num_decision_classes}")
                    self.tabAns.resizeColumnsToContents()

                else:
                    self.labInfor.setText("No file selected.")
                self.tabAns.resizeColumnsToContents()

            else:
                error_dialog = ErrorDialog("")
                error_dialog.show_error("File not found")

    def run_app(self):

        progress_dialog = ProgressDialog()
        progress_dialog.show()

        if not self.path:
            error_dialog = ErrorDialog("")
            error_dialog.show_error("No file selected. Please import a CSV file.")
            return

        row_selected_text = self.ledSelectedRow.text()
        if not row_selected_text:
            error_dialog = ErrorDialog("")
            error_dialog.show_error("Please enter the number of the selected row.")
            return

        try:
            row_selected = int(row_selected_text)
            self.row_selected = row_selected
            row = int(self.row)
            data = self.data
            if row_selected <= 0 or row_selected > len(data) - 1 - row:
                error_dialog = ErrorDialog("")
                error_dialog.show_error(f"The selected row is invalid.")
                return
        except ValueError:
            error_dialog = ErrorDialog("")
            error_dialog.show_error("The value of the selected row is invalid.")
            return
        self.worker = Worker(self.path, self.col, self.row_selected, self.delta)
        self.worker.finished.connect(self.on_process_finished)

        # Hiển thị dialog
        self.progress_dialog = ProgressDialog()
        self.progress_dialog.show()

        # Bắt đầu worker thread
        self.worker.start()
        
    def on_process_finished(self):
        self.progress_dialog.close()
        self.tabAns.setRowCount(0)
        file_name_with_ext = os.path.basename(self.path)
        file_name, _ = os.path.splitext(file_name_with_ext)
        output_file_name = file_name + "_output.txt"
        with open(output_file_name, "r") as file:
            reader = csv.reader(file, delimiter="\t")
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

        # Loop through all columns and set bold font for headers
        for col_idx in range(min(num_columns, 7)):  # Only for the first 7 columns
            header_item = self.tabAns.horizontalHeaderItem(col_idx)
            if header_item is not None:
                font = QtGui.QFont()
                font.setBold(True)
                header_item.setFont(font)

        self.tabAns.setWordWrap(True)

        # Set the width for the first 7 columns
        first_column_width = round(0.4 * self.tabAns.width())
        self.tabAns.setColumnWidth(0, first_column_width)
        self.tabAns.setColumnWidth(1, round(0.1 * self.tabAns.width()))
        self.tabAns.setColumnWidth(2, round(0.15 * self.tabAns.width()))
        self.tabAns.setColumnWidth(3, round(0.15 * self.tabAns.width()))
        self.tabAns.setColumnWidth(4, round(0.0932 * self.tabAns.width()))
        self.tabAns.setColumnWidth(5, round(0.0932 * self.tabAns.width()))

        # Hide the remaining columns
        for col_idx in range(6, num_columns):
            self.tabAns.setColumnHidden(col_idx, True)



    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.setFixedSize(1300, 616)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(mainWindow.sizePolicy().hasHeightForWidth())
        mainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=mainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Button to import data
        self.btnImportData = QtWidgets.QPushButton(
            parent=self.centralwidget, clicked=lambda: self.importData()
        )
        self.btnImportData.setGeometry(QtCore.QRect(40, 40, 251, 23))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.btnImportData.setFont(font)
        self.btnImportData.setObjectName("btnImportData")

        # Button to process
        self.btnProcess = QtWidgets.QPushButton(
            parent=self.centralwidget, clicked=lambda: self.run_app()
        )
        self.btnProcess.setGeometry(QtCore.QRect(950, 40, 301, 23))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)

        # Back btn
        self.btnProcess.setFont(font)
        self.btnProcess.setObjectName("btnProcess")
        self.btnBack = QtWidgets.QPushButton(
            parent=self.centralwidget, clicked=lambda: self.go_back()
        )
        self.btnBack.setGeometry(QtCore.QRect(40, 10, 60, 20))
        font.setPointSize(12)
        self.btnBack.setFont(font)
        self.btnBack.setObjectName("btnBack")
        icon = QtGui.QIcon("icon_back.png")
        self.btnBack.setIcon(icon)
        self.btnBack.clicked.connect(self.go_back)
        # Label and Line Edit for Alpha
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(40, 90, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.ledAlpha = QtWidgets.QLabel(parent=self.centralwidget)
        font.setPointSize(12)
        self.ledAlpha.setFont(font)
        self.ledAlpha.setObjectName("labelDelta")
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
        self.delta = QtWidgets.QLabel(parent=self.centralwidget)
        self.delta.setGeometry(QtCore.QRect(160, 190, 131, 21))
        self.delta.setObjectName("delta")
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.delta.setFont(font)
        self.delta.setObjectName("labelDelta")

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
        self.labInfor.setGeometry(QtCore.QRect(950, 80, 350, 100))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.labInfor.setFont(font)
        self.labInfor.setText("")
        self.labInfor.setObjectName("labInfor")

        # Table Widget
        self.tabAns = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tabAns.setGeometry(QtCore.QRect(30, 240, 1230, 341))
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
        self.ledAlpha.setText(_translate("mainWindow", ""))
        self.label_2.setText(_translate("mainWindow", "Rows Selected"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_Reinforcement()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec())
