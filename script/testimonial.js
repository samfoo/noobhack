$(document).ready(function() {
    var $testimonials = $('.endorsement');
    $testimonials.sort(function() {return 0.5 - Math.random()});
    $testimonials.filter(':first').show();

    setInterval(function() {
        var $next = $testimonials.filter(':visible').hide().next('.endorsement');
        if ($next.length === 0) $next = $testimonials.filter(':first');
        $next.show();
    }, 7500);
});
