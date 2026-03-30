# xwnode

Graph-shaped data with one API: many node and edge strategies, lots of query languages behind the same surface, and `AUTO` when you want the implementation chosen for you.

Longer write-up: [README_LONG.md](README_LONG.md).

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

| Install | What you get | When to use |
|---------|--------------|-------------|
| `pip install exonware-xwnode` | **Lite** - core only | Smallest install. |
| `pip install exonware-xwnode[lazy]` | **Lazy** - backends pulled in when first used | Local dev. |
| `pip install exonware-xwnode[full]` | **Full** - common strategies pre-installed | CI or production bundles. |

Requires xwsystem. Extras only add dependencies; the import path stays the same.

---

## Quick start

```python
from exonware.xwnode import XWNode

node = XWNode.from_native({
    'users': [{'name': 'Alice', 'age': 30, 'city': 'NYC'}, {'name': 'Bob', 'age': 25, 'city': 'LA'}],
    'products': {'laptop': {'price': 1000}, 'phone': {'price': 500}}
})

print(node['users'][0]['name'].value)   # Alice
results = node.query("SELECT * FROM users WHERE age > 25")
node.add_edge('Alice', 'Bob', {'relationship': 'friend'})
friends = node.neighbors('Alice')
```

Pick a mode explicitly (`NodeMode.HASH_MAP`, `NodeMode.LSM_TREE`, `EdgeMode.COMPRESSED_GRAPH`, `EdgeMode.HNSW`, …) or use `NodeMode.AUTO`. See [REF_14_DX](docs/REF_14_DX.md) and [REF_15_API](docs/REF_15_API.md).

---

## What you get

| Area | Contents |
|------|----------|
| **Node strategies** | Hash maps, ordered structures, LSM-style trees, tries, learned indexes, and more behind one API. |
| **Edge strategies** | Adjacency, compressed graphs, HNSW, R-tree, quadtree, temporal layouts, … |
| **Query** | Many languages (SQL, GraphQL, Cypher, XPath, …) via xwquery. |
| **Operations** | WAL, Bloom filters, lock-free options, automatic strategy selection where enabled. |

Status and roadmap: [REF_22_PROJECT](docs/REF_22_PROJECT.md). Full strategy lists: [REF_15_API](docs/REF_15_API.md), [docs/](docs/).

---

## Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md).
- **Usage:** [docs/GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md).
- **REFs:** [REF_01_REQ](docs/REF_01_REQ.md), [REF_22_PROJECT](docs/REF_22_PROJECT.md), [REF_13_ARCH](docs/REF_13_ARCH.md), [REF_14_DX](docs/REF_14_DX.md), [REF_15_API](docs/REF_15_API.md), [REF_51_TEST](docs/REF_51_TEST.md).
- **Tests:** [docs/REF_51_TEST.md](docs/REF_51_TEST.md). Run: `python tests/runner.py` from repo root.

---

## License and links

MIT - see [LICENSE](LICENSE).

- **Homepage:** https://exonware.com  
- **Repository:** https://github.com/exonware/xwnode  

Contributing: CONTRIBUTING.md · Security: SECURITY.md (when present).
Version: 0.9.0.16 | Updated: 30-Mar-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
