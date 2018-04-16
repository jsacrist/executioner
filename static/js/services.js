/*
 * Given the status of a service, return the corresponding class of its toggle button
 */
function getServiceToggleClass(serviceStatus){
    if ( serviceStatus == "0" ) {
        return "divService toggle-button toggle-button-selected";
    } else {
        return "divService toggle-button";
    }
}

/*
 * Given the status of a service, return the endpoint URL
 */
function toggleToTargetUrl(serviceToggle){
    if ( serviceToggle == getServiceToggleClass(0) ) {
        return "/srv_stop/";
    } else {
        return "/srv_start/";
    }
}

/*
 * Given the numerical status of a service, update a toggle button and a restart button
 */
function updateToggleNRestartBtns(serviceStatus, toggleDiv, restartButton){
    if ( serviceStatus == "0" ) {  
        toggleDiv.setAttribute("class", "divService toggle-button toggle-button-selected");
        restartButton.setAttribute("class", "restartButton");
        restartButton.disabled = false;
        restartButton.innerHTML = "&#9850;"
    } else {
        toggleDiv.setAttribute("class", "divService toggle-button");
        restartButton.setAttribute("class", "restartButton restartButton-disabled");
        restartButton.disabled = true;
        restartButton.innerHTML = ""
    }
}

/*
 * Display an alert message only for a period of time.
 */
/*
function tempAlert(msg, duration, bgColor){
    var myElem = document.createElement("div");
    myElem.setAttribute("style", "position:absolute;" +
                                 "top:200px; left:100px;" +
                                 "border:2px solid #7DA652;" +
                                 "background-color:" + bgColor + ";" +
                                 "font-size:55px");
    myElem.innerHTML = msg;
    setTimeout(function(){
        myElem.parentNode.removeChild(myElem);
    }, duration);
    document.body.appendChild(myElem);
}
*/

/* 
 *  Toggle button actions (Turn ON/OFF)
 */
$(function() {
    $(".serviceButton").click(function() {
        console.info("toggle button pressed")
        var selectedService = $(this).attr("value");
        var myDiv = document.getElementById("div-" + selectedService);
        var targetUrl = toggleToTargetUrl(myDiv.getAttribute("class"));

        myDiv.setAttribute("class", "divService toggle-button toggle-button-pressed")

        $.ajax({
            type: "GET",
            url: targetUrl,
            contentType: "application/json; charset=utf-8",
            data: { "service_name": selectedService },
            success: function(data) {
                $.each(data, function(my_key, my_value) {
                    console.info("Setting [" + my_key + "] to: " + my_value);
                    var responseDivToggle = document.getElementById("div-" + my_key);
                    var responseBtnReset = document.getElementById("rBtn-" + my_key);
                    updateToggleNRestartBtns(my_value, responseDivToggle, responseBtnReset);
                });
            }
        });
    });
});

/* 
 *  Restart button actions (Turn OFF, then turn ON)
 */
$(function() {
    $(".restartButton").click(function() {
        console.info("Reset button pressed")
        var selectedService = $(this).attr("value");
        var pressedBtnReset = document.getElementById("rBtn-" + selectedService);
        pressedBtnReset.setAttribute("class", "restartButton restartButton-pressed");
        
        $.ajax({
            type: "GET",
            url: "/srv_restart/",
            contentType: "application/json; charset=utf-8",
            data: { "service_name": selectedService },
            success: function(data) {
                $.each(data, function(my_key, my_value) {
                    console.info("Setting [" + my_key + "] to: " + my_value);
                    var responseDivToggle = document.getElementById("div-" + my_key);
                    var responseBtnReset = document.getElementById("rBtn-" + my_key);
                    updateToggleNRestartBtns(my_value, responseDivToggle, responseBtnReset);
//                    console.info(responseBtnReset);
                });  
            }
        });
    });
});

