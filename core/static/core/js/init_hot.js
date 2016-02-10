function init_hot() {
    // Initialise handsontable
    var ht = new Handsontable(document.getElementById('hot'), hotOptions);

    // There is a fake submit button rathern than a real one, as we need to validate the hotInstance
    $('#submitData').click(function() {
      // Get the data in the cells
      var htData = ht.getData();

      // If the last row is empty, remove it before validation
      if(htData.length > 1 && ht.isEmptyRow(htData.length - 1)) {
        // We don't want HOT to automatically add rows as it screws the validation
        // ht.updateSettings({minSpareRows: 0});

        // Remove the last row if it's empty
        ht.alter('remove_row', parseInt(htData.length - 1), keepEmptyRows = false);
      }

      // Validate the cells and submit the form via ajax
      ht.validateCells(function(result, obj) {
        if(result == true) {
          // JSON our data up
          json_data = JSON.stringify(htData);

          // Ajax options for the jquery ajax form
          var options = {
            dataType: 'json',
            data: { 'hot_data': json_data },
            success: function(data) {
                // Change the header
                $('h4#myModalLabel').html(data['objects_saved'] + ' rows successfully saved');

                // Add metadata id to the redirect link
                var _href = $("a#redirectURL").attr("href");
                $("a#redirectURL").attr("href", _href + data['metadata_pk'] + '#documentation');

                // Make the message appear to fade in
                $('#modalMessage').hide();

                // Provide redirect to project page
                $('#modalMessageSuccess').fadeIn();
            },
            error: function(jqXHR, textStatus, errorThrown){
                // Make the message appear to fade in
                $('#modalMessage').hide();
                $('#serverErrorMessage').text(textStatus);
                $('#modalMessageServerFailure').fadeIn();
            }
          };
          $('form.data-upload-form').ajaxForm(options);

          // Show our modal
          $('#uploadModal').modal({backdrop: 'static', keyboard: false, show: true});

          // Ajax submit the form
          $('form.data-upload-form').submit();

          console.log('submitted');
        }
        else {
          // ht.updateSettings({minSpareRows: 1}); - this doesn't seem to work, change to minsparerows on init rather
        }
      });
    })
}