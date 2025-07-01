import sys
import sqlite3
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QComboBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavBar
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


# TODO: add a dict or list for wrecks so that i dont filter every time
#           although this is already kinda done with self.wrecks
# TODO: add logic to the filter dropdowns so that they only show relevant options i.e hierarchy for locations


class ShipwreckMapCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = plt.figure(figsize=(10, 5))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        self.setParent(parent)
        self.setup_plot()

    def setup_plot(self):
        self.ax.clear()
        self.ax.set_extent([-180, 180, -90, 90])
        self.ax.add_feature(cfeature.LAND.with_scale('50m'))
        self.ax.add_feature(cfeature.OCEAN.with_scale('50m'))
        self.ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
        self.ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
        self.ax.set_title("Shipwreck Map")
        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")
        self.ax.set_xlim(-180, 180)
        self.ax.set_ylim(-90, 90)
        self.fig.tight_layout()

        self.draw()

    def plot_shipwrecks(self, wrecks):
        """
        wrecks: list of tuples 
        """
        self.ax.clear()
        self.setup_plot()

        # TODO: update logic to plot based off most accurate data
        # i.e. if coords, use, else if local, use that, else if ocean, use that
        for name, lat, lon, id, year, mat_id, mat, local, ocean, country, prop_id, prop, sheath_id, sheath, fast_id, fast, purp_id, purp, type_id, type in wrecks:
            self.ax.plot(lon, lat, 'ro')
        #print(wrecks)  # Debugging line to check the wrecks being plotted 

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
        self.year_input.setPlaceholderText("Year filter FROM ")

        self.year2_input = QLineEdit()
        self.year2_input.setPlaceholderText("Year filter TO (OPTIONAL)")

        # TODO: this can be optimised when done with a loop. list the names i.e. materials, oceans, countries, local
        # then each i represents one of the items. and each is slightly different based on i

        self.material_input = QComboBox()
        self.material_input.addItem("All Materials")  # Default option
        for i in self.materials:
            self.material_input.addItem(i[1]) # Add material names to the combo box
        self.material_input.setPlaceholderText("Material filter")

        self.ocean_input = QComboBox()
        self.ocean_input.addItem("Oceans")  # Default option
        for i in self.oceans:
            self.ocean_input.addItem(i[1]) # Add ocean names to the combo box
        self.ocean_input.setPlaceholderText("Ocean filter")

        self.country_input = QComboBox()
        self.country_input.addItem("Countries")  # Default option
        for i in self.countries:
            self.country_input.addItem(i[1]) # Add country names to the combo box
        self.country_input.setPlaceholderText("Country filter")

        self.local_input = QComboBox()
        self.local_input.addItem("Locations")  # Default option
        for i in self.local:
            self.local_input.addItem(i[1]) # Add local names to the combo box
        self.local_input.setPlaceholderText("Location filter")

        self.sheathing_input = QComboBox()
        self.sheathing_input.addItem("Sheathing")  # Default option
        for i in self.sheathing:
            self.sheathing_input.addItem(i[1])
        self.sheathing_input.setPlaceholderText("Sheathing filter")

        self.type_input = QComboBox()
        self.type_input.addItem("Type")  # Default option
        for i in self.type:
            self.type_input.addItem(i[1])
        self.type_input.setPlaceholderText("Type filter")

        self.fastening_input = QComboBox()
        self.fastening_input.addItem("Fastening")  # Default option
        for i in self.fastening:
            self.fastening_input.addItem(i[1])
        self.fastening_input.setPlaceholderText("Fastening filter")

        self.purpose_input = QComboBox()
        self.purpose_input.addItem("Purpose")  # Default option
        for i in self.purpose:
            self.purpose_input.addItem(i[1])
        self.purpose_input.setPlaceholderText("Purpose filter")

        self.propulsion_input = QComboBox()
        self.propulsion_input.addItem("Propulsion")
        for i in self.propulsion:
            self.propulsion_input.addItem(i[1])
        self.propulsion_input.setPlaceholderText("Propulsion filter")
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.handle_search)

        controls_layout.addWidget(QLabel("Filters:"))
        controls_layout.addWidget(self.year_input)
        controls_layout.addWidget(self.year2_input)
        controls_layout.addWidget(self.material_input)
        controls_layout.addWidget(self.propulsion_input)
        controls_layout.addWidget(self.sheathing_input)
        controls_layout.addWidget(self.fastening_input)
        controls_layout.addWidget(self.purpose_input)
        controls_layout.addWidget(self.type_input)
        controls_layout.addWidget(self.ocean_input)
        controls_layout.addWidget(self.country_input)
        controls_layout.addWidget(self.local_input)
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
        c.execute("""SELECT
                    wrecks.name, 
                    wrecks.x_coord, 
                    wrecks.y_coord, 
                    wrecks.location_row_ID, 
                    wrecks.year_lost, 
                    builds.material_id, 
                    materials.material_name, 
                    local.local_name, 
                    oceans.ocean_name, 
                    countries.country_name,
                    builds.propulsion_id, 
                    propulsion.propulsion_name,
                    builds.sheathing_id,
                    sheathing.sheathing_name,
                    builds.fastening_id,
                    fastening.fastening_name,
                    builds.purpose_id,
                    purpose.reason,
                    builds.type_id,
                    type.type_name
                FROM wrecks
                LEFT JOIN builds ON wrecks.id = builds.build_id 
                LEFT JOIN propulsion ON builds.propulsion_id = propulsion.propulsion_id
                LEFT JOIN type ON builds.type_id = type.type_id
                LEFT JOIN fastening ON builds.fastening_id = fastening.fastening_id
                LEFT JOIN purpose ON builds.purpose_id = purpose.purpose_id
                LEFT JOIN sheathing ON builds.sheathing_id = sheathing.sheathing_id
                LEFT JOIN materials ON builds.material_id = materials.material_id
                LEFT JOIN locations ON wrecks.location_row_ID = locations.location_row_ID
                LEFT JOIN local ON locations.local_id = local.local_id
                LEFT JOIN oceans ON locations.ocean_id = oceans.ocean_id
                LEFT JOIN countries ON locations.country_id = countries.country_id
                """)
        self.shipwrecks = c.fetchall()

    def load_lists(self):
        """ Load all the info needed for the lists """
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("SELECT * FROM materials")
        self.materials = c.fetchall()
        c.execute("SELECT * FROM oceans")
        self.oceans = c.fetchall()
        c.execute("""SELECT country_id, country_name, ocean_id
                    FROM countries
                    GROUP BY country_name""")
        self.countries = c.fetchall()
        c.execute("SELECT * FROM local")
        self.local = c.fetchall()
        c.execute("SELECT * FROM propulsion")
        self.propulsion = c.fetchall()
        c.execute("SELECT * FROM sheathing")
        self.sheathing = c.fetchall()
        c.execute("SELECT * FROM fastening")
        self.fastening = c.fetchall()
        c.execute("SELECT * FROM purpose")
        self.purpose = c.fetchall()
        c.execute("SELECT * FROM type")
        self.type = c.fetchall()
        conn.close()
        

    def plot_all(self):
        self.canvas.plot_shipwrecks(self.shipwrecks)

    def handle_search(self):
        """ Filter shipwrecks based on user input and update the plot. """
        # TODO: immplement a switch case rather than 500 lines of if statements
        # TODO once this is complete and I know the filters and all the tables are correct

        #material_filter = self.material_input.currentText().strip()
        #if material_filter:
            #if material_filter == "All Materials":
                #filtered = self.shipwrecks 
            #else:
                #filtered = [w for w in self.shipwrecks if material_filter == w[6]] 

        #propulsion_filter = self.propulsion_input.currentText().strip()
        #if propulsion_filter:
            #f propulsion_filter == "Propulsion":
                #filtered = self.shipwrecks 
            #else:
                #filtered = [w for w in self.shipwrecks if propulsion_filter == w[11]]
        
        #sheathing_filter = self.sheathing_input.currentText().strip()
        #if sheathing_filter:
            #if sheathing_filter == "Sheathing":
                #filtered = self.shipwrecks 
            #else:
                #filtered = [w for w in self.shipwrecks if sheathing_filter == w[13]]

        #fastening_filter = self.fastening_input.currentText().strip()
        #if fastening_filter:
            #if fastening_filter == "Fastening":
                #filtered = self.shipwrecks 
            #else:
                #filtered = [w for w in self.shipwrecks if fastening_filter == w[15]]

        #purpose_filter = self.purpose_input.currentText().strip()
        #if purpose_filter:
            #if purpose_filter == "Purpose":
                #filtered = self.shipwrecks 
            #else:
                #filtered = [w for w in self.shipwrecks if purpose_filter == w[17]]

        #type_filter = self.type_input.currentText().strip()
        #if type_filter:
            #if type_filter == "Type":
                #filtered = self.shipwrecks
            #else:
                #filtered = [w for w in self.shipwrecks if type_filter == w[19]]
        
        
        #ocean_filter = self.ocean_input.currentText().strip()
        #if ocean_filter:
            #if ocean_filter == "Oceans":
                #filtered = self.shipwrecks 
            #else:
                #filtered = [w for w in self.shipwrecks if ocean_filter == w[8]]

        #country_filter = self.country_input.currentText().strip()
        #if country_filter:
            #if country_filter == "Countries":
                #filtered = self.shipwrecks 
            #else:
                #filtered = [w for w in self.shipwrecks if country_filter == w[9]]

        #local_filter = self.local_input.currentText().strip()
        #if local_filter:    
            #if local_filter == "Locations":
                #filtered = self.shipwrecks 
            #else:
                #filtered = [w for w in self.shipwrecks if local_filter == w[7]]

        year_filter = self.year_input.text().strip()
        if year_filter:
            year2_filter = self.year2_input.text().strip()
            if year2_filter:
                try:
                    year_filter = int(year_filter)
                    year2_filter = int(year2_filter)
                except ValueError:
                    print("Invalid year input. Please enter valid integers.")
                    return
                filtered = [w for w in self.shipwrecks if year_filter <= int(w[4]) <= year2_filter]
            else:
                filtered = [w for w in self.shipwrecks if w[4] == year_filter]
        else:
            filtered = self.shipwrecks

        self.canvas.plot_shipwrecks(filtered)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
