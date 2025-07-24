from PyQt5.QtWidgets import (
      QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
      QTabWidget, QLineEdit, QComboBox, QFormLayout,
      QFileDialog, QDialog)
from PyQt5.QtCore import pyqtSignal
import sqlite3
from dicts import sections, boxes_dict, input_dict


class WreckInfoWindow(QWidget):
    switch_signal = pyqtSignal(str, object)

    def __init__(self, wreck_data):
        super().__init__()
        self.setWindowTitle("Wreck Information")
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.create_gui(wreck_data)


    def create_gui(self, wreck_data):
        """ Creates The GUI, Basically The Data Entry Page, But Empty Spots Ommitted """

        top_row = QHBoxLayout()

        ship = QComboBox() # choose between the ships
        
        for row in wreck_data:
            ship.addItem(row[0])

        id = ship.currentTextChanged.connect(lambda: self.update_id(ship.currentText()))

        back = QPushButton("Back to the Map")

        back.clicked.connect(lambda: self.switch_signal.emit("map", None))

        top_row.addWidget(ship)
        top_row.addWidget(back)
        self.main_layout.addLayout(top_row)

        self.info_sections = QTabWidget()
        self.main_layout.addWidget(self.info_sections)

        self.display()


    def display(self):
        """ Sets The Data In The Tabs """
        # grab all the sections
        self.sections = sections()
        data = input_dict()
        self.combo_boxes = boxes_dict()

        # for each section
        for section_name, fields in self.sections.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab.setLayout(tab_layout)
            self.info_sections.addTab(tab, section_name)

            form = QFormLayout()

            # TODO: this will just add everything multiple times to each tab
            for key in fields.keys():
                if key in data:
                    # switch to the other dict 
                    data_keys = data[key]
                    self.populate(data_keys[0], data_keys[1], data_keys[2], key)

                #query = f"SELECT {}"
                
            # for the specific ship
                # look for data
                    # if blank, continue
                    # else display the data
        # have a edit button
            # takes you to an editing page
        # delete button
            # deletes the shipwreck from the db0

    
    def populate(self, where, what, lookup, key):
        """ Populates The Form with SQL Queries """

        # get the data
        #conn = sqlite3.connect("shipwrecks.db")
        #c = conn.cursor()
        #c.execute(f"SELECT {what} FROM {where}")
        #results = c.fetchall()

        if lookup: # if the result is an id, lookup the name
            for key, value in self.combo_boxes.items():
                if value[1] == lookup:
                    print(key + ":")
                    print(value[1], value[0])   #TODO: get the name from the id, return the name

            #c.execute(f"SELECT {}")


    def update_id(self, ship):
        """ Gets The Ship ID Of What Ship Is Selected """
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("SELECT id FROM wrecks WHERE name = ?", (ship,))
        id = c.fetchone()
        conn.close()
        return id