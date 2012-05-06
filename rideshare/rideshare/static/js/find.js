$(function() {
    var d = new Date()
    var date = (d.getMonth() + 1) + "/" + d.getDay() + "/" + d.getFullYear()

    $("#dpicker").val(date)
    $("#dpicker").datepicker()

    $("#time").val("12:00")
});
