import { makeid } from './rand.js';

export var client, infod, key_user, clientId;

var host = "35.199.113.247";
var port = 8083;
var topicSub = ["fDWsZDAVg7/JS_Response", "fDWsZDAVg7/ESP32_RGB/response"];

// Callback for failure connection with broker MQTT.
const failureConnection = () => {
    alert("Error try connect to broker [" + host + "]");
}

// Connection finish, client is disconnect from broker.
export const closeConnection = () => {
    client.disconnect();

    return true;
}

// Callback for succesconect to broker, exec when the client already connect.
export const succesConnect = () => {
    console.log("Conexion establecida con server MQTT: " + host + ":" + `${port}`);

    // Subscribiendo cliente a los topics.
    for (let t of topicSub) {
        client.subscribe(t);
        console.log("sub to: " + t);
    }
}

// CallBack for new message arrived.
export const messageNew = (messageObject) => {

    console.log(messageObject.destinationName + ":" + messageObject.payloadString);

}

// Callback for connection lost.
export const connectLost = (responseObject) => {
    if (responseObject.errorCode !== 0) {
        console.log("Connection is lost, error log is: " + responseObject.errorMessage);
    }
}

// Function to generate random id from connection to MQTT.
const genId = () => {
    client = "", infod = "", key_user = "", clientId = "";

    infod = new Date().getUTCDate();
    key_user = makeid(6);
    key_user += "_" + infod;
    clientId = "[JS_C_ESP32]_" + key_user;

    return true;
}

// Function to connect to broker MQTT.
export const connectMQTT = () => {
    // creacion Id Usuario.
    if (genId()) {
        console.log("[genId] Id generada con extio");
    }

    // Instanciamos objeto Client.
    client = new Paho.MQTT.Client(host, port, clientId);

    // Asignando Callbacks para cada propiedad evento.
    client.onConnectionLost = connectLost;
    client.onMessageArrived = messageNew;
    client.connect({
        onSuccess: succesConnect,
        keepAliveInterval: 10,
        onFailure: failureConnection
    });

    return client;
}

console.log("Import mqtt.js completed!");