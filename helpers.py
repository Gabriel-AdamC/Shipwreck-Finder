import sqlite3
import os
from dicts import boxes_dict, input_dict, sections
from PyQt5.QtWidgets import QLabel, QWidget, QScrollArea,QTabWidget, QGridLayout, QVBoxLayout, QFormLayout, QPushButton, QApplication, QFrame, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSignal

def location_change(
        source,
        selected_ocean,
        selected_country,
        selected_local,
        oceans,
        countries,
        local,
        country_ocean,
        oceans_input,
        countries_input,
        local_input,
        get_ocean_id_by_name,
        get_country_id_by_name,
        placeholder=None
):
        """Update country and local dropdowns based on selected ocean or country."""

        # country => (country_id, country_name, ocean_id)
        # local => (local_id, local_name, country_id, ocean_id)
        # oceans => (ocean_id, ocean_name)

        selected_ocean = oceans_input.currentText().strip()
        selected_country = countries_input.currentText().strip()  
        selected_local = local_input.currentText().strip()

        # Set the placeholder texts if none were given
        if placeholder is None:
            placeholder = {
                "ocean": "All Oceans",
                "country": "All Countries",
                "local": "All Locals"
            }

        # Reset all dropdowns first to avoid duplication
        oceans_input.blockSignals(True)
        countries_input.blockSignals(True)
        local_input.blockSignals(True)

        # Store current selections to preserve them
        prev_country = countries_input.currentText().strip()
        prev_local = local_input.currentText().strip()
        prev_ocean = oceans_input.currentText().strip()

        if source == "ocean":
            
            if selected_ocean != placeholder.get("ocean", ""):
                # Filter countries that border selected ocean

                ocean_id = get_ocean_id_by_name(selected_ocean)

                if ocean_id is not None:
                    ocean_id = ocean_id[0]
                filtered_countries = [c for c in countries if c[0] in [co[0] for co in country_ocean if co[1] == ocean_id]]
                countries_input.clear()
                countries_input.addItem(placeholder.get("country", ""))
                for country in filtered_countries:
                    countries_input.addItem(country[1])
                
                # Preserve selection if it's still valid, otherwise reset
                if prev_country in [country[1] for country in filtered_countries]:
                    countries_input.setCurrentText(prev_country)
                else:
                    countries_input.setCurrentIndex(0)

                # Filter locals that also border same ocean
                country_ids = [co[0] for co in country_ocean if co[1] == ocean_id]
                filtered_locals = [l for l in local if l[2] in country_ids]
                local_input.clear()
                local_input.addItem(placeholder.get("local", ""))
                for local_item in filtered_locals:
                    local_input.addItem(local_item[1])
                
                # Preserve selection if it's still valid, otherwise reset
                if prev_local in [local_item[1] for local_item in filtered_locals]:
                    local_input.setCurrentText(prev_local)
                else:
                    local_input.setCurrentIndex(0)
            else:
                # "All Oceans" selected - reset countries and locals to show all options
                countries_input.clear()
                countries_input.addItem(placeholder.get("country", ""))
                for country in countries:
                    countries_input.addItem(country[1])
                countries_input.setCurrentIndex(0)  # Reset to placeholder

                local_input.clear()
                local_input.addItem(placeholder.get("local", ""))
                for local_item in local:
                    local_input.addItem(local_item[1])
                local_input.setCurrentIndex(0)  # Reset to placeholder

        elif source == "country":

            country_id = get_country_id_by_name(selected_country)

            if selected_country != placeholder.get("country", ""):
                # Filter oceans connected to this country
                if country_id is not None:
                    country_id = country_id[0]
                ocean_ids = [co[1] for co in country_ocean if co[0] == country_id]
                filtered_oceans = [o for o in oceans if o[0] in ocean_ids]
                oceans_input.clear()
                oceans_input.addItem(placeholder.get("ocean", ""))
                for ocean in filtered_oceans:
                    oceans_input.addItem(ocean[1])
                
                # Preserve selection if it's still valid, otherwise reset
                if prev_ocean in [ocean[1] for ocean in filtered_oceans]:
                    oceans_input.setCurrentText(prev_ocean)
                else:
                    oceans_input.setCurrentIndex(0)

                # Filter locals connected to this country
                filtered_locals = [l for l in local if l[2] == country_id]
                local_input.clear()
                local_input.addItem(placeholder.get("local", ""))
                for local_item in filtered_locals:
                    local_input.addItem(local_item[1])
                
                # Preserve selection if it's still valid, otherwise reset
                if prev_local in [local_item[1] for local_item in filtered_locals]:
                    local_input.setCurrentText(prev_local)
                else:
                    local_input.setCurrentIndex(0)
            else:
                # "All Countries" selected - reset oceans and locals to show all options
                oceans_input.clear()
                oceans_input.addItem(placeholder.get("ocean", ""))
                for ocean in oceans:
                    oceans_input.addItem(ocean[1])
                oceans_input.setCurrentIndex(0)  # Reset to placeholder

                local_input.clear()
                local_input.addItem(placeholder.get("local", ""))
                for local_item in local:
                    local_input.addItem(local_item[1])
                local_input.setCurrentIndex(0)  # Reset to placeholder

        elif source == "local":
            if selected_local != placeholder.get("local", ""):
                # Get local row
                local_row = next((l for l in local if l[1] == selected_local), None)
                if local_row:
                    country_id = local_row[2]
                    ocean_ids = [co[1] for co in country_ocean if co[0] == country_id]

                    # Set country to the one this local belongs to
                    filtered_country = next((c for c in countries if c[0] == country_id), None)
                    countries_input.clear()
                    countries_input.addItem(placeholder.get("country", ""))
                    if filtered_country:
                        countries_input.addItem(filtered_country[1])
                        countries_input.setCurrentText(filtered_country[1])

                    # Set oceans connected to this country
                    filtered_oceans = [o for o in oceans if o[0] in ocean_ids]
                    oceans_input.clear()
                    oceans_input.addItem(placeholder.get("ocean", ""))
                    for ocean in filtered_oceans:
                        oceans_input.addItem(ocean[1])
                    
                    # Preserve selection if it's still valid, otherwise reset
                    if prev_ocean in [ocean[1] for ocean in filtered_oceans]:
                        oceans_input.setCurrentText(prev_ocean)
                    else:
                        oceans_input.setCurrentIndex(0)
            else:
                # "All Locals" selected - reset oceans and countries to show all options
                oceans_input.clear()
                oceans_input.addItem(placeholder.get("ocean", ""))
                for ocean in oceans:
                    oceans_input.addItem(ocean[1])
                oceans_input.setCurrentIndex(0)  # Reset to placeholder

                countries_input.clear()
                countries_input.addItem(placeholder.get("country", ""))
                for country in countries:
                    countries_input.addItem(country[1])
                countries_input.setCurrentIndex(0)  # Reset to placeholder

                # Also reset local dropdown to show all options
                local_input.clear()
                local_input.addItem(placeholder.get("local", ""))
                for local_item in local:
                    local_input.addItem(local_item[1])
                local_input.setCurrentIndex(0)  # Reset to placeholder

        else:
            # No filters selected: show all
            oceans_input.clear()
            oceans_input.addItem(placeholder.get("ocean", ""))
            for ocean in oceans:
                oceans_input.addItem(ocean[1])
            oceans_input.setCurrentIndex(0)

            countries_input.clear()
            countries_input.addItem(placeholder.get("country", ""))
            for country in countries:
                countries_input.addItem(country[1])
            countries_input.setCurrentIndex(0)

            local_input.clear()
            local_input.addItem(placeholder.get("local", ""))
            for local_item in local:
                local_input.addItem(local_item[1])
            local_input.setCurrentIndex(0)

        oceans_input.blockSignals(False)
        countries_input.blockSignals(False)
        local_input.blockSignals(False)
        

