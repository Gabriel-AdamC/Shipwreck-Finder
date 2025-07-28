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

                    # I dont want to leave blank spaces on the page
                    if info is None:
                        info = "N/A"

                    # if its a year or measurement I want to keep it as is
                    if isinstance(info, int) or isinstance(info, float): 
                        info = str(info) 

                    form.addRow(key.replace("_", " ").capitalize(), QLabel(info))
            
            tab_layout.addLayout(form)


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

        results = c.fetchone()
        result = results[0] if results else None

        if lookup and result != None and isinstance(result, int): # if the result is an id, lookup the name
            for key, value in self.combo_boxes.items():
                if value[2] == lookup:
                    query2 = f"SELECT {value[1]} FROM {value[2]} WHERE {value[0]} = ?"
                    c.execute(query2, (result,))
                    names = c.fetchone()
                    name = names[0] if names else None
                    conn.close()
                    return name
        
        conn.close()
        return result


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