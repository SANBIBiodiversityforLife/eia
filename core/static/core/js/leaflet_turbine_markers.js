/*var turbineIcon = new L.icon({
    iconUrl: '/static/core/img/icons/turbine-icon.png',
    shadowUrl: '/static/core/img/icons/turbine-shadow.png',

    iconSize:     [48, 63], // size of the icon
    shadowSize:   [66, 33], // size of the shadow
    iconAnchor:   [24.2, 60], // point of the icon which will correspond to marker's location
    shadowAnchor: [14, 30],  // the same for the shadow
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});
var myStyle = {
    "color": "#ff7800",
    "weight": 5,
    "opacity": 0.65
};*/

var turbineIcon = L.AwesomeMarkers.icon({
    prefix: 'fa', //font awesome rather than bootstrap
    markerColor: 'orange', // see colors above
    icon: 'asterisk' //http://fortawesome.github.io/Font-Awesome/icons/
});