$(document).ready(function() {
    // This function is called when the map initializes (automatically via django-leaflet)
    $(window).on('map:init', function(e) {
        // Get a reference to the map
        map = e.originalEvent.detail.map;

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
                style: {color:'red'},
                //onEachFeature: function(feature){ drawnItems.addLayer(feature); },
            },

            // Add to map after loading (default: true) ?
            addToMap: false,
        });
        control.addTo(map);

        // Every time a file is put on we need to wipe the previous layers
        /*control.loader.on('data:loading', function (e) {
            // Iterate over the layers
            map.eachLayer(function(layer) {
                // Check to make sure that we're not getting rid of the base map
                if(layer._latlngs)
                    map.removeLayer(layer);

                // We need to wipe all of the layers from the drawnItems featureGroup as well
                // It seems that when drawing a polygon it adds the polygon layer with latlongs and a separate layer
                // to the drawnItems featureGroup
                //if(layer._layers)
                //    layer.clearLayers();
            });
        });*/

        // When the fileLayer has loaded some data (i.e. someone has loaded a file)
        control.loader.on('data:loaded', function (e) {
            // Get the geojson layer which gets added from the file layers
            gLayer = e.layer.getLayers()[0];

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
            /*
            map.eachLayer(function(layer) {
                if(layer._layers) {
                    layer.clearLayers();
                    //console.log('yes layers VV')
                }
                else {
                    //console.log('no layers VV')
                }
            });*/
            // Add the polygon to the map because django-leaflet seems to
            map.addLayer(gLayer)

            // Add the polygon to the drawnItems featureGroup
            drawnItems.addLayer(gLayer);

            // Django-leaflet seems to do this so just copy him until something works
            store.save(drawnItems);
        });

        // Every time someone draws something we need to wipe the previous layers
        /*map.on('draw:created', function (e) {
            // Iterate over the layers
            map.eachLayer(function(layer) {
                // Check to make sure that we're not getting rid of the base map
                if(layer._latlngs) {
                    map.removeLayer(layer);
                }
            });
        });*/

        // Just stopping it from submitting while we are debugging.
        /*$('form').submit(function(event) {
            console.log($('form'));
            console.log($('form').serialize());
            event.preventDefault();
        });*/
    });
})