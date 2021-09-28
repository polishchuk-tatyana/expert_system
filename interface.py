from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
        QVBoxLayout, QPushButton, QLabel, QLineEdit,QTextEdit)

class Interface():

    def __init__(self):
        self.goal = QLineEdit('')
        self.button = QPushButton('Звантажити базу знань')
        self.rules = QTextEdit()
        self.facts = QTextEdit()
        self.go_chain1 = QPushButton('Вивести ланцюжок міркувань')
        self.chain = QTextEdit()
        # self.chain2 = QTextEdit()
        self.find = QTextEdit()
        self.result = QTextEdit()

        self.label1 = QLabel('Перегляд правил БП')
        self.label2 = QLabel('Перегляд фактів БП')
        self.window = QWidget()

    def show(self):
        app = QApplication([])
        self.window.resize(900, 600)

        line1 = QVBoxLayout()
        line2 = QVBoxLayout()
        line_chain = QHBoxLayout()
        line_button = QHBoxLayout()
        main = QHBoxLayout()
        self.goal.setPlaceholderText('Введіть ціль...')
        line1.addWidget(self.button)
        line1.addWidget(self.label1)
        line1.addWidget(self.rules)
        line1.addWidget(self.label2)
        line1.addWidget(self.facts)
        line2.addWidget(self.goal)
        line2.addWidget(self.find)
        line_button.addWidget(self.go_chain1)
        line2.addLayout(line_button)
        line_chain.addWidget(self.chain)
        # line_chain.addWidget(self.chain2)
        line2.addLayout(line_chain)
        line2.addWidget(self.result)


        main.addLayout(line1)
        main.addLayout(line2)

        self.window.setLayout(main)


        self.window.show()
        app.exec_()
