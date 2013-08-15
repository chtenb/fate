"""Import plugins"""
from importlib import import_module
import logging


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


def merge_orderings(a, b):
    """Merge two lists while preserving the original ordering"""
    duplicates = [x for x in a if x in b]
    a_split = split(a, duplicates)
    b_split = split(b, duplicates)
    zipped = [x + y for x, y in zip(a_split, b_split)]
    return join(zipped, duplicates)


def merge(ordered_lists):
    """Merge a list of lists while preserving the original ordering"""
    if not ordered_lists:
        return []
    x = ordered_lists[0]
    for y in ordered_lists[1:]:
        x = merge_orderings(x, y)
    return x


def solve_plugin_dependencies(plugin, parents = []):
    """Recursively import dependencies of plugin, and return correct execution order"""
    children = []
    for child_name in plugin.__dependencies__:
        try:
            child = import_module("." + child_name, "protexted")
        except ImportError:
            logging.critical("Unresolved dependency: plugin '" + child_name + "' can not be found")
        else:
            if child in parents:
                logging.critical("Cycle detected in dependency tree of plugin '" + child_name + "'")
            else:
                children.append(child)

    return merge([solve_plugin_dependencies(child, parents + [plugin]) for child in children]) + [plugin]

# Import user plugin
from . import user

# Execute recursive dependencies of user plugin in the right order
for plugin in solve_plugin_dependencies(user):
    try:
        plugin.main()
    except Exception as e:
        logging.error(e, exc_info=True)
