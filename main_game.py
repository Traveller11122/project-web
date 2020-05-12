from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QLabel, Qw
from PyQt5.QtGui import QPixmap
import sys
import os
from game import Ui_Form
from autorization import Ui_Form1


class Login(QMainWindow):



class Intro(QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Geometry Dash (alpha)")
        self.pushButton_3.clicked.connect(self.game)
        self.pushButton.clicked.connect(self.info)
        self.pushButton_2.clicked.connect(self.log)
        self.pic = QPixmap(os.path.join('data', 'geometry-dash-icon.png'))
        self.label = QLabel(self)
        self.label.move(225, 100)
        self.label.resize(200, 200)
        self.label.setPixmap(self.pic)

    def game(self):
        import classes_and_functions as code
        self.game_gd = code.Game()
        self.hide()
        self.game_gd.main()
        del self.game_gd, code
        self.show()

    def info(self):
        ok = QMessageBox.information(self, "Управление", "Управление двумя кнопками: пробелом или левой кнопкой мыши.\n"
                                                         "Можно зажать любую из кнопок.")
        if ok:
            pass

    def log(self):
        q = Ui_Form1



if __name__ == '__main__':
    app = QApplication(sys.argv)
    intr = Intro()
    intr.show()
    sys.exit(app.exec())
