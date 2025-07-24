import sys
import sqlite3
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QMessageBox,
    QLineEdit, QLabel, QComboBox, QHBoxLayout, QDialog, QDialogButtonBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavBar
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PyQt5.QtCore import pyqtSignal
from helpers import (location_change, get_country_id_by_name, get_ocean_id_by_name)

class ShipwreckMapCanvas(FigureCanvas):
    switch_signal = pyqtSignal(str, object)

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = plt.figure(figsize=(10, 5))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        self.setParent(parent)
        self.setup_plot()
        self.cid = self.fig.canvas.mpl_connect("button_press_event", self.on_click)

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
        for name, lat, lon, id, year, mat_id, mat, local, ocean, country, prop_id, prop, sheath_id, sheath, fast_id, fast, purp_id, purp, type_id, type, por2_id, por2, por4_id, por4, trad_id, trad, ctpye_id, ctype, con_id, con, wood_id, wood, co_oc_co_id, co_oc_oc_id in wrecks:
            self.ax.plot(lon, lat, 'ro')

        self.draw()


    def on_click(self, event):
        """ Handle Click Events On The Map """
        wreck_data = []
        xdata = event.xdata
        ydata = event.ydata
        wrecks = self.load_basic_data()

        radius = 2.0 # check around the click

        for wreck in wrecks:
            wreck_lon = float(wreck[2])
            wreck_lat = float(wreck[1])

            # is this wreck by the click?
            if (abs(wreck_lon - xdata) <= radius and abs(wreck_lat - ydata) <= radius):
                wreck_data.append(wreck)

        # send user to new page with those wrecks
        if wreck_data:
            self.view_wreck(wreck_data)
        


    def view_wreck(self, wreck_data):
        """ Promts User To Take Them To A New Page With The Info Of Clicked Wreck """
        dlg = QDialog(self)
        dlg.setWindowTitle("Move to Wreck Info?")
        msg = QLabel("Would you like to view the wreck information for the clicked pin?")
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.accept(dlg, wreck_data))
        buttons.rejected.connect(dlg.reject)
        mes_layout = QVBoxLayout()
        mes_layout.addWidget(msg)
        mes_layout.addWidget(buttons)
        dlg.setLayout(mes_layout)
        return dlg.exec_()


    def accept(self, dlg, wreck_data):
        dlg.accept()
        # emit signal
        self.switch_signal.emit("see_wreck", wreck_data)


    def load_basic_data(self):
        """ Load Only Neccassary Data For Map Click Check """
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute("""
            SELECT name, x_coord, y_coord
            FROM wrecks
        """)
        basics = c.fetchall()
        conn.close()
        return basics




