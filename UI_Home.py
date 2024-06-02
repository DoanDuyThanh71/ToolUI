from PyQt6 import QtCore, QtGui, QtWidgets
from UI_ReducedData import Ui_ReducedData
from UI_Reinforcement import Ui_Reinforcement
from UI_IFPD import UI_IFPD

class Ui_MainWindow(object):
    def openReducedData(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_ReducedData()
        self.ui.setupUi(self.window)
        self.window.setWindowTitle("Static Table Attribute Reduction Algorithm")
        self.window.show()

    def openReinforcement(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_Reinforcement()
        self.ui.setupUi(self.window)
        self.window.setWindowTitle("Incremental Algorithm")
        self.window.show()
        
    def openIFPD(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = UI_IFPD()
        self.ui.setup(self.window)
        self.window.setWindowTitle("Load Reduction Algorithm")
        self.window.show()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(800, 477)
        MainWindow.setFixedSize(800, 477)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 50, 751, 40))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")

        self.btnReducedData = QtWidgets.QPushButton(self.centralwidget)
        self.btnReducedData.setGeometry(QtCore.QRect(180, 150, 431, 41))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnReducedData.setFont(font)
        self.btnReducedData.setObjectName("btnReducedData")
        self.btnReducedData.clicked.connect(self.openReducedData)

        self.btnReinforcement = QtWidgets.QPushButton(self.centralwidget)
        self.btnReinforcement.setGeometry(QtCore.QRect(180, 270, 431, 41))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnReinforcement.setFont(font)
        self.btnReinforcement.setObjectName("btnReinforcement")
        self.btnReinforcement.clicked.connect(self.openReinforcement)
        
        
        self.btnIFPD = QtWidgets.QPushButton(self.centralwidget)
        self.btnIFPD.setGeometry(QtCore.QRect(180, 390, 431, 41))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnIFPD.setFont(font)
        self.btnIFPD.setObjectName("btnIFPD")
        self.btnIFPD.clicked.connect(self.openReinforcement)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(
            _translate(
                "MainWindow",
                "Attribute Reduction Program for Decision Tables",
            )
        )
        self.btnReducedData.setText(
            _translate("MainWindow", "Static Table Attribute Reduction Algorithm")
        )
        self.btnReinforcement.setText(_translate("MainWindow", "Incremental Algorithm"))
        self.btnIFPD.setText(_translate("MainWindow", "Load Reduction Algorithm"))

    def run_app(self):
        subprocess.Popen(["python", "app.py"])


if __name__ == "__main__":
    import sys
    import subprocess

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
