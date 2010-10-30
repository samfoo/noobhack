import json 
import select

callbacks = {}
safeties = {} 

class ClientReady(Exception):
    pass

def unhandle(server):
    global callbacks, safeties

    # Unregister... everything. Nuke it from orbit. It's the only way to be 
    # sure.
    for pattern in callbacks.keys():
        server.output_proxy.unregister(pattern)

    for key in safeties.keys():
        server.input_proxy.unregister(key)

    callbacks = {}
    safeties = {}

def handle(server, com):
    # TODO: Proper error handling. Ha!
    if com.has_key("pattern"):
        __register_callback(server, com["name"], com["pattern"])
    elif com.has_key("safety"):
        __register_safety(server, com["name"], com["safety"])
    elif com.has_key("ready"):
        raise ClientReady() 

def __callback(server, name, data):
    """Make a call to the client telling it to execute some callback."""

    callback = {"callback": name, "data": data}
    server.client.send(json.dumps(callback) + "\r\n")

def __safety(server, name, key):
    """Make a call to the client, asking it to tell us whether or not we should
    allow this keypress through to the game."""

    callback = {"safety": name, "key": key}
    server.client.send(json.dumps(callback) + "\r\n")

    # Safeties are special. After calling back to the client we MUST wait for a
    # response and parse it to determine whether to continue. Now is as good a
    # time as any to do that.
    response = server._read()

    for command in response[:]:
        if command["safety"] == name and command["status"] == "ok":
            response.remove(command)
            return True
        elif command["safety"] == name:
            response.remove(command)
            return False

    # Process the rest of the things on the queue? This really is a
    # pretty ghetto way of doing things. Stateful server programming sucks.
    server._execute(response)

    # If we get this far, something is probably pretty wrong with the client...
    # We asked them if it's alright to continue and they haven't responded for
    # some reason. We're just going to assume it's not okay to continue.
    return False

def __safety_wrapper(key):
    """A wrapper passed to the input proxy that translates an input filter 
    callback to the client callback"""

    if safeties.has_key(key):
        for safety in safeties[key]:
            success = __safety(safety["server"],
                               safety["name"],
                               key)
            if success == False:
                return False
    return True

def __callback_wrapper(pattern, data): 
    """A wrapper passed to the output proxy that translates a callback to a 
    client that registered it."""

    if callbacks.has_key(pattern):
        for registration in callbacks[pattern]:
            __callback(registration["server"], 
                       registration["name"], 
                       data)

def __register_callback(server, name, pattern):
    if not callbacks.has_key(pattern):
        # If we haven't seen this pattern before, register it with out output 
        # proxy and initialize it in our callback table.
        callbacks[pattern] = []
        server.output_proxy.register(pattern, __callback_wrapper)

    callbacks[pattern].append({"name": name, "server": server})

def __register_safety(server, name, key):
    if not safeties.has_key(key):
        safeties[key] = []
        server.input_proxy.register(key, __safety_wrapper)

    safeties[key].append({"name": name, "server": server})
