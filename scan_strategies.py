import importlib, pkgutil, inspect
import exonware.xwnode.nodes.strategies as ns

failures = []
for importer, modname, ispkg in pkgutil.walk_packages(ns.__path__, ns.__name__ + "."):
    try:
        mod = importlib.import_module(modname)
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if hasattr(obj, "__abstractmethods__") and obj.__abstractmethods__ and not name.startswith("A") and "Strategy" in name:
                failures.append((name, modname.split(".")[-1], sorted(obj.__abstractmethods__)))
    except Exception as e:
        pass

for name, mod, methods in sorted(failures):
    print(f"{name} ({mod}): {methods}")
print(f"\nTotal: {len(failures)} incomplete strategies")
