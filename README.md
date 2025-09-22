# restaurant-map

Simple site for saving restaurants, using FastAPI, htmx, tinydb and maplibre-gl. based on [simplesite](https://github.com/tataraba/simplesite/tree/main) for basic structure.

## Build

- Use `uv` and install with `uv sync`
- Then create the css with tailwind: `uv run tailwindcss -i src/restaurant_map/static/src/input.css -o src/restaurant_map/static/css/main.css` 
- Then run the map with `uv run fastapi dev src/restaurant_map/main.py --port 8011`, then will be live at `localhost:8011` (or pass `run` instead fo `dev` for production)

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
    - [ ] url(s)
- [x] on both view, click on either map or list should jump corresponding pointin other
    - list to map: can call map.flyTo with the coordinates directly
    - map to list: need to check which view we're in, to determine whether to highlight on list or display popup
        - add list sort by distance to click, and just trigger that
- [x] on both view, sort by distance from current location
- [ ] ingest geojson:
    - [ ] don't add duplicate based on coordinates
    - [ ] add ability to add tag to all imported points
    - [ ] add ability to do through website?
- [x] color circle based on tag. 
    - [ ] right now just picking a tag, but should pick something reasonable in ontoogy 
- [x] add name when zoomed in on all the way
- [x] add toggles for included fields
- [x] filter by tag on map, not just list
- [ ] add export to text, with toggles for which fields to include
    - [ ] export button, one for geojson, one for text, which just exports current view (filtered etc)
- [ ] check how exported geojson works with organic maps or osmand
- [ ] add create / import backup, to run from command line
    - [ ] import backup will overwrite everythign
    - [ ] create backup will include all tables
    - [ ] then create script that runs create backup regularly, git committing output
- [x] show tags at top of page and filter them by tapping on them
- [x] then [ch 4](https://github.com/tataraba/simplesite/blob/main/docs/04_Chapter_4.md)
- [ ] add point: with all fields, autocomplete existing tags. add ability to put in either coordinates or address and geocode to other
    - [ ] import, go right to add point, pre-completing those fields. then test with google maps, organic maps, etc
- [x] bulk edit tags: click to select locations and then add/remove tags to all, auto-completing
- [x] list should be easy to filter, sort, and include/exclude various info
    - [x] should have "more info" button, which shows everything about current point. same as edit view, but can't edit
- [ ] tag view? showing all tags, with number of tagged places, and making ontology clear
- [ ] lists: add selected points / tags to list, then have separate ability to just view them
- [ ] make website a [progressive web
      app](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps#tutorials)
      with offline support
    - offline should be readonly? would it be possible to get it working for other people who won't be connected to my webserver all the time
        - I don't think so, because there's so much interaction with web server
        - if I wanted to, the proper way to do this with PWA is to use IndexedDB, and [this synceddb](https://github.com/darrachequesne/synceddb) package looks like a way to sync with remote server via REST API
        - but I think instead my preferred thing "fully offline" would be to just export what I want and load into CoMaps
    - [maplibre use local geojson](https://maplibre.org/maplibre-gl-js/docs/examples/view-local-geojson/)
- [ ] PWA:
    - [ ] make it able to accept data shared from other apps (ideally, google maps and other maps)
    - [ ] I think can export to phone using [File System API](https://developer.mozilla.org/en-US/docs/Web/API/File_System_API)
    - [ ] and do it regularly with [Periodic Background Sync API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Periodic_Background_Synchronization_API)
- [ ] offline maps? using pmtiles? resources
    - [maplibre issue](https://github.com/maplibre/maplibre-gl-js/discussions/1580)
    - [pmtiles docs](https://docs.protomaps.com/pmtiles/maplibre)
    - [maplibre docs](https://web.archive.org/web/20250822100700/https://maplibre.org/maplibre-gl-js/docs/examples/pmtiles-source-and-protocol/)
    - [stackoverflow question](https://stackoverflow.com/questions/68853853/load-local-mbtiles-with-maplibre-gl-js)
- [ ] search on map with [geocoder](https://maplibre.org/maplibre-gl-js/docs/examples/geocode-with-nominatim/)?
    - could use [geocodio](https://www.geocod.io/pricing/#tier-payg-section)? [docs](https://www.geocod.io/docs/?shell#geocoding)
- [ ] pack it up [as docker](https://docs.astral.sh/uv/guides/integration/fastapi/#migrating-an-existing-fastapi-project) to run

## Related links

- [geocoding](https://pythonsimplified.com/geocoding-in-python-using-geopy/) with geopy
- [htmx](https://htmx.org/examples/click-to-edit/)
- [tailwindcss docs](https://tailwindcss.com/docs/padding#adding-horizontal-padding)
- [blog with info](https://ogbe.net/blog/self-hosted-maps#org0ba42d4) about self-hosted mapping
