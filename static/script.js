function triggerETL() {
    fetch('/triggermspr')
        .then(response => response.text())
        .then(data => document.getElementById("status").innerText = data)
        .catch(error => document.getElementById("status").innerText = "Erreur : " + error);
}

function triggerMetadata() {
    fetch('/triggermetadata')
        .then(response => response.text())
        .then(data => document.getElementById("status").innerText = data)
        .catch(error => document.getElementById("status").innerText = "Erreur : " + error);
}
