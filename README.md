# restaurant-map

Simple site for saving restaurants, using FastAPI, htmx, tinydb and folium. based on [simplesite](https://github.com/tataraba/simplesite/tree/main) for basic structure.

## Build

- Use `uv` and install with `uv sync`
- Then create the css with tailwind: `uv run tailwindcss -i src/restaurant_map/static/src/input.css -o src/restaurant_map/static/css/main.css` 
- Then run the map with `uv run app`, then will be live at `localhost:8011`

## todo

- add types to tags? type, subtypes, cuisines, details
    - then display tags in that order, sorted within each category
    - if type not specified, consider it a detail
- show tags at top of page and filter them by tapping on them
- add folium view
- then [ch 4](https://github.com/tataraba/simplesite/blob/main/docs/04_Chapter_4.md)

## Related links

- html in folium popups:
    - [dynamic folium marker](https://stackoverflow.com/questions/77050363/how-to-create-a-dynamic-folium-marker)
    - [html in folium](https://towardsdatascience.com/use-html-in-folium-maps-a-comprehensive-guide-for-data-scientists-3af10baf9190/)
    - [formatted popups](https://github.com/python-visualization/folium/issues/1596)
- [geocoding](https://pythonsimplified.com/geocoding-in-python-using-geopy/) with geopy
- [htmx](https://htmx.org/examples/click-to-edit/)
- [tailwindcss docs](https://tailwindcss.com/docs/padding#adding-horizontal-padding)
- [using folium with flask](https://python-visualization.github.io/folium/latest/advanced_guide/flask.html)
- [grouping features with folium](https://python-visualization.github.io/folium/latest/user_guide/plugins/featuregroup_subgroup.html)
- [pmtiles with leaflet](https://docs.protomaps.com/pmtiles/leaflet)
- [folium pmtiles](https://pypi.org/project/folium-pmtiles/)
- [blog with info](https://ogbe.net/blog/self-hosted-maps#org0ba42d4) about self-hosted mapping
