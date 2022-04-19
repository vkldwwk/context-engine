"""
Loads all flow_components
"""
import pkgutil
import context_engine.commands.components as components

__all__ = [name for _,name, _ in pkgutil.iter_modules(
    components.__path__) if name != "all"]

for name in __all__:
    exec("from ..%s import %s" % (name,name))