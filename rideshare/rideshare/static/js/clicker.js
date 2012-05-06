$(function() {
    $(".row").each(function(idx, div) {
        $(div).click(function(div) {
            var $div = $(this);
            $show = $div.find(".toggle")
            $show.toggle();
        });
    });
});
