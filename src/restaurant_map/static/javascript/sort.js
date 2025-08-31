function euclidean_distance(x, y) {
  return Math.sqrt(Math.pow(x[0] - y[0], 2) + Math.pow(x[1] - y[1], 2))
}

function convert_str_to_lngLat(lngLat) {
    return lngLat.split(',').map(x => parseFloat(x))
}

function sort_by_distance(target_location) {
  // from https://stackoverflow.com/a/9436948
  if (typeof target_location === 'string' || target_location instanceof String) {
    target_location = convert_str_to_lngLat(target_location)
  } else if (!Array.isArray(target_location)) {
    target_location = [target_location['lng'], target_location['lat']]
  }
  return function(a, b) {
    var coords_a = convert_str_to_lngLat($(a).data("coords"))
    var coords_b = convert_str_to_lngLat($(b).data("coords"))
    dist_a = euclidean_distance(coords_a, target_location)
    dist_b = euclidean_distance(coords_b, target_location)
    return (dist_a < dist_b) ? -1 : (dist_a > dist_b) ? 1 : 0;
  }
}
