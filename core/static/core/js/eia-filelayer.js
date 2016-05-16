$(document).ready(function() {
    // This function is called when the map initializes (automatically via django-leaflet)
    $(window).on('map:init', function(e) {
        // Get a reference to the map
        //map = e.originalEvent.detail.map;
        map = e.detail.map;

        // Store the featureGroup (drawnItems) which django-leaflet's drawControl uses to submit to the form
        var drawnItems;
        var store;
        map.on('map:loadfield', function (e) {
            drawnItems = e.field.drawnItems;
            store = e.field.store;
        });

        // Add the filelayer to allow the uploading of files
        control = L.Control.fileLayerLoad({
            // See http://leafletjs.com/reference.html#geojson-options
            layerOptions: {
                style: { color:'red' },
                //onEachFeature: function(feature){ drawnItems.addLayer(feature); },
            },

            // Add to map after loading (default: true) ?
            addToMap: false,
        });
        control.addTo(map);

        // When the fileLayer has loaded some data (i.e. someone has loaded a file)
        control.loader.on('data:loaded', function (e) {
            // Get the geojson layer which gets added from the file layers
            gLayer = e.layer.getLayers()[0];

            // Only allow polygons to proceed
            if(gLayer.feature.geometry.type != 'Polygon') {
                alert('Invalid geometry (' + gLayer.feature.geometry.type + '). You must upload only a single polygon.');
                location.reload(true);
            }

            // If it's a KML it will have altitude, so iterate through and strip them out
            newLatLngs = []
            oldLatLngs = gLayer.getLatLngs();
            $(oldLatLngs).each(function(index, obj) {
                newLatLng = {lat: obj.lat, lng: obj.lng} // Can also: new L.LatLng(obj.lat, obj.lng);
                newLatLngs.push(newLatLng);
            })

            // Set the new latlngs for the polygon
            gLayer.setLatLngs(newLatLngs);

            // If someone has drawn something previously we need to wipe it
            drawnItems.eachLayer(function(l) {
                map.removeLayer(l);
            })
            drawnItems.clearLayers();

            // Add the polygon to the map, not sure why this is required but django-leaflet does this
            map.addLayer(gLayer)

            // Add the polygon to the drawnItems featureGroup
            drawnItems.addLayer(gLayer);

            // Django-leaflet does this so just copy it
            store.save(drawnItems);
        });
    });
})