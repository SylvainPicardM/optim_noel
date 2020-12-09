from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QMainWindow,
    QLineEdit, QVBoxLayout, QLabel,
    QDialogButtonBox, QGridLayout, QPushButton)
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem
from checkable_combo_box import CheckableComboBox

class AppView(QMainWindow):
    def __init__(self, products):
        """View initializer."""
        super().__init__()
        self.setWindowTitle('Calcul compatibilité produits')
        self.setFixedSize(400, 400)
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        self.products = products
        self._create_form()
        self._create_buttons()
        self._create_display()

    def _create_form(self):
        combo = CheckableComboBox()
        combo.addItems(self.products)
        self.form = QFormLayout()
        self.form.addRow('Produits:', combo)
        self.generalLayout.addLayout(self.form)

    def _create_buttons(self):
        self.buttons = {}
        buttonsLayout = QGridLayout()
        buttons = {'Run': (0, 0), 'Cancel': (0, 1)}
        for btnText, pos in buttons.items():
            self.buttons[btnText] = QPushButton(btnText)
            self.buttons[btnText].setFixedSize(80, 40)
            buttonsLayout.addWidget(self.buttons[btnText], pos[0], pos[1])
        self.generalLayout.addLayout(buttonsLayout)

    def _create_display(self):
        """Create the display."""
        # self.table = QTableWidget()
        # self.table.setRowCount(1)
        # self.table.setColumnCount(2)
        # self.table.setItem(0, 0, QTableWidgetItem("Groupe"))
        # self.table.setItem(0, 1, QTableWidgetItem("Produit"))
        self.display = QLabel()
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setFixedSize(400, 400)
        self.generalLayout.addWidget(self.display)


    def set_display(self, group_dict):
        text = ""
        for g, plist in group_dict.items():
            text += f'Rétention {g}:  '
            first = True
            for p in plist:
                if first:
                    text += f'{p}\n'
                    first = False
                else:
                    text += f'                      {p}\n'
            text += " --------------------- \n"
        self.display.setText(text)
        # i = 1
        # for g, plist in group_dict.items():
        # 	for p in plist:
        # 		self.table.insertRow(i)
        # 		self.table.setItem(i, 0, QTableWidgetItem(str(g)))
        # 		self.table.setItem(i, 1, QTableWidgetItem(str(p)))
        # 		i += 1


    def clear_display(self):
        widget = self.form.itemAt(1)
        combo = widget.widget()
        combo.clear()

        for i in range(1, self.table.rowCount() + 1):
            self.table.removeRow(1)