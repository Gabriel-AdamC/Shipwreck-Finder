import sqlite3
import os
from dicts import boxes_dict, input_dict, sections
from PyQt5.QtWidgets import (
    QLabel, QWidget, QComboBox, QLineEdit, QScrollArea,QTabWidget, QGridLayout, QVBoxLayout,
    QFormLayout, QPushButton, QApplication, QFrame, QHBoxLayout, QDialog
)
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from helpers import location_change, get_country_id_by_name, get_ocean_id_by_name, get_widget_value, get_id_by_name, link_im_cap

class ClickableImageLabel(QLabel):
    """ Custom QLabel That Emits A Signal When Clicked """
    clicked = pyqtSignal(str, str)  # image_path and caption

    def __init__(self, image_path, caption):
        super().__init__()
        self.image_path = image_path
        self.caption = caption
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path, self.caption)


class FullScreenViewer(QWidget):
    """ View An Image In FullScreen Along With The Associated Caption """

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # close button
        close_btn = QPushButton("x")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: none;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 255);
            }
        """)
        close_btn.clicked.connect(self.close)

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(close_btn)
        layout.addLayout(top_layout)

        # image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label, 1)

        # Caption label
        self.caption_label = QLabel()
        self.caption_label.setAlignment(Qt.AlignCenter)
        self.caption_label.setWordWrap(True)
        self.caption_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            padding: 10px;
            background-color: rgba(0, 0, 0, 150);
            border-radius: 5px;
        """)
        layout.addWidget(self.caption_label)
        
        self.setLayout(layout)

    def show_image(self, image_path, caption):
        """ Display The Image And Caption """
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            screen_size = QApplication.desktop().screenGeometry()
            scaled_pixmap = pixmap.scaled(
                screen_size.width() - 100,
                screen_size.height() - 200,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

            self.caption_label.setText(caption)
            self.showFullScreen()

    def keyPressEvent(self, event):
        """ Close The Image """
        if event.key() == Qt.Key_Escape:
            self.close()


class DataDisplayWidget(QWidget):
    """ Reusable widget for displaying tabbed data with images """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        self.info_sections = QTabWidget()
        self.main_layout.addWidget(self.info_sections)
        
        self.full_screen_viewer = FullScreenViewer()
        self.buttons = None
        
        # Data storage
        self.name = None
        self.ids = None
        self.sections = None
        self.combo_boxes = None
        self.db_path = None

        self.deleted_images = []
        self.selected_images = []

        
    def display(self, name, ids, sections_func, input_dict_func, boxes_dict_func, 
                db_path="shipwrecks.db", edit_callback=None, what=None):
        """ 
        Sets The Data In The Tabs 
        
        Args:
            name: The name identifier for the main record
            ids: List/tuple of IDs [ship_id, location_id, build_id]
            sections_func: Function that returns sections dictionary
            input_dict_func: Function that returns input dictionary
            boxes_dict_func: Function that returns combo boxes dictionary
            db_path: Path to the database file
            edit_callback: Function to call when edit button is clicked
            delete_callback: Function to call when delete button is clicked
        """

        # Handle hierarchy
        location_keys = {
            "ocean": "oceans",
            "country": "countries",
            "local_location": "local"
        }

        locations = ["ocean", "country", "district", "local_location"]
        
        # Store the data
        self.name = name
        self.ids = ids
        self.db_path = db_path
        
        # clear every time the page is called to allow for changing ships
        self.info_sections.clear() 
        if hasattr(self, "buttons") and self.buttons:
            self.main_layout.removeItem(self.buttons)
            # Clear all widgets from the layout
            while self.buttons.count():
                child = self.buttons.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # grab all the sections
        self.sections = sections_func()
        data = input_dict_func()
        self.combo_boxes = boxes_dict_func()

        # for each section
        for section_name, fields in self.sections.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab.setLayout(tab_layout)
            self.info_sections.addTab(tab, section_name)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            form = QFormLayout()

            if section_name == "sources":
                """ Generate The Sources Tab Separately, It Has Images """
                title = QLabel("Image Gallery")
                title.setAlignment(Qt.AlignCenter)
                title.setFont(QFont("Arial", 18, QFont.Bold))
                tab_layout.addWidget(title)

                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

                # Limit the size otherwise it goes offscreen
                scroll_area.setMaximumHeight(400) 
                scroll_area.setMinimumHeight(200)

                # Container for grid
                container = QWidget()
                grid_layout = QGridLayout()
                container.setLayout(grid_layout)
                
                # Add images to grid
                self.create_grid(grid_layout)
                
                scroll_area.setWidget(container)
                tab_layout.addWidget(scroll_area)

                continue

            for key, widget in fields.items():
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

                    # set what the page looks like based on where the user comes from 
                    if what == "see":
                        box = QLabel(info)
                        box.setWordWrap(True)# allow the info to wrap to prevent screen runoff

                    elif what == "edit":
                        box = widget
                        if isinstance(widget, QComboBox):
                            box.addItem(info)

                            column = self.combo_boxes[key][1]
                            table = self.combo_boxes[key][2]
                            query = f"SELECT {column} FROM {table}"
                            conn = sqlite3.connect("shipwrecks.db")
                            c = conn.cursor()
                            c.execute(query)
                            options = c.fetchall()

                            if key in location_keys:
                                setattr(self, location_keys[key], options)

                            if key == "material":
                                self.materials_input = widget
                            if key == "wood_type":
                                self.wood_types_input = widget

                            for item in options:
                                untupled = item[0]
                                if untupled == info:
                                    continue
                                box.addItem(untupled)
                                
                            # hierarchy for the combo boxes that need them
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
                                widget.currentTextChanged.connect(lambda _, sk=source_key: self.hierarchy(sk))

                        elif isinstance(widget, QLineEdit):
                            box.setText(info)

                            if key == "caption": # set the names of these two for later use in update
                                self.caption_input = widget
                            elif key == "other_sources": 
                                self.source_input = widget

                        else: # only other is TextEdit
                            box.setPlainText(info)

                    form.addRow(key.replace("_", " ").capitalize(), box)
            
            tab_layout.addLayout(form)

        # have an edit and delete button if callbacks are provided
        if edit_callback:
            self.buttons = QHBoxLayout()

            if what == "see":
                edit = QPushButton("Edit This Wreck")
                self.buttons.addWidget(edit)
                edit.clicked.connect(lambda: edit_callback(self.name, self.ids))

            elif what == "edit":
                update = QPushButton("Update Information")
                self.buttons.addWidget(update)
                update.clicked.connect(self.update)

            self.main_layout.addLayout(self.buttons)


    def populate(self, where, what, lookup, key):
        """ Populates The Form with SQL Queries """

        # get the data
        conn = sqlite3.connect(self.db_path)
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
    

    def create_grid(self, grid_layout):
        """ Creates The Grid Of Images """

        columns = 3
        image_data = link_im_cap(self.ids[0], None, None)

        for i, (image_path, caption) in enumerate(image_data):
            row = i // columns
            col = i % columns

            # convert from tuple to str
            if isinstance(image_path, tuple):
                actual_path = image_path[0]  
            else:
                actual_path = image_path

            if isinstance(caption, tuple):
                actual_caption = caption[0]
            else:
                actual_caption = caption

            # create a frame for each image caption pair
            frame = QFrame()
            frame.setFrameStyle(QFrame.Box)
            frame.setLineWidth(1)
            frame.setMaximumSize(180, 200)
            frame_layout = QVBoxLayout()
            frame_layout.setContentsMargins(5, 5, 5, 5)
            frame.setLayout(frame_layout)

            image_label = ClickableImageLabel(actual_path, actual_caption)

            # load and scale the image
            pixmap = QPixmap(120, 90)
            pixmap.fill(QColor(200, 200, 200))

            # try to load the actual image
            actual_pixmap = QPixmap(actual_path)
            if not actual_pixmap.isNull():
                pixmap = actual_pixmap.scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            image_label.setPixmap(pixmap)
            image_label.setFixedSize(120, 90)
            image_label.setScaledContents(True)

            image_label.clicked.connect(self.full_screen)

            # set the captions
            caption_label = QLabel(actual_caption)
            caption_label.setWordWrap(True)
            caption_label.setAlignment(Qt.AlignCenter)
            caption_label.setMaximumWidth(120)
            caption_label.setMaximumHeight(60)
            caption_label.setStyleSheet("""
                padding: 5px;
                font-size: 12px;
                background-color: #f0f0f0;
                border-radius: 3px;
            """)

            frame_layout.addWidget(image_label)
            frame_layout.addWidget(caption_label)

            grid_layout.addWidget(frame, row, col)


    def full_screen(self, image_path, caption):
        self.full_screen_viewer.show_image(image_path, caption)
    

    def delete_record(self):
        """ Deletes The Wreck From The Database Completely """
        tables = ["wrecks", "builds", "locations", "voyage", "extras", "images"]
        confusing = ["wrecks", "builds", "locations"] # These will all have different queries

        try:
            # i need the location_row_ID and the build_id 
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT location_row_ID, build_id FROM wrecks WHERE id = ?", (self.ids[0],))
            result = c.fetchone()

            # delete the local images as well
            c.execute("SELECT image_path FROM images WHERE ship_id = ?", (self.ids[0],))
            image_paths = c.fetchall()

            if not result:
                print("Could not find location_row_ID or build_id")
                return False
            
            location_id, build_id = result

            # delete the image
            if image_paths:
                try:
                    for path_tuple in image_paths:
                        path = path_tuple[0]
                        if os.path.exists(path):
                            os.remove(path)
                except OSError as e:
                    print(f"Error deleting images: {e}")
                    # but continue with the rest of the deletion even if error here
            
            for table in tables:
                if table not in confusing:
                    query = f"DELETE FROM {table} WHERE ship_id = ?"
                    c.execute(query, (self.ids[0],))
                elif table == "locations":
                    query = "DELETE FROM locations WHERE location_row_ID = ?"
                    c.execute(query, (location_id,))
                elif table == "builds":
                    query = "DELETE FROM builds WHERE build_id = ?"
                    c.execute(query, (build_id,))
                else: # only other table is wrecks
                    query = "DELETE FROM wrecks WHERE id = ?"
                    c.execute(query, (self.ids[0],))

            conn.commit()
            return True
        
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
                print(f"Database error: {e}")
                return False
        
        except Exception as e:
            if conn:
                conn.rollback()
                print(f"Unexpected error: {e}")
                return False

        finally:
            if conn:
                conn.close()

    
    def hierarchy(self, source):
        source_mapping = {
            "ocean": "ocean",
            "country": "country", 
            "local_location": "local"
        }
        
        mapped_source = source_mapping.get(source, source)

        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("SELECT * FROM local")
        local = c.fetchall()
        c.execute("SELECT * FROM countries")
        countries = c.fetchall()
        c.execute("SELECT * FROM oceans")
        oceans = c.fetchall()
        conn.close()

        location_change(
            mapped_source,  
            self.oceans_input.currentText().strip(),
            self.countries_input.currentText().strip(),
            self.local_input.currentText().strip(),
            oceans,
            countries,
            local,
            self.country_ocean,
            self.oceans_input,
            self.countries_input,
            self.local_input,
            get_ocean_id_by_name=lambda name: get_ocean_id_by_name(name),
            get_country_id_by_name=lambda name: get_country_id_by_name(name),
            placeholder={
                "ocean": "",
                "country": "",
                "local": ""
            }
        )


    def update(self):
        """ Handle the form submission by gathering non blank values """
        # dict to correlate form to db
        form_db = input_dict()
        print("updating")

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
                        value = get_widget_value(widget, key)

                        if value:
                            if lookup:
                                value = get_id_by_name(value, lookup)
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
                set_clause = ", ".join([f"{col}=?" for col in locations.keys()])
                query = f"UPDATE locations SET {set_clause} WHERE location_row_ID = ?"
                c.execute(query, tuple(locations.values()) + (self.ids[1],))

            if builds: # TODO: idk if this works for ComboBoxes, works for locations though?
                set_clause = ", ".join([f"{col}=?" for col in builds.keys()])
                query = f"UPDATE builds SET {set_clause} WHERE build_id = ?"
                c.execute(query, tuple(builds.values()) + (self.ids[2],))

            if wrecks:
                set_clause = ", ".join([f"{col}=?" for col in wrecks.keys()])
                query = f"UPDATE wrecks SET {set_clause} WHERE id = ?"
                c.execute(query, tuple(wrecks.values()) + (self.ids[0],))

            if rest:
                for table_name, table_data in rest.items():
                    if table_data:
                        if table_name == "images" and hasattr(self, "selected_images") and self.selected_images:

                            # TODO: This may need to change when  I implement multiple captions and sources
                            current_caption = self.caption_input.text() if hasattr(self, "caption_input") else ""
                            current_source = self.source_input.text() if hasattr(self, "source_input") else "" 

                            # Delete images
                            for path in self.deleted_images:
                                query = f"DELETE FROM images WHERE image_path = ?"
                                c.execute(query, (path,))
                                # delete the local copy
                                if os.path.exists(path):
                                    try:
                                        os.remove(path)
                                    except OSError as e:
                                        print(f"Error: {e}")

                            for image_data in self.selected_images:
                                # Check if image already exists for this ship
                                check_query = "SELECT id FROM images WHERE image_path = ?"
                                c.execute(check_query, (image_data['image_path'],))
                                existing_image = c.fetchone()

                                if existing_image:
                                    # Update existing image
                                    query = "UPDATE images SET caption = ?, source = ? WHERE id = ?"
                                    c.execute(query, (current_caption, current_source, existing_image[0]))
                                else:
                                    # Insert new image
                                    query = "INSERT INTO images (image_path, caption, source, ship_id) VALUES (?, ?, ?, ?)"
                                    c.execute(query, (
                                        image_data['image_path'],
                                        current_caption,
                                        current_source,
                                        self.ids[0]
                                    ))
                        
                            # Clear selected images after insertion
                            self.selected_images.clear()
                            self.deleted_images.clear()
                            continue

                        # Check if a record already exists
                        check_query = f"SELECT COUNT(*) FROM {table_name} WHERE ship_id = ?"
                        c.execute(check_query, (self.ids[0],))
                        exists = c.fetchone()[0] > 0

                        columns = ", ".join(table_data.keys())
                        placeholders = ", ".join(["?" for _ in table_data])
                        values = tuple(table_data.values())

                        if exists:
                            # Build UPDATE query
                            set_clause = ", ".join([f"{col} = ?" for col in table_data.keys()])
                            query = f"UPDATE {table_name} SET {set_clause} WHERE ship_id = ?"
                            c.execute(query, tuple(table_data.values()) + (self.ids[0],))
                        else:
                            # INSERT new record
                            query = f"INSERT INTO {table_name} ({columns}, ship_id) VALUES ({placeholders}, ?)"
                            c.execute(query, values + (self.ids[0],))

            conn.commit()
        
            # TODO: Send a message to the user

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
        dlg = QDialog()
        message = f"Error: {e} \n Please Try again"
        dlg.setWindowTitle("Error")
        er_layout = QVBoxLayout()
        er_layout.addWidget(message)
        dlg.setLayout(er_layout)
        dlg.exec_()
        