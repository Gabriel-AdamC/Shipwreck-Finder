from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QTabWidget, QLineEdit
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
        # Creates the buttons to change between parts of the app
        self.page_change = QHBoxLayout()
        self.btn_map = QPushButton("Map")
        self.btn_map.clicked.connect(lambda: self.switch_signal.emit("map"))
        self.btn_entry = QPushButton("Data Entry")
        self.btn_entry.clicked.connect(lambda: self.switch_signal.emit("data_entry"))
        self.page_change.addWidget(self.btn_map)
        self.page_change.addWidget(self.btn_entry)
        layout.addLayout(self.page_change)

        # I want to loop through the form inputs, so that I can avoid hardcoding each one.
        # So here is a dict of all the info I need to effectively loop and dynamically create
        self.sections = {
            "wreck": {
                "kraken_id": QLineEdit(),
            },
            "location": {

            }
        }

        # Create tabs for grouped sections of the form, rather than one extremely long form
        form_sections = QTabWidget()
        tabs = ["Location", "Construction Details", "Wreck Event", "Registration Details", "Personnel", "Archaeological Details", "Sources"]
        for name in tabs:
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab.setLayout(tab_layout)
            form_sections.addTab(tab, name)
        layout.addWidget(form_sections)