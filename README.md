# xwnode

**Graph-based data engine with one API.** 60+ node strategies, 30+ edge/graph representations, and 35+ query languages behind a single interface; AUTO mode picks the right strategy.

*Full features and DX: [README_LONG.md](README_LONG.md).*

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  
**Version:** See [version.py](src/exonware/xwnode/version.py) or PyPI. · **Updated:** See [version.py](src/exonware/xwnode/version.py) (`__date__`)

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

| Install | What you get | When to use |
|---------|--------------|-------------|
| `pip install exonware-xwnode` | **Lite** — core only | Minimal footprint. |
| `pip install exonware-xwnode[lazy]` | **Lazy** — missing deps on first use | Development. |
| `pip install exonware-xwnode[full]` | **Full** — common strategies pre-installed | Production or CI. |

Requires xwsystem. Same package; `[lazy]` and `[full]` are extras.

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

Choose strategy: `XWNode(mode=NodeMode.HASH_MAP)`, `NodeMode.LSM_TREE`, `EdgeMode.COMPRESSED_GRAPH`, `EdgeMode.HNSW`, or `NodeMode.AUTO`. See [REF_14_DX](docs/REF_14_DX.md) and [REF_15_API](docs/REF_15_API.md).

---

## What you get

| Area | What's in it |
|------|----------------|
| **Node strategies** | Many data structures (HashMap, OrderedMap, LSM Tree, B+ Tree, Trie, Bloom Filter, Learned Index, …) behind one API. |
| **Edge strategies** | Graph representations (adjacency, compressed graph, HNSW, R-Tree, QuadTree, temporal, …). |
| **Query** | 35+ languages (SQL, GraphQL, Cypher, XPath, …) via xwquery integration. |
| **Production** | WAL, Bloom filters, lock-free options, AUTO strategy selection. |

Current status and roadmap: [REF_22_PROJECT](docs/REF_22_PROJECT.md). Full strategy list and examples: [REF_15_API](docs/REF_15_API.md), [docs/](docs/).

---

## Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md).
- **Use it:** [docs/GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md).
- **REFs:** [REF_01_REQ](docs/REF_01_REQ.md), [REF_22_PROJECT](docs/REF_22_PROJECT.md), [REF_13_ARCH](docs/REF_13_ARCH.md), [REF_14_DX](docs/REF_14_DX.md), [REF_15_API](docs/REF_15_API.md), [REF_51_TEST](docs/REF_51_TEST.md).
- **Tests:** See [docs/REF_51_TEST.md](docs/REF_51_TEST.md). Run: `python tests/runner.py` from project root.

---

## License and links

MIT — see [LICENSE](LICENSE).

- **Homepage:** https://exonware.com  
- **Repository:** https://github.com/exonware/xwnode  
- **Version:** `from exonware.xwnode import __version__`  

Contributing → CONTRIBUTING.md · Security → SECURITY.md (when present).

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
