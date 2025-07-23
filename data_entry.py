import os
import shutil  
import uuid
from PyQt5.QtWidgets import (
      QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
      QTabWidget, QLineEdit, QComboBox, QFormLayout,
      QFileDialog, QDialog)
from PyQt5.QtCore import pyqtSignal, QDir
from PyQt5.QtGui import QPixmap
import sqlite3
from helpers import location_change, get_country_id_by_name, get_ocean_id_by_name
from dicts import sections, boxes_dict, input_dict


class DataEntryWindow(QWidget):

    switch_signal = pyqtSignal(str, object)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.entry_ui(layout)
        self.selected_images = []
        self.image_labels = []

    def entry_ui(self, layout):
        """ Set up the UI for data entry. """
        # Creates the buttons to change between parts of the app
        self.page_change = QHBoxLayout()
        self.btn_map = QPushButton("Map")
        self.btn_map.clicked.connect(lambda: self.switch_signal.emit("map", None))
        self.btn_entry = QPushButton("Data Entry")
        self.btn_entry.clicked.connect(lambda: self.switch_signal.emit("data_entry", None))
        self.page_change.addWidget(self.btn_map)
        self.page_change.addWidget(self.btn_entry)
        layout.addLayout(self.page_change)

        # I want to loop through the form inputs, so that I can avoid hardcoding each one.
        # So here is a dict of all the info I need to effectively loop and dynamically create
        self.sections = sections()

        # a dict that shows what data to get, and where, based on the form
        boxes = boxes_dict()

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

            if section_name == "sources": # create a reference so I can place pixmaps 
                self.sources_tab_layout = tab_layout
        
            for key, widget in fields.items(): # layout the inputs in each tab
                if isinstance(widget, QComboBox): # if its a box, find the right places to gather data
                    if key in boxes:

                        if key == "material":
                            self.materials_input = widget
                        if key == "wood_type":
                            self.wood_types_input = widget

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
                    if key == "caption":
                        self.caption_input = widget
                    elif key == "other_sources": 
                        self.source_input = widget
                else: # the only other widget is a button
                    btn = QPushButton("Add Photos")
                    btn.clicked.connect(self.add_photo)
                    form.addRow(key, btn)
            
            tab_layout.addLayout(form)
        
        if hasattr(self, "materials_input") and hasattr(self, "wood_types_input"):
            self.materials_input.currentTextChanged.connect(self.update_wood)
        
        submit = QPushButton("submit")
        warn = QLabel("Please only click submit once you have filled as much as you would like from EACH tab")
                       
        layout.addWidget(form_sections)
        layout.addWidget(warn)
        layout.addWidget(submit)

        submit.clicked.connect(self.submit)


    def update_wood(self, selected_material): # dynamically changes wood input table
        self.wood_types_input.clear()
        if selected_material.lower() == "wood":
            self.wood_types_input.addItem("")  
            # Query wood types from the database
            conn = sqlite3.connect("shipwrecks.db")
            c = conn.cursor()
            c.execute("SELECT name FROM wood_types")
            wood_types = c.fetchall()
            conn.close()
            for row in wood_types:
                self.wood_types_input.addItem(row[0])
        

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

        caption = self.caption_input.text() if hasattr(self, 'caption_input') else ""
        source = self.source_input.text() if hasattr(self, 'source_input') else ""
    
        # Store the complete image data for db insertion
        image_data = {
            'image_path': local_path,
            'caption': caption,
            'source': source
        }

        # display the image onto the pixmap
        pixmap = QPixmap()
        pixmap.load(local_path)
        label = QLabel()
        label.setPixmap(pixmap.scaled(200, 200, aspectRatioMode=1))
        self.sources_tab_layout.addWidget(label)
        self.image_labels.append(label)
    
        if not hasattr(self, 'selected_images'):
            self.selected_images = []
        self.selected_images.append(image_data)

    
    def submit(self):
        """ Handle the form submission by gathering non blank values """
        # dict to correlate form to db
        form_db = input_dict()

        # most tables need ship_id, so I need to do wrecks sooner than most tables,
        # but wrecks needs locations_row_ID and builds_id
        # so I need to do those first. Hence the order of the code below
 
        conn = None

        try:
            
            conn = sqlite3.connect("shipwrecks.db")
            c = conn.cursor()
            
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
                c.execute(query, values)
                location_row_ID = c.lastrowid

            if builds:
                columns = ", ".join(builds.keys())
                placeholders = ", ".join(["?" for _ in builds])
                values = tuple(builds.values())
                query = f"INSERT INTO builds ({columns}) VALUES ({placeholders})"
                c.execute(query, values)
                build_id = c.lastrowid

            if wrecks:
                build_id = build_id if build_id is not None else 0 # oceans always has to be inputted, but builds is optional
                columns = ", ".join(wrecks.keys())
                placeholders = ", ".join(["?" for _ in wrecks])
                values = tuple(wrecks.values())
                query = f"INSERT INTO wrecks ({columns}, build_id, location_row_ID) VALUES ({placeholders}, ?, ?)"
                c.execute(query, values + (build_id, location_row_ID))
                ship_id = c.lastrowid

            if rest:
                print(rest)
                for table_name, table_data in rest.items():
                    print(table_name, table_data)
                    if table_data:
                        if table_name == "images" and hasattr(self, "selected_images") and self.selected_images:

                            current_caption = self.caption_input.text() if hasattr(self, "caption_input") else ""
                            current_source = self.source_input.text() if hasattr(self, "source_input") else "" 
                    
                            # Insert each image with all its metadata
                            for image_data in self.selected_images:
                                query = "INSERT INTO images (image_path, caption, source, ship_id) VALUES (?, ?, ?, ?)"
                                c.execute(query, (
                                    image_data['image_path'],
                                    current_caption,
                                    current_source,
                                    ship_id
                                ))
                    
                            # Clear selected images after insertion
                            self.selected_images.clear()
                            continue

                        columns = ", ".join(table_data.keys())
                        placeholders = ", ".join(["?" for _ in table_data])
                        values = tuple(table_data.values())

                        query = f"INSERT INTO {table_name} ({columns}, ship_id) VALUES ({placeholders}, ?)"
                        c.execute(query, values + (ship_id,))

            conn.commit()
        
            # Clear form inputs after submission
            self.reset_fields()
            # send an alert to the user
            self.submit_message()

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
                self.error(e)
        
        except Exception as e:
            if conn:
                conn.rollback()
                self.error(e)

        finally:
            if conn:
                conn.close()

    
    def error(self, e):
        msg = QLabel("There was an error submitting the data. Please try again.")
        msg2 = QLabel("error: " + str(e))
        dlg = QDialog(self)
        dlg.setWindowTitle("Submission Error")
        error_layout = QVBoxLayout()
        error_layout.addWidget(msg)
        error_layout.addWidget(msg2)
        dlg.setLayout(error_layout)
        dlg.exec_()

    
    def submit_message(self):
        msg = QLabel("Data submitted successfully!")
        msg2 = QLabel("Please click reset on the map page to see the new data")
        dlg = QDialog(self)
        dlg.setWindowTitle("Submission Successful")
        final_layout = QVBoxLayout()
        final_layout.addWidget(msg)
        final_layout.addWidget(msg2)
        dlg.setLayout(final_layout)
        dlg.exec_()


    def reset_fields(self):
        """" resets all the inputs in the form"""
        for section_name, fields in self.sections.items():
            for key, widget in fields.items():
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)
        for label in getattr(self, "image_labels", []):
            label.deleteLater()
        self.image_labels = []


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