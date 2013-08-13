"""Import all plugins"""
# Needs refactoring
from importlib import import_module
import logging

from IPython import embed

def split(l, separators):
    result = []
    prev = 0
    for i, item in enumerate(l):
        if item in separators:
            result.append(l[prev:i])
            prev = i + 1
    result.append(l[prev:])
    return result

def join(l, separators):
    result = []
    for i, item in enumerate(l[0:-1]):
        result.extend(item)
        result.append(separators[i])
    result.extend(l[-1])
    return result

def merge_ordering(a, b):
    duplicates = [x for x in a if x in b]
    a_split = split(a, duplicates)
    b_split = split(b, duplicates)
    zipped = [x + y for x,y in zip(a_split, b_split)]
    return join(zipped, duplicates)

def merge_list_of_orderings(l):
    if not l:
        return []
    x = l[0]
    for y in l[1:]:
        x = merge_ordering(x,y)
    return x

def solve_plugin_dependencies(plugin):
    return merge_list_of_orderings([solve_plugin_dependencies(plugins[name]) for name in plugin.__dependencies__]) + [plugin]

plugin_names = ['select_system', 'filetype_system']
plugins = {}
for name in plugin_names:
    plugins[name] = import_module("." + name, "protexted")

plugin_order = merge_list_of_orderings([solve_plugin_dependencies(plugin) for plugin in plugins.values()])
for plugin in plugin_order:
    try:
        plugin.main()
    except Exception as e:
        logging.error(e, exc_info=True)
