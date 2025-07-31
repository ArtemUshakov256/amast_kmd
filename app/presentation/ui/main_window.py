
from PySide6.QtWidgets import (
    QScrollArea, QSizePolicy, QAbstractScrollArea,
    QApplication, QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QHeaderView,
    QHBoxLayout, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPixmap
from app.presentation.constants import *
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
        scroll1_table = self.wrap_table_in_scroll(self.sections_table)
        self.set_initial_state_in_sections_table()
        layout.addWidget(scroll1_table)

        layout.addWidget(QLabel("Траверсы"))
        self.traverse_table = self.create_traverse_table()
        scroll2_table = self.wrap_table_in_scroll(self.traverse_table)
        self.set_initial_state_in_traverse_table()
        layout.addWidget(scroll2_table)

        layout.addWidget(QLabel("Угол узла на уровне троса"))
        self.additional_table = self.create_additional_table()
        scroll3_table = self.wrap_table_in_scroll(self.additional_table)
        image_label = QLabel()
        pixmap = QPixmap(DEGREE_IMAGE_PATH)
        pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignTop)
        hbox = QHBoxLayout()
        hbox.addWidget(scroll3_table)
        hbox.addWidget(image_label)
        hbox.setAlignment(Qt.AlignTop)
        container = QWidget()
        container.setLayout(hbox)
        layout.addWidget(container)

        self.import_button = QPushButton("Экспортировать данные")
        self.import_button.clicked.connect(self.export_data)
        layout.addWidget(self.import_button)

    def create_sections_table(self) -> QTableWidget:
        """Создает таблицу секций с параметрами и выпадающими списками."""
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

    def create_traverse_table(self) -> QTableWidget:
        """Создает таблицу траверс с предопределенными значениями."""
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

    def create_additional_table(self) -> QTableWidget:
        """Создает таблицу дополнительных параметров."""
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

    def set_initial_state_in_sections_table(self) -> None:
        """
        Деактивирует и закрашивает недоступные ячейки в таблице секций.
        """
        table = self.sections_table
        for row_idx in range(len(SECTIONS_ROWS)):
            if row_idx == 6:
                for col in [1, 4, 5, 6, 7, 8, 10]:
                    self.disable_and_grey_cell(table, row_idx, col)
            else:
                self.disable_and_grey_cell(table, row_idx, 8)

    def set_initial_state_in_traverse_table(self) -> None:
        """
        Устанавливает начальное состояние ячеек таблицы траверс.
        """
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

    def wrap_table_in_scroll(self, table: QTableWidget) -> QScrollArea:
        """
        Оборачивает таблицу в scroll area, адаптированную под содержимое.
        Показывает скроллы, если таблица не помещается в окно.
        """
        """
        Оборачивает таблицу в scroll и подгоняет scroll под размер таблицы.
        """
        width = table.verticalHeader().width()
        for col in range(table.columnCount()):
            width += table.columnWidth(col)
        width += table.frameWidth() * 2

        height = table.horizontalHeader().height()
        for row in range(table.rowCount()):
            height += table.rowHeight(row)
        height += table.frameWidth() * 2

        # Настройка scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(table)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Максимально возможный размер scroll'а = размер таблицы
        scroll.setMaximumSize(width + 20, height + 20)  # запас на scrollbars
        scroll.setMinimumSize(100, 100)  # чтобы при пустой таблице не было краха
        return scroll
    
    def export_data(self) -> None:
        """
        Импортирует данные из таблиц и сохраняет в JSON-файл.
        Исключает строку 'Траверсы' как заголовок, 'additional' собирает в список пар.
        """
        # Сбор данных по секциям
        section_data = {}
        for row in range(self.sections_table.rowCount()):
            item = self.sections_table.item(row, 0)
            if not item or not item.text().strip():
                continue
            key = item.text().strip()
            section_data[key] = {}
            for col in range(1, self.sections_table.columnCount()):
                header = SECTIONS_HEADERS[col]
                if (widget := self.sections_table.cellWidget(row, col)):
                    val = widget.currentText()
                elif (cell := self.sections_table.item(row, col)):
                    val = cell.text()
                else:
                    val = ""
                section_data[key][header] = val

        # Сбор данных по траверсам
        traverse_data = {}
        for row in range(self.traverse_table.rowCount()):
            item = self.traverse_table.item(row, 0)
            if not item or not item.text().strip():
                continue
            key = item.text().strip()
            if "траверс" in key.lower():
                continue
            traverse_data[key] = {}
            for col in range(1, self.traverse_table.columnCount()):
                header_item = self.traverse_table.horizontalHeaderItem(col)
                header = header_item.text() if header_item else f"Column {col}"
                widget = self.traverse_table.cellWidget(row, col)
                if isinstance(widget, QComboBox):
                    val = widget.currentText()
                elif (cell := self.traverse_table.item(row, col)):
                    val = cell.text()
                else:
                    val = ""
                traverse_data[key][header] = val

        # Сбор additional как список значений
        additional_data = []
        for row in range(self.additional_table.rowCount()):
            widget = self.additional_table.cellWidget(row, 1)
            if isinstance(widget, QComboBox):
                val = widget.currentText()
            else:
                cell = self.additional_table.item(row, 1)
                val = cell.text() if cell else ""

            if val.strip():
                additional_data.append(val.strip())

        # Финальный объект
        self.data = {
            "sections": section_data,
            "traverses": traverse_data,
            "additional": additional_data,
        }

        # Диалог выбора файла
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить данные как...",
            "data.json",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Успешно", f"Данные сохранены в:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


def run_app():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
