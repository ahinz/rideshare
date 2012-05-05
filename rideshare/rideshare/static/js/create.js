$(function() {
    var d = new Date()
    var date = (d.getMonth() + 1) + "/" + d.getDay() + "/" + d.getFullYear()

    $("#dpicker").datepicker()
    $("#dpicker").val(date)

    $("#time").val("12:00")
});
