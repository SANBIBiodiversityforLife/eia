// Introjs tour of map features
function startIntro(){
    var intro = introJs();
    intro.setOptions({
      steps: [
        {
          element: '.leaflet-top',
          intro: "This is the map toolbar.",
          position: 'top'
        },
        {
          element: document.querySelector('.leaflet-control-zoom-in'),
          intro: 'Zoom into the map using this tool.',
          position: 'right'
        },
        {
          element: document.querySelector('a.leaflet-control-filelayer'),
          intro: 'Use this tool to upload a KML or GPX (GPS device) file from your computer. If you only have a SHP file or CSV file, use http://www.mapsdata.co.uk/online-file-converter/ to convert your file to KML.',
          position: 'right'
        },
        {
          element: document.querySelector('.leaflet-draw-toolbar-top'),
          intro: "Use these tools to draw a polygon or a square. When drawing a polygon, remember to click back into the first point that you made on the map.",
          position: 'right'
        },
        {
          element: document.querySelector('.leaflet-draw-edit-edit'),
          intro: 'Edit a polygon you have drawn or uploaded on the map using this tool. Remember to click "Save" when you are done.',
          position: 'right'
        },
        {
          element: document.querySelector('.leaflet-draw-edit-remove'),
          intro: 'Made a mistake and want to start again? Use this tool to delete a polygon on the map. Remember to click "Save" when you are done.',
          position: 'right'
        }
      ]
    });
    intro.start();
}