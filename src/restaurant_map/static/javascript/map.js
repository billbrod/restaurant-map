async function getData() {
  let response = await fetch("/points.json")
  if (!response.ok) {
    throw new Error(`Response status: ${response.status}`)
  }
  return await response.json();
}

data = getData()

const map = new maplibregl.Map({
  container: "map",
  style: 'https://tiles.openfreemap.org/styles/liberty',
  zoom: 11,
  center: [-73.925, 40.776],
})
// Add geolocate control to the map.
let geolocate = new maplibregl.GeolocateControl({
  positionOptions: {
    enableHighAccuracy: true
  },
})
map.addControl(geolocate);
map.on('load', async () => {
  geolocate.trigger();
  let points = await data;
  map.addSource("locations", {
    type: "geojson",
    data: points,
    cluster: true,
    clusterMaxZoom: 14, // Max zoom to cluster points on
    clusterRadius: 50 // Radius of each cluster when clustering points (defaults to 50)
  })
  map.addLayer({
    id: "unclustered-points",
    type: "circle",
    source: "locations",
    paint: {
      "circle-color": "#11b4da",
      "circle-radius": 5,
      "circle-stroke-width": 1,
      "circle-stroke-color": "#000",
    },
  })
  map.addLayer({
    id: 'clusters',
    type: 'circle',
    source: 'locations',
    filter: ['has', 'point_count'],
    paint: {
      // Use step expressions with three steps to implement three types of circles:
      //   * Blue, 20px circles when point count is less than 3
      //   * Yellow, 30px circles when point count is between 3 and 5
      //   * Pink, 40px circles when point count is greater than or equal to 5
      'circle-color': [
        'step',
        ['get', 'point_count'],
        '#51bbd6',
        3,
        '#f1f075',
        5,
        '#f28cb1'
      ],
      'circle-radius': [
        'step',
        ['get', 'point_count'],
        20,
        3,
        30,
        5,
        40
      ]
    }
  });
  map.addLayer({
    id: 'cluster-count',
    type: 'symbol',
    source: 'locations',
    filter: ['has', 'point_count'],
    layout: {
      'text-field': '{point_count_abbreviated}',
      'text-font': ['Noto Sans Regular'],
      'text-size': 12
    }
  });
  // inspect a cluster on click
  map.on('click', 'clusters', async (e) => {
    const features = map.queryRenderedFeatures(e.point, {
      layers: ['clusters']
    });
    const clusterId = features[0].properties.cluster_id;
    const zoom = await map.getSource('locations').getClusterExpansionZoom(clusterId);
    map.easeTo({
      center: features[0].geometry.coordinates,
      zoom
    });
  });
  map.on('click', 'unclustered-points', (e) => {
    const coordinates = e.features[0].geometry.coordinates.slice();
    const properties = e.features[0].properties;

    let popup_text = `<div class="py-1 text-lg text-center uppercase font-bold">${properties.name}</div>`
    properties.tags.split(',').sort().forEach(tag => {
      let tag_class = tag.toLowerCase().replaceAll(' ', '-')
      popup_text = popup_text + `<div class="mx-10 text-sm text-slate-200 ${tag_class} text-center">${tag}</div>`
    })
    popup_text = popup_text + `<div class="py-1 px-1 text-sm text-slate-600">${properties.address}</div>`
    popup_text = popup_text + `<span class="py-1 px-1 text-sm text-slate-600">${properties.description}</span>`

    // Ensure that if the map is zoomed out such that
    // multiple copies of the feature are visible, the
    // popup appears over the copy being pointed to.
    while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
      coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    }

    new maplibregl.Popup()
                  .setLngLat(coordinates)
                  .setHTML(popup_text)
                  .addTo(map);
  });
})
