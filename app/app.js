import { connectMQTT, client, messagePublish, statusClient, closeConnection } from "./modules/mqtt.js";
import { btn_connect, view_hum, view_temp, cloud_status, content, foot } from "./elements.js";

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
        alert("You are already connect for recived information!");
    }
}

btn_connect.addEventListener("click", () => {

    if (concl) {
        clearInterval(eventAppStatusID);
        content.style.display = "none";
        concl = false;
        if (closeConnection()) {
            console.log("Cerrando conexion")
            cloud_status.style.color = "#555"

            smsPayload = '';
            smsTopic = '';

            view_temp.innerHTML = '';
            view_hum.innerHTML = '';
            alert("You are disconnect from broker!");



        }

    } else {
        concl = true;
        eventAppStatusID = "";
        content.style.display = "flex";


        connectMQTT(sms);
        btn_connect.style.disable = "true"
        eventAppStatusID = setInterval(statusApp, 1000);
    }
})