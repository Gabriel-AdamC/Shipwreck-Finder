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

        ship = QComboBox() # choose between the ships
        
        for row in wreck_data.values():
            ship.addItem(row[0])

        id = ship.currentTextChanged.connect(lambda: self.update_id(ship.currentText()))
        self.main_layout.addWidget(ship)

        info_sections = QTabWidget()
        self.main_layout.addWidget(info_sections)

        # grab all the sections
        self.sections = sections()
        data = input_dict()

        # some items are kept as ids referencing other tables
        # these are what need to be converted
        convert = boxes_dict()

        # for each section
        for section_name in self.sections.keys():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab.setLayout(tab_layout)
            info_sections.addTab(tab, section_name)

            form = QFormLayout()

            # TODO: this will just add everything multiple times to each tab
            for key, widget in data.items():
                conn = sqlite3.connect("shipwrecks.db")
                c = conn.cursor()

                #query = f"SELECT {}"
                
            # for the specific ship
                # look for data
                    # if blank, continue
                    # else display the data
        # have a edit button
            # takes you to an editing page
        # delete button
            # deletes the shipwreck from the db0


    def update_id(self, ship):
        """ Gets The Ship ID Of What Ship Is Selected """
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("SELECT id FROM wrecks WHERE name = ?", (ship,))
        id = c.fetchone()
        conn.close()
        return id