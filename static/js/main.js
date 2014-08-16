var FETCH_INTERVAL = 3000,
    REVIEW_SPAN = 5,
    THRESHOLDS = {
        'boring': 25,
        'exciting': 75
    };

$(function(){
    $('.noUiSlider').noUiSlider({
        'range': [0, 100],
        'start': 50,
        'step': 1,
        'handles': 1,
        'connect': 'lower'
    }).change(function() {
        var game = $(this).closest('.game');
        $.getJSON('/review/' + game.attr('id'),
            { 'timespan': REVIEW_SPAN, 'rating': Math.floor($(this).val()) },
            function(data) {
                update_metrics();
            }
        );
    });

    $('.game-rating-and-slider').popover({ 'trigger': 'hover focus' });

    $('.game').mouseover(function() {
        $(this).find('.game-rating').addClass('hidden');
        $(this).find('.game-slider').removeClass('hidden');
    });

    $('.game').mouseout(function() {
        $(this).find('.game-rating').removeClass('hidden');
        $(this).find('.game-slider').addClass('hidden');
    });

    setInterval(function update_metrics() {
        $('.game').each(function(i, elem) {
            var rating = $(elem).find('.game-rating-content');
            if (rating.hasClass('hidden'))
                return;

            var gameid = $(elem).attr('id');
            $.getJSON('/ratings/' + gameid, function(data) {
                if (!(data.avg))
                    return;
                rating.html(data.avg);
                rating.css('font-size', (100 + 50 * data.avg / 100.0) + '%');
                rating.removeClass('label-default label-warning label-success label-danger');
                if (data.avg < THRESHOLDS.boring)
                    rating.addClass('label-danger');
                else if (data.avg > THRESHOLDS.exciting)
                    rating.addClass('label-success');
                else
                    rating.addClass('label-default');
            });
        });

        return update_metrics;
    }(), FETCH_INTERVAL);
});
