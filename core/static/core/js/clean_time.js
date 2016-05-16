// Function to clean up time
function cleanTime(value) {
    if(isNaN(value)) { // True if value is not a number
        // First, if you have things formatted like 5 00 or 09:00 or 23h00
        // add a dot in to make 09.00
        regex = /^\s*(\d?\d)(\s+|h|hr|:)?(\d\d)/;
        value = value.replace(regex, '$1.$3');

        // Does it contain am? If so remove
        regex = /\s*[Aa][Mm]\s*/;
        value = value.replace(regex, '');

        // If it contains pm we need to translate 11 -> 23 (add 12), do this after rounding
        regex = /\s*[Pp][Mm]\s*/;
        if(value.match(regex)) {
            value = value.replace(regex, '');
            value = parseInt(value, 10) + 12;
        }
    }

    // Hopefully we've fixed some values above. Now try parse as an integer
    if(!isNaN(value)) {
        // Parse as an integer
        value = parseFloat(value);

        // We need to sort out 0100 0930 types first, where there is no decimal place
        if(value >=100 && value <= 2359) {
            value = value/100;
        }

        // Do any rounding that's necessary
        hours = Math.floor(value)
        minutes = value - hours;
        value = hours + Math.round(minutes/0.6  );

        // Final sanity check, 24+ cannot be returned
        if(value > 23)
            return 23;
    }
    // Otherwise the validator will throw it back and they will have to correct it

    return value;
}
