$(document).ready(function(){
    // All your normal JS code goes in here
    $(".restaurant.rating").rating('disable');
    $('.ui.search').search({type: 'category'});
    $('.ui.dropdown').dropdown();
    $('.ui.radio.checkbox').checkbox();
    $('#example1').calendar({type: 'date'});
});