class MapWindow(QWidget):

    # This signal is emitted when the map is switched to the data entry page
    switch_signal = pyqtSignal(str, object)

    # list of inputs for the dropdowns and filters
    # these are used to dynamically create the dropdowns in the UI
    inputs = [
        "coord_type", "confidence", "port2", "port4", "trade_routes", "oceans", "countries", "districts",
        "local", "sheathing", "type", "fastening", "purpose", "propulsion", "materials"
    ]

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.map_ui(layout)


    def map_ui(self, layout):
        """ Set up the main UI for the shipwreck map viewer. """

        self.setGeometry(100, 100, 900, 700)

        # Controls
        #load the materials for the materials dropdown
        self.load_lists()

        # buttons to change the page view
        self.page_change = QHBoxLayout()
        self.btn_map = QPushButton("Map")
        self.btn_map.clicked.connect(lambda: self.switch_signal.emit("map", None))
        self.btn_entry = QPushButton("Data Entry")
        self.btn_entry.clicked.connect(lambda: self.switch_signal.emit("data_entry", None))
        self.page_change.addWidget(self.btn_map)
        self.page_change.addWidget(self.btn_entry)

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

                if i == "countries":
                    combo.addItem("All Countries")
                elif i == "oceans":
                    combo.addItem("All Oceans")
                elif i == "local":
                    combo.addItem("All Locals")
                else:
                    combo.addItem(f"All {i.capitalize()}s")  

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
            self.oceans_input, self.countries_input, self.local_input,
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

        layout.addLayout(self.page_change)
        layout.addLayout(self.controls_layout)

        # Matplotlib canvas and toolbar
        self.canvas = ShipwreckMapCanvas(self)
        self.canvas.switch_signal.connect(self.relay_signal)
        self.toolbar = NavBar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Load data from database
        self.load_data()
        self.plot_all()

        # Create functional hierarchy for the dropdowns
        self.materials_input.currentTextChanged.connect(self.material_change)
        self.oceans_input.currentTextChanged.connect(lambda: self.hierarchy("ocean"))
        self.countries_input.currentTextChanged.connect(lambda: self.hierarchy("country"))
        self.local_input.currentTextChanged.connect(lambda: self.hierarchy("local"))


    def relay_signal(self, page_name, data=None):
        """ Relay the signal from the canvas to the main window. """
        self.switch_signal.emit(page_name, data)

    
    def hierarchy(self, source):
        location_change(
            source,
            self.oceans_input.currentText().strip(),
            self.countries_input.currentText().strip(),
            self.local_input.currentText().strip(),
            self.oceans,
            self.countries,
            self.local,
            self.country_ocean,
            self.oceans_input,
            self.countries_input,
            self.local_input,
            get_ocean_id_by_name=lambda name: get_ocean_id_by_name(name, self.oceans),
            get_country_id_by_name=lambda name: get_country_id_by_name(name, self.countries)
        )


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
                    wood_types.name,
                    country_ocean.country_id,
                    country_ocean.ocean_id
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
                LEFT JOIN countries ON locations.country_id = countries.country_id
                LEFT JOIN country_ocean ON locations.country_id = country_ocean.country_id
                LEFT JOIN oceans ON oceans.ocean_id = country_ocean.ocean_id
                LEFT JOIN voyage ON wrecks.id = voyage.ship_id
                LEFT JOIN ports AS ports_to ON voyage.port_to = ports_to.id
                LEFT JOIN ports AS ports_from ON voyage.port_from = ports_from.id
                LEFT JOIN trade_routes ON voyage.trade_route = trade_routes.id
                LEFT JOIN misc ON wrecks.id = misc.ship_id
                LEFT JOIN coord_type ON misc.coord_type = coord_type.id
                LEFT JOIN confidence ON misc.confidence = confidence.id
                LEFT JOIN wood_types ON builds.wood_id = wood_types.wood_id
                """)
        shipwrecks = c.fetchall()
        conn.close()
    
        self.shipwrecks = shipwrecks
        return shipwrecks
        

    def load_lists(self):
        """ Load all the info needed for the lists """

        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        # list that you iterate through to dynamically add variables, rather than hardcode each
        vars = [
            "materials", "oceans", "countries", "local", "propulsion",
            "sheathing", "fastening", "purpose", "type", "ports",
            "trade_routes", "coord_type", "confidence", "wood_types", "country_ocean"
        ]
        for i in vars:
            c.execute(f"SELECT * FROM {i}")
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
            "countries": 9,
            "local": 7,
            "sheathing": 13,
            "type": 19,
            "fastening": 15,
            "purpose": 17,
            "propulsion": 11
        }
        
        filtered = self.shipwrecks  # Start with all shipwrecks
        filters = False  # Flag to check if any filter is applied
        exceptions = ["Port Destination", "Port Departed"]  # Special cases for ports

        for input_name, index in filter_field_indexes.items():
            input_widget = getattr(self, f"{input_name}_input")
            selected_text = input_widget.currentText().strip()
            
            # Check if this is a "All ..." selection (meaning no filter should be applied)
            is_all_selection = (
                selected_text.startswith("All ") or 
                selected_text in exceptions
            )
            
            if not is_all_selection:
                if selected_text in exceptions:
                    continue # Keep the filtered list as is
                else:
                    filtered = [w for w in filtered if w[index] == selected_text]
                    filters = True
            elif filters == True:
                continue
            else:
                filtered = filtered


        wood_type_filter = self.wood_types_input.currentText().strip() if hasattr(self, 'wood_types_input') else None
        if wood_type_filter and wood_type_filter != "All Wood Types":
            filtered = [w for w in filtered if w[31] is not None and wood_type_filter == w[31]]

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
                filtered = [w for w in filtered if w[4] is not None and year_filter <= int(w[4]) <= year2_filter]
            else:
                try:
                    year_filter = int(year_filter)
                    filtered = [w for w in filtered if w[4] is not None and int(w[4]) == year_filter]
                except ValueError:
                    print("Invalid year input. Please enter valid integers.")
                    return
        else:
            filtered = filtered  # If no year filter is applied, keep the filtered list as is

        name_filter = self.name_input.text().strip()
        if name_filter:
            filtered = [w for w in filtered if w[0] is not None and name_filter.lower() in w[0].lower()]
        else:
            filtered = filtered

        seen = set()
        deduped = []
        for w in filtered:
            key = (w[0], w[1], w[2])  
            if key not in seen:
                deduped.append(w)
                seen.add(key)

        self.canvas.plot_shipwrecks(filtered)


    def reset(self):
        """ Reset all filters and reload the original shipwrecks. """
        self.year_input.clear()
        self.year2_input.clear()
        self.name_input.clear()

        self.oceans_input.blockSignals(True) # These prevent maximum recursion depth 
        self.countries_input.blockSignals(True)
        self.local_input.blockSignals(True)

        for input_name in self.inputs:
            if input_name != "oceans" and input_name != "country" and input_name != "local":
                input_widget = getattr(self, f"{input_name}_input")
                input_widget.setCurrentIndex(0)
            else: # Redet the location filters, as they change based on the input due to hierarchy
                input_widget = getattr(self, f"{input_name}_input")
                input_widget.blockSignals(True)
                input_widget.clear()
                input_widget.addItem(f"All {input_name.capitalize()}s")
                for item in getattr(self, input_name):
                    input_widget.addItem(item[1])
                input_widget.setCurrentIndex(0)
                input_widget.blockSignals(False)
            
        self.oceans_input.blockSignals(False)
        self.countries_input.blockSignals(False)
        self.local_input.blockSignals(False)

        # get the new list of wrecks for if user adds to the database
        new = self.load_data()
                
        self.canvas.plot_shipwrecks(new)
