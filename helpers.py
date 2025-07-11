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
        get_country_id_by_name
):
        """Update country and local dropdowns based on selected ocean or country."""

        # country => (country_id, country_name, ocean_id)
        # local => (local_id, local_name, country_id, ocean_id)
        # oceans => (ocean_id, ocean_name)

        selected_ocean = oceans_input.currentText().strip()
        selected_country = countries_input.currentText().strip()  
        selected_local = local_input.currentText().strip()

        # Reset all dropdowns first to avoid duplication
        oceans_input.blockSignals(True)
        countries_input.blockSignals(True)
        local_input.blockSignals(True)

        prev_country = countries_input.currentText().strip()
        prev_local = local_input.currentText().strip()
        prev_ocean = oceans_input.currentText().strip()


        if source == "ocean":
            
            if selected_ocean != "All Oceanss":
                # Filter countries that border selected ocean
                filtered_countries = [c for c in countries if (c[0], get_ocean_id_by_name(selected_ocean)) in country_ocean]
                countries_input.clear()
                countries_input.addItem("All Countriess")
                for country in filtered_countries:
                    countries_input.addItem(country[1])
                if prev_country in [country[1] for country in filtered_countries]:
                    countries_input.setCurrentText(prev_country)
                else:
                    countries_input.setCurrentIndex(0) 

                # Filter locals that also border same ocean
                country_ids = [co[0] for co in country_ocean if co[1] == get_ocean_id_by_name(selected_ocean)]
                filtered_locals = [l for l in local if l[2] in country_ids]
                local_input.clear()
                local_input.addItem("All Locals")
                for local in filtered_locals:
                    local_input.addItem(local[1])
                if prev_local in [local[1] for local in filtered_locals]:
                    local_input.setCurrentText(prev_local)
                else:
                    local_input.setCurrentIndex(0)
            else:
                countries_input.clear()
                countries_input.addItem("All countriess")
                for o in countries:
                    countries_input.addItem(o[1])
                countries_input.setCurrentIndex(0)

                local_input.clear()
                local_input.addItem("All Locals")
                for l in local:
                    local_input.addItem(l[1])
                local_input.setCurrentIndex(0)

        elif source == "country":
            country_id = get_country_id_by_name(selected_country)

            if selected_country != "All Countriess":
                # Filter oceans connected to this country
                ocean_ids = [co[1] for co in country_ocean if co[0] == country_id]
                filtered_oceans = [o for o in oceans if o[0] in ocean_ids]
                oceans_input.clear()
                oceans_input.addItem("All Oceans")
                for o in filtered_oceans:
                    oceans_input.addItem(o[1])
                if prev_ocean in [o[1] for ocean in filtered_oceans]:
                    oceans_input.setCurrentText(prev_ocean)
                else:
                    oceans_input.setCurrentIndex(0)

                # Filter locals connected to this country
                filtered_locals = [l for l in local if l[2] == country_id]
                local_input.clear()
                local_input.addItem("All Locals")
                for l in filtered_locals:
                    local_input.addItem(l[1])
                if prev_local in [l[1] for local in filtered_locals]:
                    local_input.setCurrentText(prev_local)
                else:
                    local_input.setCurrentIndex(0)
            else:
                # Reload full oceans and locals list
                oceans_input.clear()
                oceans_input.addItem("All Oceans")
                for o in oceans:
                    oceans_input.addItem(o[1])
                oceans_input.setCurrentIndex(0)

                local_input.clear()
                local_input.addItem("All Locals")
                for l in local:
                    local_input.addItem(l[1])
                local_input.setCurrentIndex(0)

        elif source == "local":
            if selected_local != "All Locals":
                # Get local row
                local_row = next((l for l in local if l[1] == selected_local), None)
                if local_row:
                    country_id = local_row[2]
                    ocean_ids = [co[1] for co in country_ocean if co[0] == country_id]

                    filtered_country = next((c for c in countries if c[0] == country_id), None)
                    countries_input.clear()
                    countries_input.addItem("All Countriess")
                    if filtered_country:
                        countries_input.addItem(filtered_country[1])
                        if prev_country == filtered_country:
                            countries_input.setCurrentText(prev_country)
                        else:
                            countries_input.setCurrentIndex(1)
                    else:
                        countries_input.setCurrentIndex(0)

                    filtered_oceans = [o for o in oceans if o[0] in ocean_ids]
                    oceans_input.clear()
                    oceans_input.addItem("All Oceanss")
                    for ocean in filtered_oceans:
                        oceans_input.addItem(ocean[1])
                    if prev_ocean in [ocean[1] for ocean in filtered_oceans]:
                        oceans_input.setCurrentText(prev_ocean)
                    else:
                        oceans_input.setCurrentIndex(0)
            else:
                oceans_input.clear()
                oceans_input.addItem("All Oceans")
                for o in oceans:
                    oceans_input.addItem(o[1])
                oceans_input.setCurrentIndex(0)

                countries_input.clear()
                countries_input.addItem("All countriess")
                for o in countries:
                    countries_input.addItem(o[1])
                countries_input.setCurrentIndex(0)

        else:
            # No filters selected: show all
            oceans_input.clear()
            oceans_input.addItem("All Oceanss")
            for o in oceans:
                oceans_input.addItem(o[1])
            oceans_input.setCurrentIndex(0)

            countries_input.clear()
            countries_input.addItem("All Countrys")
            for c in countries:
                countries_input.addItem(c[1])
            countries_input.setCurrentIndex(0)

            local_input.clear()
            local_input.addItem("All Locals")
            for l in local:
                local_input.addItem(l[1])
            local_input.setCurrentIndex(0)

            oceans_input.blockSignals(False)
            countries_input.blockSignals(False)
            local_input.blockSignals(False)

        oceans_input.blockSignals(False)
        countries_input.blockSignals(False)
        local_input.blockSignals(False) 
        

def get_country_id_by_name(name, countries):
        return next((c[0] for c in countries if c[1] == name), None)


def get_ocean_id_by_name(name, oceans):
    return next((o[0] for o in oceans if o[1] == name), None)