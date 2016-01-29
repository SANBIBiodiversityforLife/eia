$(document).ready(function() {
    // When the map init functions we need to do a few things
    $(window).on('map:init', function(e) {
      console.log(e);
      map = e.originalEvent.detail.map;
      //var map = e.map;
      console.log(map.drawControl);
      console.log(map.drawnItems);
      console.log(map._editionLayer);
      var featureGroup;
       map.on('map:loadfield', function (e) {
            console.log('pay attention');
            console.log(e);
            featureGroup = e.field.drawnItems;
            console.log(featureGroup);
           //map.drawControl.setDrawingOptions(...);
       });


      // Add the filelayer to allow the uploading of files
      control = L.Control.fileLayerLoad({
          // See http://leafletjs.com/reference.html#geojson-options
          layerOptions: {style: {color:'red'},
          //onEachFeature: function(feature){
          //    featureGroup.addLayer(feature);
          //},
          },
          // Add to map after loading (default: true) ?
          addToMap: false,
          // File size limit in kb (default: 1024) ?
          fileSizeLimit: 1024,
          // Restrict accepted file formats (default: .geojson, .kml, and .gpx) ?
          formats: [
              '.geojson',
              '.kml',
              '.gpx'
          ],
      });
      control.addTo(map);

      // Every time a file is put on we need to wipe the previous layers
      control.loader.on('data:loading', function (e) {
        // Iterate over the layers
        map.eachLayer(function(layer) {
          // Check to make sure that we're not getting rid of the base map
          if(layer._latlngs) {
            console.log(layer);
            map.removeLayer(layer);
          }
        });
      });

      // It also needs to get added to the featuregroup

      control.loader.on('data:loaded', function (e) {
        // Get the geojson layer
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

        removedLayers = []
        //console.log('glayer VV');
        //console.log(gLayer);
        console.log(map);
        map.eachLayer(function(layer) {
            //$.isFunction($.fn.lettering)
            //console.log(typeof(layer));
            if(layer._layers) {
                layer.clearLayers();
                //layer.addLayer(gLayer);
                //console.log('yes layers VV')
            }
            else {
                //console.log('no layers VV')
            }
            //console.log(layer);
          // 29 seems to be the featuregroup which Leaflet.Draw uses with geodjango. Let's hope it never changes.
          // if(layer._leaflet_id == 28) {
          // if(layer.getLayers().length > 0) { todo find some other way of doing this jesus christ fuck
            //layer.clearLayers();
            //layer.removeLayer(56);
            //layer.addLayer(gLayer);
          //}
          /*else if(layer._latlngs) {
            map.removeLayer(layer);
          }*/
        });

        featureGroup.addLayer(gLayer); todo note this
        //map.addLayer(gLayer);

        //console.log(e);
        console.log('loaded');
        //console.log(gLayer);
        //map.addLayer(reallayer);
        /*var featureGroup = L.featureGroup().addTo(map);
        //gl = e.layer.geometryToLayer();
        //console.log(gl);
        reallayer = e.layer.getLayers()[0];
        featureGroup.addLayer(reallayer);
        console.log(reallayer);*/
        /*map.eachLayer(function(layer) {
          if(layer._latlngs)
          featureGroup.addLayer(e.layer);
        });*/
        //featureGroup.addLayer(e.layer[0]);

        //featureGroup.addTo(map);
      });


      // Every time someone draws something we need to wipe the previous layers
        map.on('draw:created', function (e) {

          //console.log(e.layer);
          // Iterate over the layers
          map.eachLayer(function(layer) {
            //console.log(layer);
            // Check to make sure that we're not getting rid of the base map
            if(layer._latlngs) {
              map.removeLayer(layer);
            }
          });

          // Do whatever else you need to. (save to db, add to map etc)
          //map.addLayer(e.layer);
          //featureGroup.addLayer(e.layer);
      });


      $('form').submit(function(event) {
        console.log($('form'));
        console.log($('form').serialize());
        event.preventDefault();
      })
    });
})