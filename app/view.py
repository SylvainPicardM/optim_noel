from PyQt5.QtWidgets import (
	QWidget, QFormLayout, QMainWindow,
	QLineEdit, QVBoxLayout, QLabel,
	QDialogButtonBox, QGridLayout, QPushButton)
from PyQt5.QtCore import Qt
from checkable_combo_box import CheckableComboBox


class AppView(QMainWindow):
	def __init__(self, products):
		"""View initializer."""
		super().__init__()
		self.setWindowTitle('Super App')
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
		# Create the display widget
		self.display = QLabel()
		# Set some display's properties
		self.display.setFixedHeight(300)
		self.display.setAlignment(Qt.AlignCenter)
		# Add the display to the general layout
		self.generalLayout.addWidget(self.display)

	def setDisplayText(self, text):
		"""Set display's text."""
		self.display.setText(text)
		self.display.setFocus()

	def displayText(self):
		"""Get display's text."""
		return self.display.text()

	def clearDisplay(self):
		"""Clear the display."""
		self.setDisplayText('')