//var http = require('http');
const express = require("express");
const WebSocket = require("ws");
const app = express();
//app.engine('py', require('ejs').renderFile);
app.use('/', express.static(__dirname + '/images'));
app.use('/', express.static(__dirname + '/Sample-Code'));
//app.use('/', express.static(__dirname));


const { appendFile } = require('fs');

app.listen(80, () => {
    console.log("Application listening on port :80")
});

app.get("/", (req, res) => {
    res.sendFile(__dirname + "/index.html")
    //res.render(__dirname + 'index.html');
});

app.get("/source.html", (req, res) => {
    res.sendFile(__dirname + "/source.html")
    //res.render(__dirname + 'index.html');
});

app.get("/projects.html", (req, res) => {
    res.sendFile(__dirname + "/projects.html")
    //res.render(__dirname + 'index.html');
});

app.get("/chat.html", (req, res) => {
    res.sendFile(__dirname + "/chat.html")
    //res.render(__dirname + 'index.html');
});

app.get("/login.html", (req, res) => {
    res.sendFile(__dirname + "/login.html")
    //res.render(__dirname + 'index.html');
});

app.post("/login.html", (req, res) => {
    
    //res.render(__dirname + 'index.html');


    let ws = new WebSocket("ws://localhost:8080");

    ws.onopen = function() {
        console.log("Connected to Server"); 

        if (ws) {
            ws.send("Username: Dave");
            ws.close();
            //showMessage(`ME: ${messageBox.value}`);
        } else {
            console.log("if ws didnt pass");
        }

    };



    ws.onmessage = function ({data}) { 
        //showMessage(`YOU: ${data}`);
    };

    ws.onclose = function() { 
        ws = null;
        console.log('localhost port 8080 websocket closed');
        //alert("Connection closed... refresh to try again!"); 
    };

    res.redirect('/chat.html');
    //res.sendFile(__dirname + "/chat.html");


});