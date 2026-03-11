# xwnode — Usage Guide

**Last Updated:** 07-Feb-2026

How to use xwnode (output of GUIDE_41_DOCS). See [REF_01_REQ.md](REF_01_REQ.md), [REF_11_COMP.md](REF_11_COMP.md), [REF_22_PROJECT.md](REF_22_PROJECT.md), [REF_14_DX.md](REF_14_DX.md) (key code), [REF_15_API.md](REF_15_API.md), [REF_21_PLAN.md](REF_21_PLAN.md) (milestones). Full set: [INDEX.md](INDEX.md).

---

## Install (avoid xwlazy delays)

```bash
pip install exonware-xwsystem
pip install numpy>=1.24.0 scipy>=1.10.0 scikit-learn>=1.2.0
pip install exonware-xwnode
# or: pip install -r requirements.txt
```

Performance deps (numpy, scipy, scikit-learn) are in requirements.txt/pyproject.toml so imports are fast.

---

## Quick start (REF_01_REQ sec. 5–6)

One API: create from data or with strategy, put/get/delete, optional graph and query.

```python
from exonware.xwnode import XWNode

# From native data (AUTO mode)
node = XWNode.from_native({'a': 1, 'b': 2})

# put / get / delete
node.put('c', 3)
val = node.get('c')
node.delete('c')
```

---

## Easy vs advanced (REF_15_API)

- **Easy:** `from_native(data)`, `put`/`get`/`delete`, `mode=NodeMode.X` (or AUTO).
- **Advanced:** Presets (fast, optimized, adaptive, dual_adaptive), merge/diff/patch, path cache, graph optimization, XWGraphManager. See [REF_15_API.md](REF_15_API.md) and [REF_01_REQ.md](REF_01_REQ.md) sec. 6.

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [REF_01_REQ.md](REF_01_REQ.md) | Requirements (vision, scope, API expectations) |
| [REF_12_IDEA.md](REF_12_IDEA.md) | Idea context and evaluation |
| [REF_22_PROJECT.md](REF_22_PROJECT.md) | Project vision, goals, FR/NFR, milestones |
| [REF_13_ARCH.md](REF_13_ARCH.md) | Architecture and boundaries |
| [REF_14_DX.md](REF_14_DX.md) | Developer experience and key code |
| [REF_15_API.md](REF_15_API.md) | Public API reference |
| [REF_21_PLAN.md](REF_21_PLAN.md) | Milestones and roadmap |
| [INDEX.md](INDEX.md) / [MASTER_INDEX.md](MASTER_INDEX.md) | Docs index |

**Examples (repo `examples/`):**

| Example | Purpose |
|---------|---------|
| [examples/db_example/](../../examples/db_example/) | DB-style runs and benchmarks (x1_basic_db … x6_file_advance_db) |
| [examples/x5/](../../examples/x5/) | Data operations and benchmark comparisons |
| [examples/enhanced_xnode_demo.py](../../examples/enhanced_xnode_demo.py) | Enhanced XWNode usage demo |

---

*Per GUIDE_00_MASTER and GUIDE_41_DOCS.*
