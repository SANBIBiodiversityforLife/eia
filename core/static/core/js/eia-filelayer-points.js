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
            // Add to map after loading (default: true) ?
            addToMap: false,
        });
        control.addTo(map);

        // When the fileLayer has loaded some data (i.e. someone has loaded a file)
        control.loader.on('data:loaded', function (e) {
            // Get the geojson layer which gets added from the file layers
            gLayer = e.layer.getLayers()[0];

            // Groups of points always seem to be geometrycollections
            if(gLayer.feature.geometry.type != 'GeometryCollection') {
                alert('Invalid geometry (' + gLayer.feature.geometry.type + '). You must upload only points for turbines.');
                location.reload(true);
                return;
            }

            // Presumably you can have geometrycollections of lines etc, so don't allow this
            $(gLayer.feature.geometry.geometries).each(function(index, obj){
                if(obj.type != 'Point') {
                    alert('Invalid geometry (' + obj.type + '). You must upload only points for turbines.');
                    location.reload(true);
                    return;
                }
            });

            // These are the LatLong points
            oldLatLngs = gLayer.getLayers(); // Note for polygons this is getLatLngs()


            // If it's a KML it will have altitude, so iterate through and strip them out
            $(oldLatLngs).each(function(index, obj) {
                oldLatLng = obj.getLatLng();
                newLatLng = {lat: oldLatLng.lat, lng: oldLatLng.lng}; // Can also: new L.LatLng(obj.lat, obj.lng);
                obj.setLatLng(newLatLng);
                //lg = L.layerGroup(newLatLng);
                //gLayer.addLayer(lg);
                //lg.editable.enable();
                //newLatLngs.push(newLatLng);
            })

            // If someone has drawn something previously we need to wipe it
            drawnItems.eachLayer(function(l) {
                map.removeLayer(l);
            })
            drawnItems.clearLayers();

            // Add the points to the map and to drawnitems
            $(gLayer.getLayers()).each(function(index, obj){
                map.addLayer(obj);
                drawnItems.addLayer(obj);
            });

            // Django-leaflet does this so just copy it
            store.save(drawnItems);
        });
    });
})