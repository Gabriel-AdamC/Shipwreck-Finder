from PyQt5.QtWidgets import (QLineEdit, QComboBox, QPushButton, QLabel)

def sections():
    sections = {
            "wreck": {
                "kraken_id": QLineEdit(),
                "ship_name": QLineEdit(),
                "year_lost": QLineEdit(),
                "date_lost": QLineEdit()
            },
            "location": {
                "ocean": QComboBox(),
                "country": QComboBox(),
                "district": QComboBox(),
                "local_location": QComboBox(),
                "details_of_location": QLineEdit(),
                "reported_coordinates": QLineEdit(),
                "coordinate_confidence": QComboBox(),
                "verified_coordinates": QLineEdit(),
                "reported_depth": QLineEdit(),
                "latitude": QLineEdit(),
                "longitude": QLineEdit(),
                "coordinate_type": QComboBox()
            },
            "construction": {
                "material": QComboBox(),
                "wood_type": QComboBox(),
                "fastening": QComboBox(),
                "sheathing": QComboBox(),
                "armament": QLineEdit(),
                "ship_purpose": QComboBox(),
                "ship_type": QComboBox(),
                "tonnage": QLineEdit(),
                "propulsion": QComboBox(),
                "engine_type": QComboBox(),
                "length": QLineEdit(),
                "breadth": QLineEdit(),
                "hold_depth": QLineEdit(), 
                "build_year": QLineEdit(),
                "builder": QLineEdit(),
                "shipyard": QLineEdit(),
                "ship_documents": QLineEdit(),
                "other_details": QLineEdit()
            },
            "wreck_event": {
                "trade_route": QComboBox(),
                "port_departed": QComboBox(),
                "port_destination": QComboBox(),
                "sequence_of_events": QLineEdit(),
                "historical_event": QLineEdit(),
                "other_details": QLineEdit()
            },
            "registration": {
                "nation": QComboBox(),
                "registered_port": QComboBox(),
                "registration_number": QLineEdit(),
                "owners": QLineEdit(),
                "previous_names": QLineEdit(),
                "sahris_id": QLineEdit()
            },
            "personnel": {
                "captain": QLineEdit(),
                "commander": QLineEdit(),
                "crew": QLineEdit(),
                "passengers": QLineEdit(),
                "number_aboard": QLineEdit(),
                "casualties": QLineEdit(),
                "burial_location": QLineEdit()
            },
            "archaeology": {
                "archaeologists": QLineEdit(),
                "artefacts": QLineEdit(),
                "cargo": QLineEdit(),
                "year_salvaged": QLineEdit(),
                "salvor": QLineEdit(),
                "other_details": QLineEdit()
            },
            "sources": {
                "images": QPushButton("Add Photos"),
                "caption": QLineEdit(),
                "other_sources": QLineEdit()    
            }
        }
    
    return sections


def boxes_dict():
    boxes = {
            "ocean": ["ocean_id", "ocean_name", "oceans"],
            "country": ["country_id", "country_name", "countries"],
            "district": ["district_id", "district_name", "districts"],
            "local_location": ["local_id", "local_name, country_id", "local"],
            "coordinate_type": ["id", "coord_type", "coord_type"],
            "coordinate_confidence": ["id", "confidence", "confidence"],
            "material": ["material_id", "material_name", "materials"],
            "wood_type": ["wood_id", "name", "wood_types"],
            "fastening": ["fastening_id", "fastening_name", "fastening"],
            "sheathing": ["sheathing_id", "sheathing_name", "sheathing"],
            "ship_purpose": ["purpose_id", "reason", "purpose"],
            "ship_type": ["thype_id", "type_name", "type"],
            "propulsion": ["propulsion_id", "propulsion_name", "propulsion"],
            "engine_type": ["engine_id", "engine_name", "engines"],
            "nation": ["id", "nation", "nations"],
            "registered_port": ["id", "port_name", "ports"],
            "trade_route": ["id", "route_name", "trade_routes"],
            "port_departed": ["id", "port_name", "ports"],
            "port_destination": ["id", "port_name", "ports"]
        }
    
    return boxes


def input_dict():
    form_db = {
            # wrecks tab
            "kraken_id": ("wrecks", "kraken_id", None),
            "ship_name": ("wrecks", "name", None),
            "year_lost": ("wrecks", "year_lost", None),
            "date_lost": ("wrecks", "date_lost", None),
            # location tab   
            "ocean": ("locations", "ocean_id", "oceans"),
            "country": ("locations", "country_id", "countries"),
            "district": ("locations", "district_id", "districts"),
            "local_location": ("locations", "local_id", "local"),
            "details_of_location": ("locations", "details", None),
            "reported_coordinates": ("locations", "reported_coords", None),
            "coordinate_confidence": ("locations", "coord_conf", "confidence"),
            "verified_coordinates": ("locations", "verified_coords", None),
            "reported_depth": ("wrecks", "reported_depth", None),
            "latitude": ("wrecks", "y_coord", None),
            "longitude": ("wrecks", "x_coord", None),
            "coordinate_type": ("locations", "coord_type", "coord_type"),
            # materials tab
            "material": ("builds", "material_id", "materials"),
            "wood_type": ("builds", "wood_id", "wood_types"),
            "fastening": ("builds", "fastening_id", "fastening"),
            "sheathing": ("builds", "sheathing_id", "sheathing"),
            "armament": ("extras", "armaments", None),
            "ship_purpose": ("builds", "purpose_id", "purpose"),
            "ship_type": ("builds", "type_id", "type"), 
            "tonnage": ("extras", "tonnage", None),
            "propulsion": ("builds", "propulsion_id", "propulsion"),
            "engine_type": ("builds", "engine_id", "engines"),
            "length": ("extras", "length", None),
            "breadth": ("extras", "breadth", None), 
            "hold_depth": ("extras", "hold_depth", None),
            "build_year": ("extras", "build_year", None),
            "builder": ("extras", "builder", None),
            "shipyard": ("extras", "shipyard", None),
            "ship_documents": ("builds", "ship_docs", None),
            "other_details": ("builds", "ship_details", None),
            # wreck event tab
            "trade_route": ("voyage", "trade_route", "trade_routes"),
            "port_departed": ("voyage", "port_from", "ports"),
            "port_destination": ("voyage", "port_to", "ports"),
            "sequence_of_events": ("extras", "sequence_of_wreck", None),
            "historical_event": ("extras", "historical_event", None),
            "other_details": ("extras", "notes", None),
            # registration tab
            "nation": ("extras", "nation", None),
            "registered_port": ("wrecks", "registered_port", None),
            "registration_number": ("extras", "registration_number", None),
            "owners": ("extras", "owners", None),
            "previous_names": ("extras", "previous_names", None),
            "sahris_id": ("extras", "sahris_id", None),
            # personnel tab
            "captain": ("extras", "captain", None),
            "commander": ("extras", "commander", None),
            "crew": ("extras", "crew", None),
            "passengers": ("extras", "passengers", None),
            "number_aboard": ("extras", "total_aboard", None),
            "casualties": ("extras", "casualties", None),
            "burial_location": ("wrecks", "burial_location", None),
            # archaeology tab
            "archaeologists": ("extras", "archaeologist", None),
            "artefacts": ("extras", "artefacts", None),
            "cargo": ("voyage", "cargo", None),
            "year_salvaged": ("extras", "year_salvaged", None),
            "salvor": ("extras", "salvors", None),
            "other_details": ("misc", "details", None),
            # sources tab
            "images": ("images", "image_path", "multiple", None),
            "caption": ("images", "caption", None),
            "other_sources": ("images", "source", None)
        }
    
    return form_db