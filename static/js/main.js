var FETCH_INTERVAL = 3000,
    REVIEW_SPAN = 5;

$(function(){
    $('.noUiSlider').noUiSlider({
        range: [0, 100],
        start: 50,
        step: 1,
        handles: 1
    }).change(function() {
        var game = $(this).closest('.game');
        $.getJSON('review/' + game.attr('id'),
            { 'timespan': REVIEW_SPAN, 'rating': Math.floor($(this).val()) },
            function(data) {
                game.find('.game-rating-content').html('<strong class="text-success">Thanks!</strong>');
            }
        );
    });

    $('.game').mouseover(function() {
        $(this).find('.game-rating').addClass('hidden');
        $(this).find('.game-slider').removeClass('hidden');
    });

    $('.game').mouseout(function() {
        $(this).find('.game-rating').removeClass('hidden');
        $(this).find('.game-slider').addClass('hidden');
    });

    setInterval(function update_metrics() { // Careful, evil hack here.
        $('.game').each(function(i, elem) {
            var rating = $(elem).find('.game-rating-content');
            if (rating.hasClass('hidden'))
                return;

            var gameid = $(elem).attr('id');
            $.getJSON('ratings/' + gameid, function(data) {
                rating.html(data.avg);
                rating.css('font-size', (75 + 50 * data.avg / 100.0) + '%');
                rating.css('border-width', (data.avg / 100.0) * 3);
            });
        });

        return update_metrics;
    }(), FETCH_INTERVAL);
});
