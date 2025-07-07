from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

class DataEntryWindow(QWidget):

    switch_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.entry_ui(layout)

    def entry_ui(self, layout):
        """ Set up the UI for data entry. """
        # This method can be expanded to include actual data entry fields
        self.label = QLabel("Data Entry Page")
        # Add more widgets as needed for data entry
        # For example, text fields, dropdowns, etc.
        
        # Example of adding a button to submit data
        self.btn_submit = QPushButton("Submit Data")
        #self.btn_submit.clicked.connect(self.submit_data)
        layout.addWidget(self.btn_submit)
        layout.addWidget(self.label)