from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from map import MapWindow
from data_entry import DataEntryWindow

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

    def switch_page(self, page_name):
        if page_name == "data_entry":
            self.stack.setCurrentWidget(self.data_entry_page)
        else:
            self.stack.setCurrentWidget(self.map_page)


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()