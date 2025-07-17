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


#TODO: ADD TRADE ROUTES TO DDATA ENTRY


class DataEntryWindow(QWidget):

    switch_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.entry_ui(layout)
        self.selcted_images = []

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

        # store the image for db insertion
        self.selected_images.append(local_path)

    
    def submit(self):
        """ Handle the form submission by gathering non blank values """
        # dict to correlate form to db
        form_db = {
            # wrecks tab
            "kraken_id": ("wrecks", "kraken_id", None),
            "ship_name": ("wrecks", "name", None),
            "year_lost": ("wrecks", "year_lost", None),
            "date_lost": ("wrecks", "date_lost", None),
            # location tab   
            "ocean": ("locations", "ocean_id", "oceans"),
            "country": ("locations", "country_id", "countries"),
            "district": ("locations", "district_id", "districts"),
            "local_location": ("locations", "local_id", "local"),
            "details_of_location": ("locations", "details", None),
            "reported_coordinates": ("locations", "reported_coords", None),
            "coordinate_confidence": ("locations", "coord_conf", "confidence"),
            "verified_coordinates": ("locations", "verified_coords", None),
            "reported_depth": ("wrecks", "reported_depth", None),
            "latitude": ("wrecks", "y_coord", None),
            "longitude": ("wrecks", "x_coord", None),
            "coordinate_type": ("locations", "coord_type", "coord_type"),
            # materials tab
            "material": ("builds", "material_id", "materials"),
            "wood_type": ("builds", "wood_id", "wood_types"),
            "fastening": ("builds", "fastening_id", "fastening"),
            "sheathing": ("builds", "sheathing_id", "sheathing"),
            "armament": ("extras", "armaments", None),
            "ship_purpose": ("builds", "purpose_id", "purpose"),
            "ship_type": ("builds", "type_id", "type"), 
            "tonnage": ("extras", "tonnage", None),
            "propulsion": ("builds", "propulsion_id", "propulsion"),
            "engine_type": ("builds", "engine_id", "engines"),
            "length": ("extras", "length", None),
            "breadth": ("extras", "breadth", None), 
            "hold_depth": ("extras", "hold_depth", None),
            "build_year": ("extras", "build_year", None),
            "builder": ("extras", "builder", None),
            "shipyard": ("extras", "shipyard", None),
            "ship_documents": ("builds", "ship_docs", None),
            "other_details": ("builds", "ship_details", None),
            # wreck event tab
            "sequence_of_events": ("extras", "sequence_of_wreck", None),
            "historical_event": ("extras", "historical_event", None),
            "other_details": ("extras", "notes", None),
            # registration tab
            "nation": ("extras", "nation", None),
            "registered_port": ("wrecks", "registered_port", None),
            "registration_number": ("extras", "registration_number", None),
            "owners": ("extras", "owners", None),
            "previous_names": ("extras", "previous_names", None),
            "sahris_id": ("extras", "sahris_id", None),
            # personnel tab
            "captain": ("extras", "captain", None),
            "commander": ("extras", "commander", None),
            "crew": ("extras", "crew", None),
            "passengers": ("extras", "passengers", None),
            "number_aboard": ("extras", "total_aboard", None),
            "casualties": ("extras", "casualties", None),
            "burial_location": ("wrecks", "burial_location", None),
            # archaeology tab
            "archaeologists": ("extras", "archaeologist", None),
            "artefacts": ("extras", "artefacts", None),
            "cargo": ("voyage", "cargo", None),
            "year_salvaged": ("extras", "year_salvaged", None),
            "salvor": ("extras", "salvor", None),
            "other_details": ("misc", "details", None),
            # sources tab
            "images": ("images", "image_path", "multiple", None),
            "caption": ("images", "caption", None),
            "other_sources": ("images", "source", None)
        }

        #TODO I need to iterate and store in a list.
        # first locations
            # if mapping[2] == None: continue
            # else lookup id with mapping[2]
            # at the end store the locations id
        # then builds
            # same as above
        # then wrecks
            # same as above but insert into builds and locations their respective ids
        # then the rest using the above
            # same as above but with ship_id

        # most tables need ship_id, so I need to do wrecks sooner than most tables,
        # but wrecks needs locations_row_ID and builds_id
        # so I need to do those first. Hence the order of the code below

        #TODO:Make it work with NOT NULL items. 
        wrecks = {}
        locations = {}
        builds = {}
        rest = {}
        location_id =None
        build_id = None
        ship_id = None

        for section_name, fields in self.sections.items():
            
            for key, widget in fields.items():

                if key in form_db:
                    table, column, lookup = form_db[key][:3]

                    value = self.get_widget_value(widget, key)
                    if value:
                        if lookup:
                            value = self.get_id_by_name(value, lookup)
                        if table == "wrecks":
                            wrecks[column] = value
                        elif table == "locations":
                            locations[column] = value
                        elif table == "builds":
                            builds[column] = value
                        else:
                            if table not in rest:
                                rest[table] = {}
                            rest[table][column] = value
        
        if locations:
            columns = ", ".join(locations.keys()) # creates a list of column names
            placeholders = ", ".join(["?" for _ in locations]) # creates a list of ? to avoid sql injection
            values = tuple(locations.values()) # creates a tuple of all the data

            query = f"INSERT INTO locations ({columns}) VALUES ({placeholders})"
            conn = sqlite3.connect("shipwrecks.db")
            c = conn.cursor()
            c.execute(query, values)
            location_row_ID = c.lastrowid
            conn.commit()
            conn.close()

        if builds:
            columns = ", ".join(builds.keys())
            placeholders = ", ".join(["?" for _ in builds])
            values = tuple(builds.values())

            query = f"INSERT INTO builds ({columns}) VALUES ({placeholders})"
            conn = sqlite3.connect("shipwrecks.db")
            c = conn.cursor()
            c.execute(query, values)
            build_id = c.lastrowid
            conn.commit()
            conn.close()

        if wrecks:
            build_id = build_id if build_id is not None else 0 # oceans always has to be inputted, but builds is optional
            columns = ", ".join(wrecks.keys())
            placeholders = ", ".join(["?" for _ in wrecks])
            values = tuple(wrecks.values())

            query = f"INSERT INTO wrecks ({columns}, build_id, location_row_ID) VALUES ({placeholders}, ?, ?)"
            conn = sqlite3.connect("shipwrecks.db")
            c = conn.cursor()
            c.execute(query, values + (build_id, location_row_ID))
            ship_id = c.lastrowid
            conn.commit()
            conn.close()

        if rest:
            for table_name, table_data in rest.items():
                if table_data:
                    columns = ", ".join(table_data.keys())
                    placeholders = ", ".join(["?" for _ in table_data])
                    values = tuple(table_data.values())

                    query = f"INSERT INTO {table_name} ({columns}, ship_id) VALUES ({placeholders}, ?)"

                    conn = sqlite3.connect("shipwrecks.db")
                    c = conn.cursor()
                    c.execute(query, values + (ship_id,))

                    conn.commit()
                    conn.close()

                        

                
                    


    def get_widget_value(self, widget, key):
        if isinstance(widget, QLineEdit):
            if widget.text() != "":
                value = widget.text()
                return value

        elif isinstance(widget, QComboBox):
            if widget.currentText() != "":
                value = widget.currentText()
                return value
            

    def get_id_by_name(self, value, lookup):
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute(f"SELECT * FROM {lookup}")
        data = c.fetchall()
        for row in data:
            if value in row:
                for field in row:
                    if isinstance(field, int):
                        conn.close()
                        return field 

    
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