from PyQt6 import QtCore, QtGui, QtWidgets
from ReducedData import Ui_ReducedData
from Reinforcement import Ui_Reinforcement


class Ui_MainWindow(object):

    def openReducedData(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_ReducedData()
        self.ui.setupUi(self.window)
        self.window.show()

    def openReinforcement(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_Reinforcement()
        self.ui.setupUi(self.window)
        self.window.show()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(800, 477)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 20, 751, 20))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.label.setToolTipDuration(0)
        self.label.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.label.setAutoFillBackground(False)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.btnReducedData = QtWidgets.QPushButton(
            parent=self.centralwidget, clicked=lambda: self.openReducedData()
        )
        self.btnReducedData.setGeometry(QtCore.QRect(180, 150, 431, 31))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnReducedData.setFont(font)
        self.btnReducedData.setObjectName("btnReducedData")
        self.btnReinforcement = QtWidgets.QPushButton(
            parent=self.centralwidget, clicked=lambda: self.openReinforcement()
        )
        self.btnReinforcement.setGeometry(QtCore.QRect(180, 270, 431, 31))
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnReinforcement.setFont(font)
        self.btnReinforcement.setObjectName("btnReinforcement")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(
            _translate(
                "MainWindow", "Chương trình rút gọn thuộc tính trên bảng quyết định "
            )
        )
        self.btnReducedData.setText(
            _translate("MainWindow", "Thuật toán tìm tập rút gọn trên bảng tĩnh"),
        )
        self.btnReinforcement.setText(_translate("MainWindow", "Thuật toán gia tăng"))

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
