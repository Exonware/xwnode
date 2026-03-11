# xwnode (long version)

**Graph-based data engine for the eXonware ecosystem.** 60+ node strategies, 30+ edge/graph representations, 35+ query languages; WAL, Bloom filters, atomic CAS; scale from KB to TB.

*This is the long version (full features, DX, architecture). Short overview: [README.md](README.md).*

---

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com

---

## Vision

Create data structures easily by selecting configurations (node strategy, edge strategy—edge can be none), plus caching; high performance; used everywhere (data, processing, logic; future TypeScript/frontend). xwnode is the **graph-based data engine** for the eXonware ecosystem.

---

## What you get

- **60+ node strategies,** 30+ edge/graph representations
- **35+ query languages** in a single API (XWQuery support)
- **WAL, Bloom filters, atomic CAS,** async-first
- **Unified graph API:** One interface for multiple backends and representations (adjacency list, matrix, compressed, etc.); AUTO mode
- **Production features:** Lock-free, scale from KB to TB
- **Integration:** xwdata, xwentity, xwschema, xwaction use xwnode

---

## Installation

See [README.md](README.md) for Lite/Lazy/Full install table.

```bash
pip install exonware-xwnode
pip install exonware-xwnode[lazy]   # optional
pip install exonware-xwnode[full]   # optional
```

---

## Quick start (key code)

| Task | Code |
|------|------|
| Create from native data | `node = XWNode.from_native(data)` or `XWNode(mode=NodeMode.X)` |
| Put / get / delete | `node.put(key, value)`, `value = node.get(key)`, `node.delete(key)` |
| Choose strategy | `XWNode(mode=NodeMode.X)` or use presets (fast, optimized, adaptive, dual_adaptive) |
| List presets | `XWNode.create_with_preset(...)`, `list_available_presets()` |

### Example

```python
from exonware.xwnode import XWNode
node = XWNode.from_native({"a": 1, "b": 2})
node.put("c", 3)
print(node.get("a"))  # 1
```

---

## Main entry points

- **Facade:** XWNode, XWEdge, XWFactory
- **Presets:** create_with_preset, list_available_presets; fast, optimized, adaptive, dual_adaptive
- **Modes:** NodeMode, EdgeMode, NodeTrait, EdgeTrait, GraphOptimization
- **Operations:** merge_nodes, diff_nodes, patch_nodes; XWGraphManager
- **Config:** get_config/set_config, XWNodeConfig

---

## Easy vs advanced

| Easy (1–3 lines) | Advanced |
|------------------|----------|
| from_native(data), put/get/delete, mode=NodeMode.X | Strategy options, immutable/COW, path_cache_size, NodeMerger/NodeDiffer/NodePatcher, graph optimization, XWGraphManager, merge_nodes/diff_nodes/patch_nodes, get_config/set_config, XWNodeConfig. |

---

## Documentation

- [docs/INDEX.md](docs/INDEX.md) — Documentation index
- [REF_22_PROJECT.md](docs/REF_22_PROJECT.md) — Project status and vision
- [REF_14_DX.md](docs/REF_14_DX.md) — Developer experience and key code
- [REF_15_API.md](docs/REF_15_API.md) — API reference
- [REF_13_ARCH.md](docs/REF_13_ARCH.md) — Architecture
- [REF_54_BENCH.md](docs/REF_54_BENCH.md) — Benchmarks (when present)
- [GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md) — Usage guide

---

## Innovation

**Tier 1 — Genuinely novel.** Graph-based data engine with 60+ node strategies, 30+ edge representations, 35+ query languages, WAL, Bloom filters, atomic CAS—single API. Part of the eXonware story — vertical integration across 20+ packages.

---

## License

MIT — see [LICENSE](LICENSE).

---

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com
