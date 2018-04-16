/*
 *
 */
function update_command_buttons(command_name, command_last_output){
    var responseDivText = document.getElementById("cmdOutput-" + command_name);
    var myClrBtn = document.getElementById("clrCmdBtn-" + command_name);
    responseDivText.innerHTML = "<pre><code>" + command_last_output + "</code></pre>";
    if ( command_last_output == "" ){
        myClrBtn.setAttribute("class", "clearCommandButton clearCommandButton-disabled");
        myClrBtn.disabled = true;
    } else {
        myClrBtn.setAttribute("class", "clearCommandButton");
        myClrBtn.disabled = false;
    }
}

/*
 *
 */
function refresh_command_button(selectedCommand){
    $.ajax({
        type: "GET",
        url: "/cmd_last_output/",
        contentType: "application/json; charset=utf-8",
        data: { "command_name": selectedCommand },
        success: function(data) {
            $.each(data, function(my_key, my_value) {
                update_command_buttons(my_key, my_value);
            });
        }
    });
}

/*
 * #############################################################################
 */

/*
 *
 */
$(function() {
    $(".commandButton").click(function() {
        var selectedCommand = $(this).attr("value");
        var myCmdBtn = document.getElementById("cmdBtn-" + selectedCommand);
        myCmdBtn.setAttribute("class", "commandButton commandButton-running");
        myCmdBtn.disabled = true;
        myCmdBtn.innerHTML = "&#8987;"                  /* Hourglass */
        console.info("commandButton Pressed: [" + selectedCommand + "]")

        $.ajax({
            type: "GET",
            url: "/cmd_exec/",
            contentType: "application/json; charset=utf-8",
            data: { "command_name": selectedCommand },
            success: function(data) {
                $.each(data, function(my_key, my_value) {
                    update_command_buttons(my_key, my_value);
                    myCmdBtn.setAttribute("class", "commandButton");
                    myCmdBtn.disabled = false;
                    myCmdBtn.innerHTML = "&#9654;"      /* Triangle */
                });  
            }
        });
    });
});

/*
 *
 */
$(function() {
    $(".clearCommandButton").click(function() {
        var selectedCommand = $(this).attr("value");
        console.info("clearCommandButton  Pressed: [" + selectedCommand + "]")
        
        $.ajax({
            type: "GET",
            url: "/cmd_clear/",
            contentType: "application/json; charset=utf-8",
            data: { "command_name": selectedCommand },
            success: function(data) {
                $.each(data, function(my_key, my_value) {
                    update_command_buttons(my_key, my_value);
                });  
            }
        });
    });
});

