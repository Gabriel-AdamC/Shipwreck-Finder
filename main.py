import sys
import sqlite3
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QPushButton,
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
#           I think I may need to use one large dict for this, rather than several vars for the lists in load_lists()


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
        for name, lat, lon, id, year, mat_id, mat, local, ocean, country, prop_id, prop, sheath_id, sheath, fast_id, fast, purp_id, purp, type_id, type, por2_id, por2, por4_id, por4, trad_id, trad, ctpye_id, ctype, con_id, con in wrecks:
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
        controls_layout = QGridLayout()

        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Year filter FROM ")

        self.year2_input = QLineEdit()
        self.year2_input.setPlaceholderText("Year filter TO (OPTIONAL)")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ship Name")
        
        # list of inputs for the dropdowns
        inputs = [
            "materials", "coordinate_type", "confidence", "port2", "port4", "trade_routes", "oceans", "country",
            "local", "sheathing", "type", "fastening", "purpose", "propulsion"
        ]

        # Dynamically generate dropdowns, rather than hardcoding each one
        for i in inputs:
            combo = QComboBox()
            setattr(self, f"{i}_input", combo)
            if i != "port2" and i != "port4":
                combo.addItem(f"All {i.capitalize()}s")  # Default options
                for item in getattr(self, f"{i}", []):
                    combo.addItem(item[1])
                combo.setPlaceholderText(f"{i.capitalize()} filter")
            # port2 and port4 both come from one var, so they have special cases
            elif i == "port2":
                combo.addItem("Port Destination")
                for item in self.ports:
                    combo.addItem(item[1])
                combo.setPlaceholderText("Port Destination filter")
            else:
                combo.addItem("Port Departed")
                for item in self.ports:
                    combo.addItem(item[1])
                combo.setPlaceholderText("Port Departed filter")

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.handle_search)

        controls = [
            QLabel("Filters"), self.year_input, self.year2_input, self.name_input,
            self.materials_input, self.propulsion_input, self.sheathing_input,
            self.fastening_input, self.purpose_input, self.type_input,
            self.oceans_input, self.country_input, self.local_input,
            self.port2_input, self.port4_input, self.trade_routes_input,
            self.coordinate_type_input, self.confidence_input, self.search_button
        ]

        cols = 6
        for i, widget in enumerate(controls):
            row = i // cols
            col = i % cols
            controls_layout.addWidget(widget, row, col)

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
                    type.type_name,
                    voyage.port_to,
                    ports_to.port_name AS port2_name,
                    voyage.port_from,
                    ports_from.port_name AS port4_name,
                    voyage.trade_route,
                    trade_routes.route_name,
                    misc.coord_type,
                    coord_type.coord_type,
                    misc.confidence,
                    confidence.confidence
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
                LEFT JOIN voyage ON wrecks.id = voyage.ship_id
                LEFT JOIN ports AS ports_to ON voyage.port_to = ports_to.id
                LEFT JOIN ports AS ports_from ON voyage.port_from = ports_from.id
                LEFT JOIN trade_routes ON voyage.trade_route = trade_routes.id
                LEFT JOIN misc ON wrecks.id = misc.ship_id
                LEFT JOIN coord_type ON misc.coord_type = coord_type.id
                LEFT JOIN confidence ON misc.confidence = confidence.id
                """)
        self.shipwrecks = c.fetchall()

    def load_lists(self):
        """ Load all the info needed for the lists """

        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        # list that you iterate through to dynamically add variables, rather than hardcode each
        vars = [
            "materials", "oceans", "country", "local", "propulsion",
            "sheathing", "fastening", "purpose", "type", "ports",
            "trade_routes", "coord_type", "confidence"
        ]
        for i in vars:
            if i != "country":
                c.execute(f"SELECT * FROM {i}")
                self.__setattr__(i, c.fetchall())
            else:
                c.execute("""SELECT country_id, country_name, ocean_id
                             FROM countries
                             GROUP BY country_name""")
                self.__setattr__(i, c.fetchall())
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

        #year_filter = self.year_input.text().strip()
        #if year_filter:
        #    year2_filter = self.year2_input.text().strip()
        #    if year2_filter:
        #        try:
        #            year_filter = int(year_filter)
        #            year2_filter = int(year2_filter)
        #        except ValueError:
        #            print("Invalid year input. Please enter valid integers.")
        #            return
        #        filtered = [w for w in self.shipwrecks if year_filter <= int(w[4]) <= year2_filter]
        #    else:
        #        filtered = [w for w in self.shipwrecks if w[4] == year_filter]
        #else:
        #    filtered = self.shipwrecks

        #port2_filter = self.port2_input.currentText().strip()
        #if port2_filter:
        #    if port2_filter == "Port Destination":
        #        filtered = self.shipwrecks 
        #    else:
        #        filtered = [w for w in self.shipwrecks if port2_filter == w[21]]

        #confidence_filter = self.confidence_input.currentText().strip()
        #if confidence_filter:
        #    if confidence_filter == "Confidence":
        #        filtered = self.shipwrecks 
        #    else:
        #        filtered = [w for w in self.shipwrecks if confidence_filter == w[29]]
        
        #ctype_filter = self.ctype_input.currentText().strip()
        #if ctype_filter:
        #    if ctype_filter == "Coordinate Type":
        #        filtered = self.shipwrecks 
        #    else:
        #        filtered = [w for w in self.shipwrecks if ctype_filter == w[27]]

        #port4_filter = self.port4_input.currentText().strip()
        #if port4_filter:    
        #    if port4_filter == "Port Departed":
        #        filtered = self.shipwrecks 
        #    else:
        #        filtered = [w for w in self.shipwrecks if port4_filter == w[23]]

        trad_filter = self.trade_routes_input.currentText().strip()
        if trad_filter:
            if trad_filter == "Trade Routes":
                filtered = self.shipwrecks 
            else:
                filtered = [w for w in self.shipwrecks if trad_filter == w[25]]

        #name_filter = self.name_input.text().strip()
        #if name_filter:
        #    filtered = [w for w in self.shipwrecks if name_filter.lower() in w[0].lower()]
        #else:
        #    filtered = self.shipwrecks

        self.canvas.plot_shipwrecks(filtered)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
