import json 

callbacks = {}

def handle(srvr, conn, com):
    # TODO: Proper error handling
    if com.has_key("register"):
        register(srvr, conn, com["register"], com["pattern"])

def __callback(conn, name, pattern, data):
    callback = {"callback": name, "data": data}
    conn.send(json.dumps(callback) + "\r\n")

def __callback_wrapper(pattern, data): 
    if callbacks.has_key(pattern):
        for registration in callbacks[pattern]:
            __callback(registration["connection"], 
                       registration["name"], 
                       pattern, 
                       data)

def register(server, conn, name, pattern):
    if not callbacks.has_key(pattern):
        callbacks[pattern] = []
        server.output_proxy.register(pattern, __callback_wrapper)

    callbacks[pattern].append({"name": name, "connection": conn})
