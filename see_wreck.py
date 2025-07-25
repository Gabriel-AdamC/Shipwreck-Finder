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

        self.name = ship.currentText()
        self.ids = self.update_id(self.name)  # Creates a tuple of (ship_id, location_row_ID, build_id)

        ship.currentTextChanged.connect(self.update_ship_info)

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
                    info = self.populate(data_keys[0], data_keys[1], data_keys[2], key)
                    if info is None:
                        continue
                    viewable_data = info[0]
                    if viewable_data is None:
                        continue
                    elif isinstance(viewable_data, int) or isinstance(viewable_data, float):
                        viewable_data = str(viewable_data) 
                    form.addRow(key.replace("_", " ").capitalize(), QLabel(viewable_data))

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
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()

        if where != "wrecks" and where != "locations" and where != "builds":
            c.execute(f"SELECT {what} FROM {where} WHERE (ship_id) = ?", (self.ids[0],))
        elif where == "wrecks":
            c.execute(f"SELECT {what} FROM {where} WHERE (name) = ?", (self.name,))
        elif where == "locations":
            c.execute(f"SELECT {what} FROM {where} WHERE (location_row_ID) = ?", (self.ids[1],))
        else:
            c.execute(f"SELECT {what} FROM {where} WHERE (build_id) = ?", (self.ids[2],))

        results = c.fetchall()

        if lookup and results[0] != "None": # if the result is an id, lookup the name
            for key, value in self.combo_boxes.items():
                if value[1] == lookup:
                    print(value)
                    print(results)   # TODO: this is where i left off, i think. Fix this code
                    query2 = f"SELECT {value[1]} FROM {value[2]} WHERE {value[0]} = ?"
                    c.execute(query2, (results[0][0],))
                    results = c.fetchall()
        
        conn.close()
        return results[0] if results else None


    def update_id(self, ship):
        """ Gets The Ship ID Of What Ship Is Selected """
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("SELECT id, location_row_ID, build_id FROM wrecks WHERE name = ?", (ship,))
        ids = c.fetchone()
        conn.close()
        return ids
    

    def update_ship_info(self, name):
        """Update both name and id when ship selection changes"""
        self.name = name
        self.ids = self.update_id(name)