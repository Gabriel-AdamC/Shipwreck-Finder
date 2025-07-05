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

# TODO: add logic to the filter dropdowns so that they only show relevant options i.e hierarchy for locations
#           I think I may need to use one large dict for this, rather than several vars for the lists in load_lists()

# TODO: Add a page gui for data entry, so that you can add shipwrecks to the database
# TODO: Add a page gui for data editing, so that you can edit shipwrecks in the database
# TODO: Add a page gui for data deletion, so that you can delete shipwrecks from the database
#           May face issues with auto-incrementing IDs, so may need to handle that in the database
# TODO: plot data based on most accurate info, as not all shipwrecks have coordinates
# TODO: Add the click functionality to the map so that it shows the shipwreck info


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
        for name, lat, lon, id, year, mat_id, mat, local, ocean, country, prop_id, prop, sheath_id, sheath, fast_id, fast, purp_id, purp, type_id, type, por2_id, por2, por4_id, por4, trad_id, trad, ctpye_id, ctype, con_id, con, wood_id, wood in wrecks:
            self.ax.plot(lon, lat, 'ro')
        #print(wrecks)  # Debugging line to check the wrecks being plotted 

        self.draw()


class MainWindow(QMainWindow):

    # list of inputs for the dropdowns and filters
    # these are used to dynamically create the dropdowns in the UI
    inputs = [
        "coord_type", "confidence", "port2", "port4", "trade_routes", "oceans", "country",
        "local", "sheathing", "type", "fastening", "purpose", "propulsion", "materials"
    ]

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
        self.controls_layout = QGridLayout()

        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Year filter FROM ")

        self.year2_input = QLineEdit()
        self.year2_input.setPlaceholderText("Year filter TO (OPTIONAL)")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ship Name")

        # Dynamically generate dropdowns, rather than hardcoding each one
        for i in self.inputs:
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
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        self.search_button.clicked.connect(self.handle_search)

        controls = [
            QLabel("Filters"), self.year_input, self.year2_input, self.name_input,
            self.oceans_input, self.country_input, self.local_input,
            self.port2_input, self.port4_input, self.trade_routes_input,
            self.coord_type_input, self.confidence_input, self.type_input,
            self.fastening_input, self.purpose_input,
            self.propulsion_input, self.sheathing_input, self.materials_input
        ]

        cols = 7
        for i, widget in enumerate(controls):
            row = i // cols
            col = i % cols
            self.controls_layout.addWidget(widget, row, col)

        self.controls_layout.addWidget(self.search_button, 4, 0)
        self.controls_layout.addWidget(self.reset_button, 4, 1)

        main_layout.addLayout(self.controls_layout)

        # Matplotlib canvas and toolbar
        self.canvas = ShipwreckMapCanvas(self)
        self.toolbar = NavBar(self.canvas, self)

        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

        # Load data from database
        self.load_data()
        self.plot_all()

        # Create functional hierarchy for the dropdowns
        self.materials_input.currentTextChanged.connect(self.material_change)

    def material_change(self):
        """ Update the dropdowns based on the selected material. """
        selected_material = self.materials_input.currentText().strip()
        if selected_material == "wood":
            if not hasattr(self, 'wood_types_input'):
                # Show wood types if wood is selected
                self.wood_types_input = QComboBox()
                self.wood_types_input.addItem("All Wood Types")
                for item in self.wood_types:
                    self.wood_types_input.addItem(item[1])
                self.controls_layout.addWidget(self.wood_types_input, 2, 4) 
        else:
            if hasattr(self, 'wood_types_input'):
                # Remove wood types dropdown if it exists
                self.controls_layout.removeWidget(self.wood_types_input)
                self.wood_types_input.deleteLater()
                del self.wood_types_input


    def load_data(self):
        # Connect to SQLite and load shipwreck data
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
                    confidence.confidence,
                    builds.wood_id,
                    wood_types.name
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
                LEFT JOIN wood_types ON builds.wood_id = wood_types.wood_id
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
            "trade_routes", "coord_type", "confidence", "wood_types"
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

        filter_field_indexes = {
            "materials": 6,     
            "coord_type": 27,   
            "confidence": 29,
            "port2": 21,        
            "port4": 23,        
            "trade_routes": 25,
            "oceans": 8,
            "country": 9,
            "local": 7,
            "sheathing": 13,
            "type": 19,
            "fastening": 15,
            "purpose": 17,
            "propulsion": 11
        }
        filtered = self.shipwrecks  # Start with all shipwrecks
        counter = 0  # Counter to check if any filters are applied
        exceptions = ["Port Destination", "Port Departed"]  # Special cases for ports

        for input_name, index in filter_field_indexes.items():
            input_widget = getattr(self, f"{input_name}_input")
            selected_text = input_widget.currentText().strip()
            if selected_text != f"All {input_name.capitalize()}s":
                if selected_text in exceptions:
                    continue # Keep the filtered list as is
                else:
                    filtered = [w for w in filtered if selected_text == w[index]]
                    counter += 1
            elif counter != 0:
                filtered = filtered # If no filter on current iteration, but filters in previous, we keep the filtered list as is
            else:
                filtered = self.shipwrecks # If no filters are applied, reset to all shipwrecks

        # unique filters that are not in the inputs list
        wood_type_filter = self.wood_types_input.currentText().strip() if hasattr(self, 'wood_types_input') else None
        if wood_type_filter and wood_type_filter != "All Wood Types":
            filtered = [w for w in filtered if wood_type_filter == w[31]]

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
                filtered = [w for w in filtered if year_filter <= int(w[4]) <= year2_filter]
            else:
                filtered = [w for w in filtered if w[4] == year_filter]
        else:
            filtered = filtered  # If no year filter is applied, keep the filtered list as is

        name_filter = self.name_input.text().strip()
        if name_filter:
            filtered = [w for w in filtered if name_filter.lower() in w[0].lower()]
        else:
            filtered = filtered

        self.canvas.plot_shipwrecks(filtered)

    def reset(self):
        """ Reset all filters and reload the original shipwrecks. """
        self.year_input.clear()
        self.year2_input.clear()
        self.name_input.clear()

        for input_name in self.inputs:
            input_widget = getattr(self, f"{input_name}_input")
            input_widget.setCurrentIndex(0)  
        self.canvas.plot_shipwrecks(self.shipwrecks)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
