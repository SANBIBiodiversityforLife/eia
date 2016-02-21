$(document).ready(function() {
    fixExampleWidths = function(widths) {
        // Sort out the examples
        $('.hot-example td').each(function(index, obj) {
          $(obj).css('width', widths[index]);
        });
        hotWidth = $('#hot').width();
        hotBlankCellWidth = $('.ht_clone_top_left_corner table.htCore').width();
        $('.hot-example').css('width', hotWidth-hotBlankCellWidth);
        $('.hot-example').css('margin-left', hotBlankCellWidth);
        $('.hot-example').hide();
        $('#showExamples').click(function() {
          $('#showExamples').hide('fast');
          $('.hot-example').show('fast');
        });
    }
});