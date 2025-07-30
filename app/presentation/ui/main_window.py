
from PySide6.QtWidgets import (
    QScrollArea, QSizePolicy, QAbstractScrollArea,
    QApplication, QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from ..constants import *
import json


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Amast KMD")
        self.setMinimumSize(1000, 600)
        self.adjustSize()
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Секции"))
        self.sections_table = self.create_sections_table()
        self.set_initial_state_in_sections_table()
        scroll1 = QScrollArea()
        scroll1.setWidgetResizable(True)
        self.sections_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.sections_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        scroll1.setWidget(self.sections_table)
        layout.addWidget(scroll1)

        layout.addWidget(QLabel("Траверсы"))
        self.traverse_table = self.create_traverse_table()
        self.set_initial_state_in_traverse_table()
        scroll2 = QScrollArea()
        scroll2.setWidgetResizable(True)
        self.traverse_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.traverse_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        scroll2.setWidget(self.traverse_table)
        layout.addWidget(scroll2)

        layout.addWidget(QLabel("Угол узла на уровне троса"))
        self.additional_table = self.create_additional_table()
        scroll3 = QScrollArea()
        scroll3.setWidgetResizable(True)
        self.additional_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.additional_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        scroll3.setWidget(self.additional_table)
        layout.addWidget(scroll3)

        self.import_button = QPushButton("Экспортировать данные")
        self.import_button.clicked.connect(self.import_data)
        layout.addWidget(self.import_button)

    def create_sections_table(self):
        table = QTableWidget(len(SECTIONS_ROWS) + 1, len(SECTIONS_HEADERS))
        table.verticalHeader().setVisible(False)
        
        self.set_headers_with_optional_tooltips(
            table,
            SECTIONS_HEADERS,
            SECTIONS_TIPS_DICT
        )

        for row_idx, row_name in enumerate(SECTIONS_ROWS):
            for col_idx, col_name in enumerate(SECTIONS_HEADERS):
                if row_idx == 0 and col_idx != 4:
                    table.setSpan(row_idx, col_idx, 2, 1)
                if col_idx == 0:
                    item = QTableWidgetItem(row_name)
                    item.setFlags(Qt.ItemIsEnabled)
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row_idx, col_idx, item)
                elif row_name == "":
                    continue
                elif col_name == "Кол-во болтов, шт":
                    combo = QComboBox()
                    combo.addItems(["12", "24", "36", "48"])
                    table.setCellWidget(row_idx, col_idx, combo)
                    item = table.item(row_idx, col_idx)
                elif col_name == "d болтов, мм":
                    combo = QComboBox()
                    combo.addItems(["20", "24", "30", "36", "42", "48", "56"])
                    table.setCellWidget(row_idx, col_idx, combo)
                    item = table.item(row_idx, col_idx)
                elif col_name == "Кол-во скорлупок\nсекции, шт":
                    combo = QComboBox()
                    combo.addItems(["2", "3"])
                    table.setCellWidget(row_idx, col_idx, combo)
                    item = table.item(row_idx, col_idx)
                elif col_name == "Тип соединения с\nнижней секцией" and row_idx == 0:
                    combo = QComboBox()
                    combo.addItems(["Фланц."])
                    table.setCellWidget(row_idx, col_idx, combo)
                    item = table.item(row_idx, col_idx)
                elif col_name == "Тип соединения с\nнижней секцией" and row_idx != 6:
                    combo = QComboBox()
                    combo.addItems(["Фланц.", "Телескоп."])
                    combo.currentTextChanged.connect(lambda _, row=row_idx: self.handle_connection_type_change(row))
                    table.setCellWidget(row_idx, col_idx, combo)
                else:
                    item = QTableWidgetItem("")
                    table.setItem(row_idx, col_idx, item)
                    item.setTextAlignment(Qt.AlignCenter)

        table.removeRow(7)

        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        return table

    def create_traverse_table(self):
        row_count = 2 + len(TRAVERSE_ROWS)  # 2 заголовка + данные
        col_count = 34  # колонки разбиты вручную

        table = QTableWidget(row_count, col_count)
        # table.setHorizontalHeaderLabels(HEADERS_TOP[:-5])
        self.set_headers_with_optional_tooltips(table, HEADERS_TOP[:-5], TRAVERSE_TIPS_DICT)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Верхние заголовки (первая строка)
        top_row = 0
        combobox_list = ["Узел в\nствол опоры (ℹ)", "Угол поворота\nтраверсы, град"]
        for col, header in enumerate(HEADERS_TOP):
            if header in combobox_list:
                for row in range(2, 9):
                    combo = QComboBox()
                    if header == "Узел в\nствол опоры (ℹ)":
                        combo.addItems(["0", "1", "2", "3", "4", "5"])
                        self.set_item_with_optional_tooltip(table, row, col, header, TRAVERSE_TIPS_DICT)
                    else:
                        combo.addItems(["0", "30", "60", "-30", "60"])
                    table.setCellWidget(row, col, combo)
                    item = table.item(row, col)
            if header == "Узел крепл. Траверса Л (ℹ)":
                table.setSpan(top_row, 13, 1, 5)
                self.set_item_with_optional_tooltip(table, top_row, 13, header, TRAVERSE_TIPS_DICT)
            elif header == "Узел крепл. Траверса П":
                table.setSpan(top_row, 18, 1, 5)
                item = QTableWidgetItem(header)
                item.setFlags(Qt.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(top_row, 18, item)
            elif header == "Распол. узла Траверса Л (ℹ)":
                table.setSpan(top_row, 23, 1, 5)
                self.set_item_with_optional_tooltip(table, top_row, 23, header, TRAVERSE_TIPS_DICT)
            elif header == "Распол. узла Траверса П":
                table.setSpan(top_row, 28, 1, 5)
                item = QTableWidgetItem(header)
                item.setFlags(Qt.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(top_row, 28, item)
            elif header == "Пластина на\nконце траверсы (ℹ)":
                table.setSpan(top_row, 33, 2, 1)
                self.set_item_with_optional_tooltip(table, top_row, 33, header, TRAVERSE_TIPS_DICT)
            else:
                table.setSpan(top_row, col, 2, 1)
                self.set_item_with_optional_tooltip(table, top_row, col, header, TRAVERSE_TIPS_DICT)
        # Вложенные заголовки
        col_start = 13
        for i in range(4):
            for subheader, name in enumerate(SUBHEADERS):
                item = QTableWidgetItem(name)
                item.setFlags(Qt.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(1, col_start + subheader, item)
                if i < 2:
                    for row in range(2, 9):
                        combo = QComboBox()
                        combo.addItems(["0", "1", "2", "3", "4", "5"])
                        table.setCellWidget(row, col_start + subheader, combo)
            col_start += 5
        combo = QComboBox()
        combo.addItems(["1", "2", "3", "7", "12", "16"])
        table.setCellWidget(2, 33, combo)

        # Основные строки данных
        for row_idx, row_name in enumerate(TRAVERSE_ROWS):
            item = QTableWidgetItem(row_name)
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row_idx + 2, 0, item)
            for col in range(1, col_count):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_idx + 2, col, item)
                
        return table

    def create_additional_table(self, ):
        table = QTableWidget(4, 2)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setSpan(0, 0, 4, 1)
        self.set_item_with_optional_tooltip(
            table,
            0,
            0,
            "Угол узла\nв ствол на\nуровне\nтрос.трав.",
        )

        for i in range(4):
            combo = QComboBox()
            combo.addItems(DEGREE_COMBOBOX)
            table.setCellWidget(i, 1, combo)

        return table
    
    def handle_connection_type_change(self, row_idx):
        table = self.sections_table
        conn_type = table.cellWidget(row_idx, 1).currentText()
        disabled_cols = []

        if conn_type == "Фланц.":
            disabled_cols = ["Длина стыка\nтелескопа, мм"]
        elif conn_type == "Телескоп.":
            disabled_cols = ["Dсекции, мм (ℹ)", "Толщина фланца, мм",
                             "Кол-во болтов, шт", "d болтов, мм",
                             "D располож.\nболтов, мм"]

        for col_idx in range(2, table.columnCount()):
            col_name = SECTIONS_HEADERS[col_idx]
            item = table.item(row_idx, col_idx)
            if col_name in disabled_cols and col_name in ["Кол-во болтов, шт", "d болтов, мм"]:
                combo = table.cellWidget(row_idx, col_idx)
                combo.setEnabled(False)
            elif col_name in disabled_cols:
                self.disable_and_grey_cell(table, row_idx, col_idx)
            else:
                if col_name in ["Кол-во болтов, шт", "d болтов, мм", "Кол-во скорлупок\nсекции, шт"]:
                    combo = table.cellWidget(row_idx, col_idx)
                    combo.setEnabled(True)
                else:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
                    item.setBackground(QBrush(QColor("white"))) 
            table.viewport().update()

    def set_initial_state_in_sections_table(self):
        table = self.sections_table
        for row_idx in range(len(SECTIONS_ROWS)):
            if row_idx == 6:
                for col in [1, 4, 5, 6, 7, 8, 10]:
                    self.disable_and_grey_cell(table, row_idx, col)
            else:
                self.disable_and_grey_cell(table, row_idx, 8)

    def set_initial_state_in_traverse_table(self):
        table = self.traverse_table
        for row_idx in range(len(TRAVERSE_ROWS) + 2):
            if row_idx > 4:
                for col in [15, 16, 17, 20, 21, 22, 25, 26, 27, 30, 31, 32]:
                    table.removeCellWidget(row_idx, col)
                    self.disable_and_grey_cell(table, row_idx, col)
            else:
                self.disable_and_grey_cell(table, row_idx + 4, 33)
        self.disable_and_grey_cell(table, 3, 33)
    
    def disable_and_grey_cell(self, table, row, col):
        item = table.item(row, col)
        if item is None:
            item = QTableWidgetItem("")
            table.setItem(row, col, item)
        item.setFlags(Qt.ItemIsEnabled)
        item.setBackground(QBrush(QColor("grey")))
        item.setText("")

    def set_headers_with_optional_tooltips(self, table, headers: list[str], tooltips: dict[str, str]):
        """
        Устанавливает заголовки таблицы. К заголовкам, указанным в словаре tooltips, добавляет всплывающую подсказку.
        
        :param table: QTableWidget
        :param headers: Список заголовков
        :param tooltips: Словарь {заголовок: текст подсказки}
        """
        for i, title in enumerate(headers):
            item = QTableWidgetItem(title)
            if title in tooltips:
                item.setToolTip(tooltips[title])
            table.setHorizontalHeaderItem(i, item)

    def set_item_with_optional_tooltip(self, table, row: int, col: int, value: str, tooltips: dict[tuple[int, int], str] | None = None):
        """
        Устанавливает значение ячейки и добавляет всплывающую подсказку, если она есть в словаре.

        :param table: QTableWidget
        :param row: Индекс строки
        :param col: Индекс столбца
        :param value: Текст для отображения в ячейке
        :param tooltips: Словарь {(row, col): tooltip}
        """
        item = QTableWidgetItem(value)
        item.setFlags(Qt.ItemIsEnabled)
        item.setTextAlignment(Qt.AlignCenter)
        key = (row, col)
        if tooltips and key in tooltips:
            item.setToolTip(tooltips[key])
        table.setItem(row, col, item)

    def import_data(self):
        section_data = {}
        for row in range(self.sections_table.rowCount()):
            key = self.sections_table.item(row, 0).text()
            section_data[key] = {}
            for col in range(1, self.sections_table.columnCount()):
                header = SECTIONS_HEADERS[col]
                if self.sections_table.cellWidget(row, col):
                    val = self.sections_table.cellWidget(row, col).currentText()
                else:
                    val = self.sections_table.item(row, col).text()
                section_data[key][header] = val

        traverse_data = {}
        for row in range(self.traverse_table.rowCount()):
            key = self.traverse_table.item(row, 0).text()
            traverse_data[key] = {}
            for col in range(1, self.traverse_table.columnCount()):
                header = self.traverse_headers[col]
                traverse_data[key][header] = self.traverse_table.item(row, col).text()

        self.data = {
            "sections": section_data,
            "traverses": traverse_data
        }

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

        print("✅ Данные успешно экспортированы")


def run_app():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
