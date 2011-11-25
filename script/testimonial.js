$(document).ready(function() {
    $("div.endorsement").hide();

    var i = 0;
    var testimonials = $("div.endorsement");
    var current = $(testimonials.get(0));
    current.show();

    function show_random_testimonial() {
        i += 1;
        current.slideDown();
        current = $(testimonials.get(i % testimonials.length));
        current.slideUp();
    }

    setInterval(show_random_testimonial, 3000)
});
