$(document).ready(function () {

    showGuest(); // default

    $.ajax({
        url: "/user/profile",
        type: "GET",

        success: function (res) {

            if (res && res.status === true && res.user) {
                showUser(res.user);
                $("#accountStatus").text(res.user.name || "User");
            } else {
                showGuest();
            }
        },

        error: function () {
            showGuest();
        }
    });

});

function showUser(user) {
    $("#guestMenu").hide();
    $("#userMenu").show();
    $("#userName").text(user.name);
}

function showGuest() {
    $("#guestMenu").show();
    $("#userMenu").hide();
}