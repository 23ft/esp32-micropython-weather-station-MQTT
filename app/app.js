import { connectMQTT, client, messagePublish, statusClient } from "./modules/mqtt.js";
import { btn_connect, view_hum, view_temp, cloud_status, content } from "./elements.js";

var eventAppStatusID, smsPayload, smsTopic, concl;

const sms = (smsObj) => {
    smsTopic = smsObj.destinationName;
    smsPayload = smsObj.payloadString;

    if (smsTopic == "stationESP32/data") {
        view_temp.innerHTML = "" + smsPayload;
    }
}

function statusApp() {
    if (statusClient) {
        console.log("Connected with: " + client);
        cloud_status.style.color = "#e4cd00";
        clearInterval(eventAppStatusID);
    }
}

btn_connect.addEventListener("click", () => {

    if (concl) {
        // btn_connect.style.color = "#333"
        // btn_connect.style.border = "none"

        content.style.display = "none";
        concl = false;

    } else {
        // btn_connect.style.color = "#ccc"
        // btn_connect.style.border = "2px inset #ccc"
        // btn_connect.style.borderRadius = "10px"

        concl = true;
        eventAppStatusID = "";
        content.style.display = "flex";

        connectMQTT(sms);
        eventAppStatusID = setInterval(statusApp, 1000);
    }
})