from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTabWidget
)
from PyQt5.QtCore import pyqtSignal
import sqlite3
import helpers
from dicts import boxes_dict, input_dict, sections

class EditWreckWindow(QWidget):
    switch_signal = pyqtSignal(str, object)

    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Edit Wrecks")
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.data_display = helpers.DataDisplayWidget()

        self.create_gui(data)


    def create_gui(self, data):
        """ Create The Outer GUI For This Page """
        top_row = QHBoxLayout()
        # change between pages
        self.btn_map = QPushButton("Map")
        self.btn_map.clicked.connect(lambda: self.switch_signal.emit("map", None))
        self.btn_entry = QPushButton("Data Entry")
        self.btn_entry.clicked.connect(lambda: self.switch_signal.emit("data_entry", None))
        top_row.addWidget(self.btn_map)
        top_row.addWidget(self.btn_entry)
        self.main_layout.addLayout(top_row)

        ship_row = QHBoxLayout()

        ship = QComboBox() # choose between the ships
        
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("SELECT name FROM wrecks")
        names = c.fetchall()
        conn.close()

        if data is not None: # set index[0] to the chosen ship from see_wreck
            self.current_name = self.get_name(data)
            ship.addItem(self.current_name)

        for name in names: # populate the ship options
            # names is a list of tuples and name is a tuple
            untupled = name[0]
            if hasattr(self, "current_name") and untupled == self.current_name: # skip the ship that has already been put in to avoid doubles
                continue
            ship.addItem(untupled)
        
        ship.setCurrentIndex(0) # will set to the first available ship. If data was passed, it will be the desired ship

        # set the variables for the first iteration
        self.name = ship.currentText()
        self.ids = helpers.update_id(self.name)

        ship_row.addWidget(ship)
        self.main_layout.addLayout(ship_row)

        # Update the info when user changes ship options
        ship.currentTextChanged.connect(self.update_info)

        # create actual display
        self.info_sections = QTabWidget()
        self.main_layout.addWidget(self.info_sections)

        self.main_layout.addWidget(self.data_display)

        self.display()

    
    def display(self):
        self.data_display.display(
            name = self.name,
            ids=self.ids,
            sections_func=sections,
            input_dict_func=input_dict,
            boxes_dict_func=boxes_dict,
            db_path="shipwrecks.db",
            edit_callback=self.update,
            what = "edit"
        )

    
    def get_name(self, id):
        """ Get The Name Of Ship Based Off ID """
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("SELECT name FROM wrecks WHERE id = ?", (id,))
        name = c.fetchone()

        if name:
            untupled = name[0] # sqlite3 returns a tuple with fetchone
        return untupled
    

    def update_info(self, new_name):
        """ Updates The Info To The Current Viewed Ship """
        self.name = new_name
        self.ids = helpers.update_id(new_name)

        self.display()
        