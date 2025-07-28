from PyQt5.QtWidgets import (
      QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
      QTabWidget, QComboBox, QFormLayout,
      QFrame, QScrollArea, QGridLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor
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
    

    def create_grid(self, grid_layout):
        """ Creates The Grid Of Images """

        columns = 3 

        image_data = link_im_cap()

        for i, (image_path, caption) in enumerate(image_data):
            row = i // columns
            col = i % columns

            # create a frame for each image caption pair
            frame = QFrame()
            frame.setFrameStyle(QFrame.box)
            frame.setLineWidth(1)
            frame_layout = QVBoxLayout()
            frame.setLayout(frame_layout)

            image_label = ClickableImageLabel(image_path, caption)

            # load and scale the image
            pixmap = QPixmap(200, 150)
            pixmap.fill(QColor(200, 200, 200))

            # try to load the actual image
            actual_pixmap = QPixmap(image_path)
            if not actual_pixmap.isNull():
                pixmap = actual_pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            image_label.setPixmap(pixmap)
            image_label.setFixedSize(200, 150)
            image_label.setScaledContents(True)

            image_label.clicked.connect(self.full_screen)

            # set the captions
            caption_label = QLabel(caption)
            caption_label.setWordWrap(True)
            caption_label.setAlignment(Qt.AlignCenter)
            caption_label.setMaximumWidth(200)
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
        """ Links The Images To The Captions """
        image_data = []

        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("SELECT image_path FROM images WHERE ship_id = ?", self.ids[0])
        image_paths = c.fetchall()
        c.execute("SELECT caption FROM images WHERE ship_id = ?", self.ids[0])
        captions = c.fetchall()
        conn.close()

        for i, image_path in 