# restaurant-map

Simple site for saving restaurants, using FastAPI, htmx, tinydb and maplibre-gl. based on [simplesite](https://github.com/tataraba/simplesite/tree/main) for basic structure.

## Build

- Use `uv` and install with `uv sync`
- Then create the css with tailwind: `uv run tailwindcss -i src/restaurant_map/static/src/input.css -o src/restaurant_map/static/css/main.css` 
- Then run the map with `uv run app`, then will be live at `localhost:8011`

## todo

- [ ] add types to tags? type, subtypes, cuisines, details
    - [ ] then display tags in that order, sorted within each category
    - [ ] if tag type not specified, consider it a detail
    - [ ] priority? something to specify places I want to try
    - [ ] only one type allowed (restaurant, bakery, grocery), but any number for the others
    - [ ] and then separate color maps within each?
- [ ] also add to db:
    - [ ] visited: date, rating, review, dishes (with four point scale: incredible, good, fine, bad)
    - [ ] should there be an overall rating? which is just mean of all ratings? or have an option to do something like mean/latest?
    - [x] id: hash of coordinates, then use that for selections
- [ ] on both view, click on either map or list should jump corresponding pointin other
- [ ] on both view, sort by distance from current location
- [ ] ingest geojson:
    - [ ] don't add duplicate based on coordinates
- [ ] add export to text, with toggles for which fields to include
- [ ] check how exported geojson works with organic maps or osmand
- [ ] show tags at top of page and filter them by tapping on them
- [ ] then [ch 4](https://github.com/tataraba/simplesite/blob/main/docs/04_Chapter_4.md)
- [ ] add point: with all fields, autocomplete existing tags. add ability to put in either coordinates or address and geocode to other
    - [ ] import, go right to add point, pre-completing those fields. then test with google maps, organic maps, etc
- [ ] bulk edit tags: click to select locations and then add/remove tags to all, auto-completing
- [ ] list should be easy to filter, sort, and include/exclude various info
    - [ ] should have "more info" button, which shows everything about current point. same as edit view, but can't edit
- [ ] tag view? showing all tags, with number of tagged places, and making ontology clear
- [ ] lists: add selected points / tags to list, then have separate ability to just view them

## Related links

- [geocoding](https://pythonsimplified.com/geocoding-in-python-using-geopy/) with geopy
- [htmx](https://htmx.org/examples/click-to-edit/)
- [tailwindcss docs](https://tailwindcss.com/docs/padding#adding-horizontal-padding)
- [blog with info](https://ogbe.net/blog/self-hosted-maps#org0ba42d4) about self-hosted mapping
