from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from map import MapWindow
from data_entry import DataEntryWindow
from see_wreck import WreckInfoWindow

# TODO: fix captions, images, add buttons to see_wreck, maybe make see_wreck look better but thats ;long term

# TODO: Add districts

# TODO: if data enty text is too long, it goes off page. Make it wrap instead?

# TODO: filters are iffy, if just ocean it doesnt work properly, so maybe make country compulsory?

# TODO: Need to make the caption to image more user friendly, and make it work.
    # caption[0] goes to image[0] and so on
        # need to make the data entry caption work for multiple captions per entry (currently at 1 per entry)
            # and currently the 1 caption gets set to every image

# TODO: Add a page gui for data editing, so that you can edit shipwrecks in the database
# TODO: Add a page gui for data deletion, so that you can delete shipwrecks from the database
#           May face issues with auto-incrementing IDs, so may need to handle that in the database
# TODO: plot data based on most accurate info, as not all shipwrecks have coordinates
# TODO: Add the click functionality to the map so that it shows the shipwreck info
# TODO: Optimise the code in location_change() to avoid repetition
# TODO: change countrys to countries on location_change(). Currently it doesnt work if it has countries for some reason.
# TODO: implement districts in filters and hierarchy
# TODO: Do extensive testing on the hierarchy for locations, make sure that works 100%
# TODO: Make it look nice

# TODO: filters check for _ in name. so if I have "i" in name, "titanic", "ship" and anything with i show up

# completed Today: 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shipwrecks Map")
        self.stack = QStackedWidget()

        self.data_entry_page = DataEntryWindow()
        self.map_page = MapWindow()
        self.see_wreck_page = None

        self.stack.addWidget(self.map_page)
        self.stack.addWidget(self.data_entry_page)

        self.setCentralWidget(self.stack)

        self.map_page.switch_signal.connect(self.switch_page)
        self.data_entry_page.switch_signal.connect(self.switch_page)


    def switch_page(self, page_name, data=None):
        if page_name == "data_entry":
            self.stack.setCurrentWidget(self.data_entry_page)
        elif page_name == "map":
            self.stack.setCurrentWidget(self.map_page)
        elif page_name == "edit_wreck":
            if self.edit_wreck_page:
                self.stack.removeWidget(self.edit_wreck_page)
                self.edit_wreck_page.deleteLater()

            self.edit_wreck_page = EditWreckWindow(data)
            self.stack.addWidget(self.edit_wreck_page)
            self.edit_wreck_page.switch_signal.connect(self.switch_page)
            self.stack.setCurrentWidget(self.edit_wreck_page)
        elif page_name == "see_wreck":
            if self.see_wreck_page:
                self.stack.removeWidget(self.see_wreck_page)
                self.see_wreck_page.deleteLater()
            
            self.see_wreck_page = WreckInfoWindow(data)
            self.stack.addWidget(self.see_wreck_page)
            self.see_wreck_page.switch_signal.connect(self.switch_page)
            self.stack.setCurrentWidget(self.see_wreck_page)


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()