def get_country_id_by_name(name):
    
    conn = sqlite3.connect("shipwrecks.db")
    c = conn.cursor()
    c.execute(f"SELECT country_id FROM countries WHERE country_name = ?", (name,))
    id = c.fetchone()
    conn.close()
    return id


def get_ocean_id_by_name(name):

    conn = sqlite3.connect("shipwrecks.db")
    c = conn.cursor()
    c.execute(f"SELECT ocean_id FROM oceans WHERE ocean_name = ?", (name,))
    id = c.fetchone()
    conn.close()
    return id


def change_height(widget):
    text_edit = widget
    
    # Get the document and ensure it's properly sized
    document = text_edit.document()
    
    # Set document width to match the text edit's content width
    content_width = text_edit.width() - text_edit.contentsMargins().left() - text_edit.contentsMargins().right() - 20  # Account for scrollbar
    document.setTextWidth(content_width)
    
    # Get the actual document height
    doc_height = int(document.size().height())
    
    # Add margins but no padding
    margins = text_edit.contentsMargins()
    frame_width = text_edit.frameWidth() * 2
    
    # Minimum height for at least one line
    font_metrics = text_edit.fontMetrics()
    min_height = font_metrics.lineSpacing() + margins.top() + margins.bottom() + frame_width
    
    height = max(min_height, doc_height + margins.top() + margins.bottom() + frame_width)
    
    text_edit.setFixedHeight(height)


