from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from map import MapWindow
from data_entry import DataEntryWindow

# TODO: finish form inputs
# TODO: Make sure hierarchy works for the data entry as well
# TODO: fix the country and ocean filtering. 
            # The filtering logic at the bottom also needs a revamp then.
            # although it may be fine, finish the form, add data and then check
# TODO: Add districts

# TODO: Add a page gui for data entry, so that you can add shipwrecks to the database
# TODO: Add a page gui for data editing, so that you can edit shipwrecks in the database
# TODO: Add a page gui for data deletion, so that you can delete shipwrecks from the database
#           May face issues with auto-incrementing IDs, so may need to handle that in the database
# TODO: plot data based on most accurate info, as not all shipwrecks have coordinates
# TODO: Add the click functionality to the map so that it shows the shipwreck info
# TODO: Optimise the code in location_change() to avoid repetition
# TODO: change countrys to countries on location_change(). Currently it doesnt work if it has countries for some reason.
# TODO: implement districts in filters and hierarchy
# TODO: change ocean to region

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shipwrecks Map")
        self.stack = QStackedWidget()

        self.data_entry_page = DataEntryWindow()
        self.map_page = MapWindow()

        self.stack.addWidget(self.map_page)
        self.stack.addWidget(self.data_entry_page)

        self.setCentralWidget(self.stack)

        self.map_page.switch_signal.connect(self.switch_page)
        self.data_entry_page.switch_signal.connect(self.switch_page)

    def switch_page(self, page_name):
        if page_name == "data_entry":
            self.stack.setCurrentWidget(self.data_entry_page)
        elif page_name == "map":
            self.stack.setCurrentWidget(self.map_page)


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()