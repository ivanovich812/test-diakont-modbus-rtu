"""
ТЕСТОВОЕ ЗАДАНИЕ "ДИАКОНТ"
Реализовано:
- опрос Modbus Slave устройства функцией #03-Holding Registers;
- опрос регистров измерений modbus-устройства формата: float, порядок байт - CD AB(как наиболее используемый формат
при передаче точных измерений в АСУ ТП)
- ввод параметров запуска скрипта в командной строке windows:
в формате: 'начальный адрес регистра' пробел 'количество опрашиваемых регистров' пробел 'адрес modbus slave-устройства'
(н.п. команда python main.py 0 10 1  - это запустить опрос с начального регистра - 0, кол-во считываемых регистров - 10,
адрес modbus slave-устройства - 1)
- представление результатов запроса в виде таблицы для одновременного отображения всех запрошенных измерений;
- обновление измерений в реальном времени.
"""
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QSize, QTimer
from pymodbus.client import ModbusSerialClient
from sys import argv
import numpy as np
import time

class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        #параметры, задаваемые командной строкой windows при запуске скрипта
        script, self.start_add, self.count, self.slave = argv
        #создаем connection по парметрам связи slave-устройства
        self.client = ModbusSerialClient(port="COM6", stopbits=2, bytesize=8, parity='N', baudrate=9600, strict=False)
        self.client.connect()
        time.sleep(2)

        # Window
        self.setMinimumSize(QSize(100, 376))
        self.setWindowTitle("Test Modbus RTU")

        # Labels
        self.nameLabel_1 = QLabel(self)
        self.nameLabel_1.setText(str("Connection: "))
        self.nameLabel_1.move(20, 20)

        self.nameLabel_2 = QLabel(self)
        self.nameLabel_2.setText(str("start_add: "))
        self.nameLabel_2.move(20, 40)

        self.nameLabel_3 = QLabel(self)
        self.nameLabel_3.setText(str("count: "))
        self.nameLabel_3.move(20, 60)

        self.nameLabel_4 = QLabel(self)
        self.nameLabel_4.setText(str("slave: "))
        self.nameLabel_4.move(20, 80)

        # Fields
        self.nameLabel_11 = QLabel(self)
        self.nameLabel_11.setText(str(self.client.connect()))
        self.nameLabel_11.move(100, 20)

        self.nameLabel_22 = QLabel(self)
        self.nameLabel_22.setText(str(self.start_add))
        self.nameLabel_22.move(100, 40)

        self.nameLabel_33 = QLabel(self)
        self.nameLabel_33.setText(str(self.count))
        self.nameLabel_33.move(100, 60)

        self.nameLabel_44 = QLabel(self)
        self.nameLabel_44.setText(str(self.slave))
        self.nameLabel_44.move(100, 80)

        # создаем виджет Таблица
        self.tb = QTableWidget(self)
        self.tb.setGeometry(5, 120, 190, 250)
        self.tb.setColumnCount(2)

        self.tb.setColumnWidth(0, 86)
        self.tb.setColumnWidth(1, 87)

        self.tb.clear()
        self.tb.setRowCount(0)
        self.tb.setHorizontalHeaderLabels(['Reg_address','Value'])

        # создаем колонки, строки по полученным измерениям и первично заполняем Таблицу
        i = 0
        for elem in self.read_hold_reg():
            self.tb.setRowCount(self.tb.rowCount() + 1)
            j = 0
            for t in elem:
                self.tb.setItem(i, j, QTableWidgetItem(str(t)))
                j += 1
            i += 1

        # для real time - отображения измерений в таблице используем таймер
        self.qTimer = QTimer()
        # интервал 1 сек
        self.qTimer.setInterval(1000)  # 1000 ms = 1 s
        # коннектим функцию обновления измерений в таблице к таймеру
        self.qTimer.timeout.connect(self.update_hold_reg)
        # старт таймер
        self.qTimer.start()

    # функция чтения измерений по заданным параметрам запуска скрипта
    def read_hold_reg(self):
        # чтение регистров
        res = self.client.read_holding_registers(address=int(self.start_add), count=int(self.count), slave=int(self.slave))
        # создаем массив данных типа word
        word16 = np.array(res.registers, dtype=np.int16)
        # преобразуем в список типа float
        vals = list(word16.view(dtype=np.float32))
        # создаем список адресов регистров для наглядного отображения в таблице
        # т.к. тип данных word занимает 1 регистр памяти, а float 2 регистра памяти, адресация float измерений будет 0, 2, 4...
        regs = []
        for i in range(int(self.start_add), (int(self.start_add) + int(self.count)), 2):
            regs.append(i)
        tab = [list(tup) for tup in zip(regs, vals)]
        #функция возвращает список списков для заполнения таблицы
        return tab

    # функция обновления значений в ячейках таблицы по таймеру
    def update_hold_reg(self):
        i = 0
        for elem in self.read_hold_reg():
            j = 0
            for t in elem:
                self.tb.setItem(i, j, QTableWidgetItem(str(t)))
                j += 1
            i += 1

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())