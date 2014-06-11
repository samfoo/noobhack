import os
import imp

from os import path

PLUGINSPATH = [
    "~/.noobhack/plugins",
    path.join(path.abspath(__file__), "../plugins")
]

def load_plugin(plugin_path):
    module = imp.find_module("__init__", [plugin_path])
    return imp.load_module("noobhack." + path.basename(plugin_path), *module)

def load_plugins_for_path(p):
    p = path.expanduser(p)

    try:
        plugin_dirs = [path.join(p, pl)
                       for pl
                       in os.listdir(p)
                       if path.isdir(path.join(p, pl))]

        modules = []
        for plugin_path in plugin_dirs:
            p = load_plugin(plugin_path)
            modules.append(load_plugin(plugin_path))

        return modules
    except OSError:
        return []

def load_plugins():
    return [plugin
            for plugins_for_path
            in PLUGINSPATH
            for plugin
            in load_plugins_for_path(plugins_for_path)]
