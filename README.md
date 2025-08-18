# restaurant-map

Simple site for saving restaurants, using FastAPI, htmx, tinydb and folium. based on [simplesite](https://github.com/tataraba/simplesite/tree/main) for basic structure.

## Build

- Use `uv` and install with `uv sync`
- Then create the css with tailwind: `uv run tailwindcss -i src/restaurant_map/static/src/input.css -o src/restaurant_map/static/css/main.css` 
- Then run the map with `uv run app`, then will be live at `localhost:8011`


