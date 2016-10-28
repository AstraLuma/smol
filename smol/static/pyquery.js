(function() {
    var connection = new WebSocket('ws://'+document.location.host+'/pyq');

    // FIXME: Handle disconnects (mostly theoretical)
    connection.onopen = function () {
        connection.send(JSON.stringify({'type': 'load'}));
    };

    connection.onerror = function (error) {
        console.log('WebSocket Error ' + error);
    };

    function getJQ(query) {
        if (query == '$document') {
            return $(document);
        } else if (query == '$window') {
            return $(window);
        } else {
            return $(query);
        }
    }

    function obj2json(obj) {
        // FIXME: Map Element, etc to JSONable types
        //return obj;
        return null;
    }

    function args2obj(args) {
        // TODO: Find /\$callback:(.*)\$/ in args (recursively) and replace with trampoline function
        return args;
    }

    connection.onmessage = function (e) {
        console.log('Server: ' + e.data);
        var body = JSON.parse(e.data);
        if (body.type == 'call') {
            var jq = getJQ(body.query);

            console.log("Results: " + jq.length + " " + jq);

            var meth = jq[body.method];
            if (meth == undefined) {
                connection.send(JSON.stringify({
                    'type': 'error', 
                    'code': 'missing-method', 
                    'msg': 'Method '+body.method+' does not exist.'
                }));
                return;
            }
            var args = body.args;
            try {
                var rv = meth.apply(jq, args2obj(args));
            } catch(e) {
                connection.send(JSON.stringify({
                    'type': 'error',
                    'code': 'calling-exception',
                    'name': e.name,
                    'msg': e.message
                }));
                return;
            }
            console.log(rv);
            connection.send(JSON.stringify({
                'type': 'return',
                'value': obj2json(rv)
            }));
            return;
        } else if (body.type == 'list') {
            var jq = getJQ(body.query);
            connection.send(JSON.stringify({
                'type': 'results',
                'list': obj2json(jq)
            }));

        } else {
            connection.send(JSON.stringify({
                'type': 'error', 
                'code': 'unknown-message', 
                'msg': 'Message type '+body.type+' not recognized.'
            }));
            return;
        }
    };
})();
