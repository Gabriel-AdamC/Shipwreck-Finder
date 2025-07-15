import os
import shutil  
import uuid
from PyQt5.QtWidgets import (
      QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
      QTabWidget, QLineEdit, QComboBox, QFormLayout,
      QFileDialog)
from PyQt5.QtCore import pyqtSignal, QDir
import sqlite3
from helpers import location_change, get_country_id_by_name, get_ocean_id_by_name

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
                "date_lost": QLineEdit()
            },
            "location": {
                "ocean": QComboBox(),
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
            "ocean": ["ocean_id, ocean_name", "oceans"],
            "country": ["country_id, country_name", "countries"],
            "district": ["district_id, district_name", "districts"],
            "local_location": ["local_id, local_name, country_id", "local"],
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

        location_keys = {
            "ocean": "oceans",
            "country": "countries",
            "local_location": "local"
        }

        # Create tabs for grouped sections of the form, rather than one extremely long form
        form_sections = QTabWidget()

        locations = ["ocean", "country", "district", "local_location"]

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

                        if key in location_keys:
                            setattr(self, location_keys[key], data)

                        # add the data to the dropdown lists
                        widget.addItem("")
                        for row in data:
                            if key in locations: # locations have id and name
                                widget.addItem(row[1])
                            else: # everything else just has name
                                widget.addItem(row[0])

                    form.addRow(key.replace('_', ' ').capitalize(), widget)

                    # Here on manages the hierarchy in the changing of locations
                    if key in locations:
                        # convert input names to allow calling of helper function
                        if key ==  "ocean":
                            self.oceans_input = widget
                        elif key == "country":
                            self.countries_input = widget
                        elif key == "local_location":
                            self.local_input = widget
                        
                        # Gather the junction data to check the hierarchy
                        conn = sqlite3.connect("shipwrecks.db")
                        c = conn.cursor()
                        c.execute("""SELECT * FROM country_ocean""")
                        self.country_ocean = c.fetchall()

                        source_key = key
                        signifier = "_"
                        new_key = key.split(signifier)[0]
                        widget.currentTextChanged.connect(lambda _, sk=source_key: self.hierarchy(sk))

                elif isinstance(widget, QLineEdit):
                    form.addRow(key.replace('_', ' ').capitalize(), widget)
                else: # the only other widget is a button
                    btn = QPushButton("Add Photos")
                    btn.clicked.connect(self.add_photo)
                    form.addRow(key, btn)
            
            tab_layout.addLayout(form)
        
        submit = QPushButton("submit")
        warn = QLabel("Please only click submit once you have filled as much as you would like from EACH tab")
                       
        layout.addWidget(form_sections)
        layout.addWidget(warn)
        layout.addWidget(submit)

        submit.clicked.connect(self.submit)
        

    def add_photo(self, filename=None):
        """adds photos to the page"""
        # Get the photo
        filename, _ = QFileDialog.getOpenFileName(self, 'Select Photo', QDir.currentPath(), 'Images (*.png *.jpg)')
        if not filename:
            return
        
        # Create the directory if there isnt one 
        images_dir = "images"
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        # Create a unique filename
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        local_path = os.path.join(images_dir, unique_filename)

        # copy the file
        shutil.copy2(filename, local_path)

    
    def submit(self):
        """ Handle the form submission by gathering non blank values """
        # dict to correlate form to db
        form_db = {
            # wrecks tab
            "kraken_id": {"wrecks", "kraken_id"},
            "ship_name": {"wrecks", "name"},
            "year_lost": {"wrecks", "year_lost"},
            "date_lost": {"wrecks", "date_lost"},
            # location tab   
            "ocean": {"locations", "ocean_id"},
            "country": {"locations", "country_id"},
            "district": {"locations", "district_id"},
            "local_location": {"locations", "local_id"},
            "details_of_location": {"locations", "details"},
            "reported_coordinates": {"locations", "reported_coords"},
            "coordinate_confidence": {"locations", "coord_conf"},
            "verified_coordinates": {"locations", "verified_coords"},
            "reported_depth": {"wrecks", "reported_depth"},
            "latitude": {"wrecks", "y_coord"},
            "longitude": {"wrecks", "x_coord"},
            "coordinate_type": {"locations", "coord_type"},
            # materials tab
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
            "other_details": QLineEdit(),
            # wreck event tab
            "sequence_of_events": QLineEdit(),
            "historical_event": QLineEdit(),
            "other_details": QLineEdit(),
            # registration tab
            "nation": QComboBox(),
            "registered_port": QComboBox(),
            "registration_number": QLineEdit(),
            "owners": QLineEdit(),
            "previous_names": QLineEdit(),
            "sahris_id": QLineEdit(),
            # personnel tab
            "captain": QLineEdit(),
            "commander": QLineEdit(),
            "crew": QLineEdit(),
            "passengers": QLineEdit(),
            "number_aboard": QLineEdit(),
            "casualties": QLineEdit(),
            "burial_location": QLineEdit(),
            # archaeology tab
            "archaeologists": QLineEdit(),
            "artefacts": QLineEdit(),
            "cargo": QLineEdit(),
            "year_salvaged": QLineEdit(),
            "salvor": QLineEdit(),
            "other_details": QLineEdit(),
            # sources tab
            "images": QPushButton("Add Photos"),
            "caption": QLineEdit(),
            "other_sources": QLineEdit()
        }



    
    def hierarchy(self, source):
        source_mapping = {
            "ocean": "ocean",
            "country": "country", 
            "local_location": "local"
        }
        
        mapped_source = source_mapping.get(source, source)

        location_change(
            mapped_source,  
            self.oceans_input.currentText().strip(),
            self.countries_input.currentText().strip(),
            self.local_input.currentText().strip(),
            self.oceans,
            self.countries,
            self.local,
            self.country_ocean,
            self.oceans_input,
            self.countries_input,
            self.local_input,
            get_ocean_id_by_name=lambda name: get_ocean_id_by_name(name, self.oceans),
            get_country_id_by_name=lambda name: get_country_id_by_name(name, self.countries),
            placeholder={
                "ocean": "",
                "country": "",
                "local": ""
            }
        )