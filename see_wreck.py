from PyQt5.QtWidgets import (
      QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
      QComboBox, QDialog, QDialogButtonBox)
from PyQt5.QtCore import pyqtSignal
from dicts import sections, boxes_dict, input_dict
import ui
from helpers import update_id

class WreckInfoWindow(QWidget):
    switch_signal = pyqtSignal(str, object)

    def __init__(self, wreck_data):
        super().__init__()
        self.setWindowTitle("Wreck Information")
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.wreck_data = wreck_data

        self.data_display = ui.DataDisplayWidget()

        self.create_gui(wreck_data)


    def create_gui(self, wreck_data):
        """ Creates The GUI, Basically The Data Entry Page """

        top_row = QHBoxLayout()

        self.ship = QComboBox() # choose between the ships
        
        for row in wreck_data:
            self.ship.addItem(row[0])

        self.name = self.ship.currentText()
        self.ids = ui.update_id(self.name)  # Creates a tuple of (ship_id, location_row_ID, build_id)

        self.ship.currentTextChanged.connect(self.update_ship_info)

        back = QPushButton("Back to the Map")

        back.clicked.connect(lambda: self.switch_signal.emit("map", None))

        top_row.addWidget(self.ship)
        top_row.addWidget(back)
        self.main_layout.addLayout(top_row)

        self.main_layout.addWidget(self.data_display)

        self.display()


    def display(self):
        self.data_display.display(
            name = self.name,
            ids=self.ids,
            sections_func=sections,
            input_dict_func=input_dict,
            boxes_dict_func=boxes_dict,
            db_path="shipwrecks.db",
            edit_callback=self.handle_edit,
            what = "see"
        )


    def update_ship_info(self, new_name):
        """Update both name and id when ship selection changes"""
        self.name = new_name
        self.ids = update_id(new_name)

        # repopulate
        self.display()


    def confirm(self, action):
        """ Provide A Dialog To The User That Takes Them To Another Page """
        phrase = QLabel(f"Are you certain you want to {action} this wreck?")
        title = f"{action.capitalize()} wreck?"
        dlg = QDialog(self)
        dlg.setWindowTitle(title)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        if action == "edit":
            buttons.accepted.connect(lambda: (self.edit(), dlg.accept()))
        else:
            buttons.accepted.connect(lambda: (self.delete(), dlg.accept()))
        buttons.rejected.connect(dlg.reject)

        message_layout = QVBoxLayout()
        message_layout.addWidget(phrase)
        message_layout.addWidget(buttons)
        dlg.setLayout(message_layout)

        return dlg.exec_()
    

    def handle_edit(self, name, ids):
        """ Change To The Edit Wreck Page With Data """
        self.switch_signal.emit("edit_wreck", ids[0])


