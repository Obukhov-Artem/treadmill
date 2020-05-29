# Пример испоьзования QCheckBox


import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Тест'
        self.resize(400, 400)
        self.setFont(QFont('Times', 13))
        layout = QVBoxLayout()
        self.radiobox = QCheckBox('Ответ 1', self)
        self.radiobox.clicked.connect(self.selected_choice_1)
        self.radiobox2 = QCheckBox('Ответ 2', self)
        self.radiobox2.clicked.connect(self.selected_choice_2)
        layout.addSpacing(20)
        layout.addWidget(self.radiobox)
        layout.addSpacing(20)
        layout.addWidget(self.radiobox2)
        self.setLayout(layout)
        self.show()

    def selected_choice_1(self, state):
        if state:
            print(self.radiobox.text())

    def selected_choice_2(self, state):
        if state:
            print(self.radiobox2.text())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
