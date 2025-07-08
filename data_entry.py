from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QTabWidget, QLineEdit, QComboBox, QFormLayout
from PyQt5.QtCore import pyqtSignal
import sqlite3

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
                "ship_name": QLineEdit(),
                "year_lost": QLineEdit(),
                "date_lost": QLineEdit(),
                "final_result": QLineEdit()
            },
            "location": {
                "region": QComboBox(),
                "country": QComboBox(),
                "district": QComboBox(),
                "local_location": QComboBox(),
                "details_of_location": QLineEdit(),
                "reported_coordinates": QLineEdit(),
                "coordinate_confidence": QComboBox(),
                "verified_coordinates": QLineEdit(),
                "reported_depth": QLineEdit(),
                "latitude": QLineEdit(),
                "longitude": QLineEdit(),
                "coordinate_type": QComboBox()
            },
            "construction": {
                "material": QComboBox(),
                "wood_type": QComboBox(),
                "fastening": QComboBox(),
                "sheathing": QComboBox(),
                "armament": QLineEdit(),
                "ship_purpose": QComboBox(),
                "ship_type": QComboBox(),
                "tonnage": QLineEdit(),
                "propulsion": QComboBox(),
                "engine_type": QComboBox(),
                "length": QLineEdit(),
                "breadth": QLineEdit(),
                "hold_depth": QLineEdit(),
                "build_year": QLineEdit(),
                "builder": QLineEdit(),
                "shipyard": QLineEdit(),
                "ship_documents": QLineEdit(),
                "other_details": QLineEdit()
            },
            "wreck_event": {
                "sequence_of_events": QLineEdit(),
                "historical_event": QLineEdit(),
                "other_details": QLineEdit()
            },
            "registration": {
                "nation": QComboBox(),
                "registered_port": QComboBox(),
                "registration_number": QLineEdit(),
                "owners": QLineEdit(),
                "previous_names": QLineEdit(),
                "sahris_id": QLineEdit()
            },
            "personnel": {
                "captain": QLineEdit(),
                "commander": QLineEdit(),
                "crew": QLineEdit(),
                "passengers": QLineEdit(),
                "number_aboard": QLineEdit(),
                "casualties": QLineEdit(),
                "burial_location": QLineEdit()
            },
            "archaeology": {
                "archaeologists": QLineEdit(),
                "artefacts": QLineEdit(),
                "cargo": QLineEdit(),
                "year_salvaged": QLineEdit(),
                "salvor": QLineEdit(),
                "other_details": QLineEdit()
            },
            "sources": {
                "images": QPushButton("Add Photos"),
                "caption": QLineEdit(),
                "other_sources": QLineEdit()
            }
        }

        # a dict that shows what data to get, and where, based on the form
        boxes = {
            "region": ["ocean_name", "oceans"],
            "country": ["country_name", "countries"],
            "district": ["district_name", "districts"],
            "local_location": ["local_name", "local"],
            "coordinate_confidence": ["confidence", "confidence"],
            "material": ["material_name", "materials"],
            "wood_type": ["name", "wood_types"],
            "fastening": ["fastening_name", "fastening"],
            "sheathing": ["sheathing_name", "sheathing"],
            "ship_purpose": ["reason", "purpose"],
            "ship_type": ["type_name", "type"],
            "propulsion": ["propulsion_name", "propulsion"],
            "engine_type": ["engine_name", "engines"],
            "nation": ["nation", "extras"],
            "registered_port": ["registered_port", "wrecks"]
        }

        # Create tabs for grouped sections of the form, rather than one extremely long form
        form_sections = QTabWidget()

        for section_name, fields in self.sections.items():
            # layout the tabs
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab.setLayout(tab_layout)
            form_sections.addTab(tab, section_name)

            form = QFormLayout()
        
            for key, widget in fields.items(): # layout the inputs in each tab
                if isinstance(widget, QComboBox): # if its a box, find the right places to gather data
                    if key in boxes:
                        what = boxes[key][0] # what to gather
                        where = boxes[key][1] # where to gather
                        query = f"SELECT {what} FROM {where}" #create the query for the prompt
                        conn = sqlite3.connect("shipwrecks.db")
                        c = conn.cursor()
                        c.execute(query)
                        data = c.fetchall()

                        # add the data to the dropdown lists
                        widget.addItem("")
                        for row in data:
                            widget.addItem(row[0])

                    form.addRow(key.replace('_', ' ').capitalize(), widget)
            tab_layout.addLayout(form)
                #elif i[1] == QLineEdit:
                    # place i + : 
                    # place text box
                #else: # else i is a button in images
                    # place placeholder
                    # place button
                    # connect it to onclick function

                
        layout.addWidget(form_sections)