import sqlite3
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QComboBox


def location_change(
        source,
        selected_ocean,
        selected_country,
        selected_local,
        oceans,
        countries,
        local,
        country_ocean,
        oceans_input,
        countries_input,
        local_input,
        get_ocean_id_by_name,
        get_country_id_by_name,
        placeholder=None
):
        """Update country and local dropdowns based on selected ocean or country."""

        # country => (country_id, country_name, ocean_id)
        # local => (local_id, local_name, country_id, ocean_id)
        # oceans => (ocean_id, ocean_name)

        selected_ocean = oceans_input.currentText().strip()
        selected_country = countries_input.currentText().strip()  
        selected_local = local_input.currentText().strip()

        # Set the placeholder texts if none were given
        if placeholder is None:
            placeholder = {
                "ocean": "All Oceans",
                "country": "All Countries",
                "local": "All Locals"
            }

        # Reset all dropdowns first to avoid duplication
        oceans_input.blockSignals(True)
        countries_input.blockSignals(True)
        local_input.blockSignals(True)

        # Store current selections to preserve them
        prev_country = countries_input.currentText().strip()
        prev_local = local_input.currentText().strip()
        prev_ocean = oceans_input.currentText().strip()

        if source == "ocean":
            
            if selected_ocean != placeholder.get("ocean", ""):
                # Filter countries that border selected ocean

                ocean_id = get_ocean_id_by_name(selected_ocean)

                if ocean_id is not None:
                    ocean_id = ocean_id[0]
                filtered_countries = [c for c in countries if c[0] in [co[0] for co in country_ocean if co[1] == ocean_id]]
                countries_input.clear()
                countries_input.addItem(placeholder.get("country", ""))
                for country in filtered_countries:
                    countries_input.addItem(country[1])
                
                # Preserve selection if it's still valid, otherwise reset
                if prev_country in [country[1] for country in filtered_countries]:
                    countries_input.setCurrentText(prev_country)
                else:
                    countries_input.setCurrentIndex(0)

                # Filter locals that also border same ocean
                country_ids = [co[0] for co in country_ocean if co[1] == ocean_id]
                filtered_locals = [l for l in local if l[2] in country_ids]
                local_input.clear()
                local_input.addItem(placeholder.get("local", ""))
                for local_item in filtered_locals:
                    local_input.addItem(local_item[1])
                
                # Preserve selection if it's still valid, otherwise reset
                if prev_local in [local_item[1] for local_item in filtered_locals]:
                    local_input.setCurrentText(prev_local)
                else:
                    local_input.setCurrentIndex(0)
            else:
                # "All Oceans" selected - reset countries and locals to show all options
                countries_input.clear()
                countries_input.addItem(placeholder.get("country", ""))
                for country in countries:
                    countries_input.addItem(country[1])
                countries_input.setCurrentIndex(0)  # Reset to placeholder

                local_input.clear()
                local_input.addItem(placeholder.get("local", ""))
                for local_item in local:
                    local_input.addItem(local_item[1])
                local_input.setCurrentIndex(0)  # Reset to placeholder

        elif source == "country":

            country_id = get_country_id_by_name(selected_country)

            if selected_country != placeholder.get("country", ""):
                # Filter oceans connected to this country
                if country_id is not None:
                    country_id = country_id[0]
                ocean_ids = [co[1] for co in country_ocean if co[0] == country_id]
                filtered_oceans = [o for o in oceans if o[0] in ocean_ids]
                oceans_input.clear()
                oceans_input.addItem(placeholder.get("ocean", ""))
                for ocean in filtered_oceans:
                    oceans_input.addItem(ocean[1])
                
                # Preserve selection if it's still valid, otherwise reset
                if prev_ocean in [ocean[1] for ocean in filtered_oceans]:
                    oceans_input.setCurrentText(prev_ocean)
                else:
                    oceans_input.setCurrentIndex(0)

                # Filter locals connected to this country
                filtered_locals = [l for l in local if l[2] == country_id]
                local_input.clear()
                local_input.addItem(placeholder.get("local", ""))
                for local_item in filtered_locals:
                    local_input.addItem(local_item[1])
                
                # Preserve selection if it's still valid, otherwise reset
                if prev_local in [local_item[1] for local_item in filtered_locals]:
                    local_input.setCurrentText(prev_local)
                else:
                    local_input.setCurrentIndex(0)
            else:
                # "All Countries" selected - reset oceans and locals to show all options
                oceans_input.clear()
                oceans_input.addItem(placeholder.get("ocean", ""))
                for ocean in oceans:
                    oceans_input.addItem(ocean[1])
                oceans_input.setCurrentIndex(0)  # Reset to placeholder

                local_input.clear()
                local_input.addItem(placeholder.get("local", ""))
                for local_item in local:
                    local_input.addItem(local_item[1])
                local_input.setCurrentIndex(0)  # Reset to placeholder

        elif source == "local":
            if selected_local != placeholder.get("local", ""):
                # Get local row
                local_row = next((l for l in local if l[1] == selected_local), None)
                if local_row:
                    country_id = local_row[2]
                    ocean_ids = [co[1] for co in country_ocean if co[0] == country_id]

                    # Set country to the one this local belongs to
                    filtered_country = next((c for c in countries if c[0] == country_id), None)
                    countries_input.clear()
                    countries_input.addItem(placeholder.get("country", ""))
                    if filtered_country:
                        countries_input.addItem(filtered_country[1])
                        countries_input.setCurrentText(filtered_country[1])

                    # Set oceans connected to this country
                    filtered_oceans = [o for o in oceans if o[0] in ocean_ids]
                    oceans_input.clear()
                    oceans_input.addItem(placeholder.get("ocean", ""))
                    for ocean in filtered_oceans:
                        oceans_input.addItem(ocean[1])
                    
                    # Preserve selection if it's still valid, otherwise reset
                    if prev_ocean in [ocean[1] for ocean in filtered_oceans]:
                        oceans_input.setCurrentText(prev_ocean)
                    else:
                        oceans_input.setCurrentIndex(0)
            else:
                # "All Locals" selected - reset oceans and countries to show all options
                oceans_input.clear()
                oceans_input.addItem(placeholder.get("ocean", ""))
                for ocean in oceans:
                    oceans_input.addItem(ocean[1])
                oceans_input.setCurrentIndex(0)  # Reset to placeholder

                countries_input.clear()
                countries_input.addItem(placeholder.get("country", ""))
                for country in countries:
                    countries_input.addItem(country[1])
                countries_input.setCurrentIndex(0)  # Reset to placeholder

                # Also reset local dropdown to show all options
                local_input.clear()
                local_input.addItem(placeholder.get("local", ""))
                for local_item in local:
                    local_input.addItem(local_item[1])
                local_input.setCurrentIndex(0)  # Reset to placeholder

        else:
            # No filters selected: show all
            oceans_input.clear()
            oceans_input.addItem(placeholder.get("ocean", ""))
            for ocean in oceans:
                oceans_input.addItem(ocean[1])
            oceans_input.setCurrentIndex(0)

            countries_input.clear()
            countries_input.addItem(placeholder.get("country", ""))
            for country in countries:
                countries_input.addItem(country[1])
            countries_input.setCurrentIndex(0)

            local_input.clear()
            local_input.addItem(placeholder.get("local", ""))
            for local_item in local:
                local_input.addItem(local_item[1])
            local_input.setCurrentIndex(0)

        oceans_input.blockSignals(False)
        countries_input.blockSignals(False)
        local_input.blockSignals(False)
        

