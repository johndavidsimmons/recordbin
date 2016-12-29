var check;

function getNewRecords() {
    $.ajax({
        url: "/" + username + "/follower_records",
        dataType: "json",
        type: "GET",

        success: function(data) {
            for (var key in data) {
                var html_string = "<li id=" + data[key]["id"] + "><img src=" + data[key]['gravatar'] + " class='gravatar'>" + data[key]['user'] + " added " + data[key]['artist'] + " - " + data[key]['title'] + " - " + moment(data[key]["timestamp"]).fromNow() + "</li>";
                $("#follower_records").append(html_string)
            }
        }
    });
}

getNewRecords()