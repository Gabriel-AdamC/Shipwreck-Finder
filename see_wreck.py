from PyQt5.QtWidgets import (
      QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
      QTabWidget, QComboBox, QFormLayout, QApplication,
      QFrame, QScrollArea, QGridLayout, QDialog, QDialogButtonBox)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QFont, QColor
import sqlite3
from dicts import sections, boxes_dict, input_dict

# TODO: delete the local image path as well as the image path in the db

class WreckInfoWindow(QWidget):
    switch_signal = pyqtSignal(str, object)

    def __init__(self, wreck_data):
        super().__init__()
        self.setWindowTitle("Wreck Information")
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.create_gui(wreck_data)

        self.full_screen_viewer = FullScreenViewer()


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

            if section_name == "sources":
                """ Generate The Sources Tab Seperately, It Has Images """

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

        # have an edit and delete button
        buttons = QHBoxLayout()

        edit = QPushButton("Edit This Wreck")
        delete = QPushButton("Delete This Wreck")
        buttons.addWidget(edit)
        buttons.addWidget(delete)
        self.main_layout.addLayout(buttons)

        # add functionality to buttons
        edit.clicked.connect(lambda: self.confirm("edit"))
        delete.clicked.connect(lambda: self.confirm("delete"))

    
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
    

    def update_ship_info(self, name):
        """Update both name and id when ship selection changes"""
        self.name = name
        self.ids = self.update_id(name)

    
    def link_im_cap(self):
        """ Links The Images To The Captions And Returns A Tuple of (image_path, caption) """
        image_data = []

        conn = sqlite3.connect("shipwrecks.db")
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
    

    def confirm(self, action):
        """ Provide A Dialog To The User That Takes Them To Another Page """
        phrase = QLabel(f"Are you certain you want to {action} this wreck?")
        title = f"{action.capitalize()} wreck?"
        dlg = QDialog(self)
        dlg.setWindowTitle(title)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        if action == "edit":
            buttons.accepted.connect(lambda: self.edit())
        else:
            buttons.accepted.connect(lambda: self.delete())
        buttons.rejected.connect(dlg.reject)

        message_layout = QVBoxLayout()
        message_layout.addWidget(phrase)
        message_layout.addWidget(buttons)
        dlg.setLayout(message_layout)

        return dlg.exec_()
    

    def edit(self):
        print("editing")
        # emit signal to switch to the edit_wreck page
        # emit the ship_id


    def delete(self):
        """ Deletes The Wreck From The Database Completely """
        tables = ["wrecks", "builds", "locations", "voyage", "extras", "images"]
        confusing = ["wrecks", "builds", "locations"] # These will all have different queries

        try:
            # i need the location_row_ID and the build_id 
            conn = sqlite3.connect("shipwrecks.db")
            c = conn.cursor()
            c.execute("SELECT location_row_ID, build_id FROM wrecks WHERE id = ?", (self.ids[0],))
            result = c.fetchone()
            if result:
                location_id, build_id = result
            else:
                location_id, build_id = None, None
            for table in tables:
                if table not in confusing:
                    query = f"DELETE FROM {table} WHERE ship_id = ?"
                    c.execute(query, (self.ids[0],))
                elif table == "wrecks":
                    query = "DELETE FROM wrecks WHERE id = ?"
                    c.execute(query, (self.ids[0],))
                elif table == "builds":
                    query = "DELETE FROM builds WHERE build_id = ?"
                    c.execute(query, (build_id,))
                else: # only other table is locations
                    query = "DELETE FROM locations WHERE location_row_ID = ?"
                    c.execute(query, (location_id,))

            conn.commit()
            conn.close()
        
        except sqlite3.OperationalError as e:
            print(f"error: {e}")

        except sqlite3.IntegrityError as e:
            print(f"error: {e}")

        except sqlite3.ProgrammingError as e:
            print(f"error: {e}")

        except sqlite3.DataError as e:
            print(f"error: {e}")


class ClickableImageLabel(QLabel):
    """ Custom QLabel That Emits A Signal When Clickd """
    clicked = pyqtSignal(str, str) # image_path and caption

    def __init__(self, image_path, caption):
        super().__init__()
        self.image_path = image_path
        self.caption = caption
        self.setCursor(Qt.PointingHandCursor)

    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path, self.caption)

        

class FullScreenViewer(QWidget):
    """ View An Image In FullSccreen Along With The Associated Caption """

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