def get_country_id_by_name(name):
    
    conn = sqlite3.connect("shipwrecks.db")
    c = conn.cursor()
    c.execute(f"SELECT country_id FROM countries WHERE country_name = ?", (name,))
    id = c.fetchone()
    conn.close()
    return id


def get_ocean_id_by_name(name):

    conn = sqlite3.connect("shipwrecks.db")
    c = conn.cursor()
    c.execute(f"SELECT ocean_id FROM oceans WHERE ocean_name = ?", (name,))
    id = c.fetchone()
    conn.close()
    return id


def change_height(widget):
    text_edit = widget
    
    # Get the document and ensure it's properly sized
    document = text_edit.document()
    
    # Set document width to match the text edit's content width
    content_width = text_edit.width() - text_edit.contentsMargins().left() - text_edit.contentsMargins().right() - 20  # Account for scrollbar
    document.setTextWidth(content_width)
    
    # Get the actual document height
    doc_height = int(document.size().height())
    
    # Add margins but no padding
    margins = text_edit.contentsMargins()
    frame_width = text_edit.frameWidth() * 2
    
    # Minimum height for at least one line
    font_metrics = text_edit.fontMetrics()
    min_height = font_metrics.lineSpacing() + margins.top() + margins.bottom() + frame_width
    
    height = max(min_height, doc_height + margins.top() + margins.bottom() + frame_width)
    
    text_edit.setFixedHeight(height)


def update_id(ship):
    """ Gets The Ship ID Of What Ship Is Selected """
    conn = sqlite3.connect("shipwrecks.db")
    c = conn.cursor()
    c.execute("SELECT id, location_row_ID, build_id FROM wrecks WHERE name = ?", (ship,))
    ids = c.fetchone()
    conn.close()
    return ids


def get_widget_value(widget, key):
        if isinstance(widget, QLineEdit):
            if widget.text() != "":
                value = widget.text()
                return value

        elif isinstance(widget, QComboBox):
            if widget.currentText() != "":
                value = widget.currentText()
                return value

        elif isinstance(widget, QTextEdit):
            if widget.toPlainText() != "":
                value = widget.toPlainText()
                return value
            

def get_id_by_name(value, lookup):
        conn = sqlite3.connect("shipwrecks.db")
        c = conn.cursor()
        c.execute(f"SELECT * FROM {lookup}")
        data = c.fetchall()
        for row in data:
            if value in row:
                for field in row:
                    if isinstance(field, int):
                        conn.close()
                        return field 


def link_im_cap(id, image=None, caption=None):
        """ Links The Images To The Captions And Returns A Tuple of (image_path, caption) """
        image_data = []

        if image == None and caption == None:
            conn = sqlite3.connect("shipwrecks.db")
            c = conn.cursor()
            c.execute("SELECT image_path FROM images WHERE ship_id = ?", (id,))
            image_paths = c.fetchall()
            c.execute("SELECT caption FROM images WHERE ship_id = ?", (id,))
            captions = c.fetchall()
            conn.close()
        else:
            image_paths = image
            captions = caption

        for i, image_path in enumerate(image_paths):
            if i < len(captions):
                caption = captions[i]
            else: 
                caption = "No Caption Available"

            image_data.append((image_path, caption))
        
        return image_data