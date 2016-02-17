$(document).ready(function() {
  // Ajax the flagForRemovalForm
  // Must include the jquery ajax form plugin before this script
  var options = {
      dataType: 'json',
      success: function(data) {
          // Change the header
          $('#flagForRemoval .modal-body').html('Dataset has been flagged for removal with an administrator.');
          $('#flagForRemovalButton').hide();
      }
  }
  $('#flagForRemoval').ajaxForm(options);
});