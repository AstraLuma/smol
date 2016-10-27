(function() {
    var connection = new WebSocket('ws://'+document.location.host+'/pyq');

    // FIXME: Handle disconnects (mostly theoretical)
    connection.onopen = function () {
        connection.send(JSON.stringify({'type': 'begin'}));
    };

    connection.onerror = function (error) {
        console.log('WebSocket Error ' + error);
    };

    connection.onmessage = function (e) {
        console.log('Server: ' + e.data);
    };
})();
