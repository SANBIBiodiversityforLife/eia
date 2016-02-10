$(document).ready(function() {
   headers =
/*
    // Set up the datetimepicker
    $('.datepicker').datetimepicker({step:30});

    // Steps for uploading
    $(".fadein").each(function(index) { $(this).delay(920*index).fadeIn(600); });

    // Add the help text for the validator (see below)
    $('.form-group').append('<div class="help-block with-errors"></div>');

    // Form validation http://1000hz.github.io/bootstrap-validator/
    // https://www.linkedin.com/pulse/bootstrap-validator-how-create-custom-validation-omri-marcovtich
    $('input#id_collected_to').attr('data-futuredate', 'futuredate');
    var options = {
        custom: {
            'futuredate':
                function($el) {
                    return $('input#id_collected_to').val() > $('input#id_collected_from').val();
                }
        },
        errors: {
            'futuredate': "You must select a date later than the previously-input date."
        }
    }
    $('#upload-form').validator(options);
    $('#upload-form').on('submit', function (e) {
      if (e.isDefaultPrevented()) {
        // Handle the invalid form...
        console.log('form errors');
      } else {
        // Everything looks good!
        $('#uploadModal').modal('show');
      }
    })

    // Make the remainder of the form appear once the spreadsheet has been selected
    $("input#id_upload_data").change(function (){
        // add some validation var fileName = $(this).val();
        $('#formRemainder').show('slow');
    });

    // Hide the success/failure messages in the modal window, only show it when everything is ok
    $('#modalMessageSuccess').hide();
    $('#modalMessageFailure').hide();
    $('#modalMessageServerFailure').hide();

    // Ajax the form
    var options = {
        dataType: 'json',
        success: function(data) {
            // Change the header
            $('h4#myModalLabel').html('Data successfully uploaded');

            // Make the message appear to fade in
            $('#modalMessage').hide();

            // If there's any spreadsheet errors then show them, otherwise redirect to project page
            if(data['error_sheet'] != 0) {
                $('#spreadsheet-errors').attr('href', data['error_sheet']);
                $('#modalMessageFailure').fadeIn();
            } else {
                $('#modalMessageSuccess').fadeIn();
            }
        },
        error: function(jqXHR, textStatus, errorThrown){
            // Make the message appear to fade in
            $('#modalMessage').hide();
            $('#serverErrorMessage').text(errorThrown);
            $('#modalMessageServerFailure').fadeIn();
        }
    }
    $('#upload-form').ajaxForm(options);*/
})