import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QComboBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavBar
import matplotlib.image as mpimg
from matplotlib.figure import Figure


class ShipwreckMapCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.setParent(parent)
        self.setup_plot()

    def setup_plot(self):
        self.ax.clear()
        try:
            img = mpimg.imread("static/Earth_scaled.png")
        except FileNotFoundError:
            self.ax.text(0.5, 0.5, "Background image not found", ha='center', va='center', transform=self.ax.transAxes, fontsize=16, color='red')
            img = None
        if img is not None:
            self.ax.imshow(img, extent=(-180, 180, -90, 90), aspect='auto')
        self.ax.grid(True)
        self.ax.set_title("Shipwreck Map")
        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")
        self.ax.set_xlim(-180, 180)
        self.ax.set_ylim(-90, 90)
        self.draw()

    def plot_shipwrecks(self, wrecks):
        """
        wrecks: list of tuples (name, lat, lon, description, year)
        """
        self.ax.clear()
        self.setup_plot()

        for name, lat, lon, id, year, mat_id, mat in wrecks:
            self.ax.plot(lon, lat, 'ro')

        self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shipwreck Map Viewer")
        self.setGeometry(100, 100, 900, 700)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Controls
        #load the materials for the materials dropdown
        self.load_lists()
        controls_layout = QHBoxLayout()

        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Year filter (e.g., 1900)")

        self.material_input = QComboBox()
        self.material_input.addItem("All Materials")  # Default option
        for i in self.materials:
            self.material_input.addItem(i[1]) # Add material names to the combo box
        self.material_input.setPlaceholderText("Material filter")
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.handle_search)

        controls_layout.addWidget(QLabel("Filter by Year:"))
        controls_layout.addWidget(QLabel("Filter by Material:"))
        controls_layout.addWidget(self.year_input)
        controls_layout.addWidget(self.material_input)
        controls_layout.addWidget(self.search_button)

        main_layout.addLayout(controls_layout)

        # Matplotlib canvas and toolbar
        self.canvas = ShipwreckMapCanvas(self)
        self.toolbar = NavBar(self.canvas, self)

        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

        # Load data from database
        self.load_data()
        self.plot_all()

    def load_data(self):
        # Connect to SQLite and load shipwreck data
        # TODO: replace with one full sql query to get all data
        # FOR TESTING THIS IS FINE 
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("""SELECT wrecks.name, wrecks.x_coord, wrecks.y_coord, wrecks.location_row_ID, wrecks.year_lost, 
                  builds.material_id, materials.material_name FROM wrecks
                  JOIN builds ON wrecks.id = builds.build_id 
                  JOIN materials ON builds.material_id = materials.material_id""")
        self.shipwrecks = c.fetchall()

    def load_lists(self):
        """ Load all the info needed for the lists """
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("SELECT * FROM oceans")
        self.oceans = c.fetchall()
        c.execute("SELECT * FROM materials")
        self.materials = c.fetchall()
        conn.close()
        

    def plot_all(self):
        self.canvas.plot_shipwrecks(self.shipwrecks)

    def handle_search(self):
        """ Filter shipwrecks based on user input and update the plot. """
        # TODO: immplement a switch case rather than 500 lines of if statements

        material_filter = self.material_input.currentText().strip()
        if material_filter:
            if material_filter == "All Materials":
                filtered = self.shipwrecks 
            else:
                filtered = [w for w in self.shipwrecks if material_filter == w[6]] 

        #year_filter = self.year_input.text().strip()
        #if year_filter:
            #filtered = [w for w in self.shipwrecks if w[4] == year_filter]
        #else:
            #filtered = self.shipwrecks
        self.canvas.plot_shipwrecks(filtered)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
