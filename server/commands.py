import json 
import select

safeties = {} 

def unhandle(server):
    global safeties

    # Unregister... everything. Nuke it from orbit. It's the only way to be 
    # sure.
    for key in safeties.keys():
        server.input_proxy.unregister(key)

    safeties = {}

def handle(server, com):
    # TODO: Proper error handling. Ha!
    if com.has_key("safety"):
        __register_safety(server, com["name"], com["safety"])

def __safety(server, name, key):
    """Make a call to the client, asking it to tell us whether or not we should
    allow this keypress through to the game."""

    message = {"safety": name, "key": key}
    server.client.send(json.dumps(message) + "\r\n")

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

def __register_safety(server, name, key):
    if not safeties.has_key(key):
        safeties[key] = []
        server.input_proxy.register(key, __safety_wrapper)

    safeties[key].append({"name": name, "server": server})