def update_id(ship):
    """ Gets The Ship ID Of What Ship Is Selected """
    conn = sqlite3.connect("shipwrecks.db")
    c = conn.cursor()
    c.execute("SELECT id, location_row_ID, build_id FROM wrecks WHERE name = ?", (ship,))
    ids = c.fetchone()
    conn.close()
    return ids


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

                    # allow the info to wrap to prevent screen runoff
                    label = QLabel(info)
                    label.setWordWrap(True)

                    form.addRow(key.replace("_", " ").capitalize(), label)
            
            tab_layout.addLayout(form)

        # have an edit and delete button if callbacks are provided
        if edit_callback:
            self.buttons = QHBoxLayout()

            if edit_callback:
                edit = QPushButton("Edit This Wreck")
                self.buttons.addWidget(edit)
                edit.clicked.connect(lambda: edit_callback(self.name, self.ids))

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
        image_data = self.link_im_cap()

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

    def link_im_cap(self):
        """ Links The Images To The Captions And Returns A Tuple of (image_path, caption) """
        image_data = []

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT image_path FROM images WHERE ship_id = ?", (self.ids[0],))
        image_paths = c.fetchall()
        c.execute("SELECT caption FROM images WHERE ship_id = ?", (self.ids[0],))
        captions = c.fetchall()
        conn.close()

        for i, image_path in enumerate(image_paths):
            if i < len(captions):
                caption = captions[i]
            else: 
                caption = "No Caption Available"

            image_data.append((image_path, caption))
        
        return image_data

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


def delete_record_from_db(name, ids, db_path="shipwrecks.db"):
    """ 
    Standalone function to delete a record from the database 
    
    Args:
        name: The name identifier for the main record
        ids: List/tuple of IDs [ship_id, location_id, build_id]
        db_path: Path to the database file
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    tables = ["wrecks", "builds", "locations", "voyage", "extras", "images"]
    confusing = ["wrecks", "builds", "locations"]

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT location_row_ID, build_id FROM wrecks WHERE id = ?", (ids[0],))
        result = c.fetchone()

        # delete the local images as well
        c.execute("SELECT image_path FROM images WHERE ship_id = ?", (ids[0],))
        image_paths = c.fetchall()

        if not result:
            print("Could not find location_row_ID or build_id")
            return False
        
        location_id, build_id = result

        # delete the images
        if image_paths:
            try:
                for path_tuple in image_paths:
                    path = path_tuple[0]
                    if os.path.exists(path):
                        os.remove(path)
            except OSError as e:
                print(f"Error deleting images: {e}")
        
        for table in tables:
            if table not in confusing:
                query = f"DELETE FROM {table} WHERE ship_id = ?"
                c.execute(query, (ids[0],))
            elif table == "locations":
                query = "DELETE FROM locations WHERE location_row_ID = ?"
                c.execute(query, (location_id,))
            elif table == "builds":
                query = "DELETE FROM builds WHERE build_id = ?"
                c.execute(query, (build_id,))
            else:
                query = "DELETE FROM wrecks WHERE id = ?"
                c.execute(query, (ids[0],))

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