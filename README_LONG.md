# xwnode (long README)

Graph engine for the eXonware stack: large families of node strategies, edge representations, and query languages, with WAL, Bloom filters, and atomic compare-and-swap where implemented. Scale targets span small in-memory graphs through very large on-disk layouts.

Short overview: [README.md](README.md).

---

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com

---

## Vision

Pick node strategy, edge strategy (or none), and optional cache behavior from one API. xwnode is meant to sit under data, processing, and orchestration layers across Exonware packages (and later frontends) without forcing a single internal representation.

---

## What you get

- Many **node** and **edge** strategies behind shared facades
- **Query** integration (xwquery) for SQL-like and graph-native text
- **Durability helpers** - WAL, Bloom filters, atomic CAS where applicable
- **AUTO** selection when you do not want to pin a structure up front
- **Stack usage** - xwdata, xwentity, xwschema, xwaction integrate with xwnode types

---

## Installation

See [README.md](README.md) for the Lite / Lazy / Full table.

```bash
pip install exonware-xwnode
pip install exonware-xwnode[lazy]   # optional
pip install exonware-xwnode[full]   # optional
```

---

## Quick start (API sketch)

| Task | Code |
|------|------|
| Create from native data | `node = XWNode.from_native(data)` or `XWNode(mode=NodeMode.X)` |
| Put / get / delete | `node.put(key, value)`, `value = node.get(key)`, `node.delete(key)` |
| Choose strategy | `XWNode(mode=NodeMode.X)` or presets (`fast`, `optimized`, `adaptive`, `dual_adaptive`) |
| List presets | `XWNode.create_with_preset(...)`, `list_available_presets()` |

```python
from exonware.xwnode import XWNode
node = XWNode.from_native({"a": 1, "b": 2})
node.put("c", 3)
print(node.get("a"))  # 1
```

---

## Main entry points

- **Facade:** `XWNode`, `XWEdge`, `XWFactory`
- **Presets:** `create_with_preset`, `list_available_presets`
- **Modes:** `NodeMode`, `EdgeMode`, `NodeTrait`, `EdgeTrait`, `GraphOptimization`
- **Operations:** `merge_nodes`, `diff_nodes`, `patch_nodes`; `XWGraphManager`
- **Config:** `get_config` / `set_config`, `XWNodeConfig`

---

## Easy vs advanced

| Short path | Deeper control |
|------------|----------------|
| `from_native`, `put` / `get` / `delete`, `mode=NodeMode.X` | Strategy options, immutability / COW, `path_cache_size`, merger / differ / patcher types, graph optimization, `XWGraphManager`, config objects |

---

## Documentation

- [docs/INDEX.md](docs/INDEX.md) - index
- [REF_22_PROJECT.md](docs/REF_22_PROJECT.md) - status
- [REF_14_DX.md](docs/REF_14_DX.md) - developer experience
- [REF_15_API.md](docs/REF_15_API.md) - API
- [REF_13_ARCH.md](docs/REF_13_ARCH.md) - architecture
- [REF_54_BENCH.md](docs/REF_54_BENCH.md) - benchmarks when published
- [GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md) - usage guide

---

## License

MIT - see [LICENSE](LICENSE).

---

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com
