# Developer Experience Reference — xwnode (REF_14_DX)

**Library:** exonware-xwnode  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 5–6  
**Producing guide:** [GUIDE_14_DX.md](../../docs/guides/GUIDE_14_DX.md)

---

## Purpose

DX contract for xwnode: happy paths, "key code," and ergonomics. Filled from REF_01_REQ.

---

## Key code (1–3 lines)

| Task | Code |
|------|------|
| Create from native data | `node = XWNode.from_native(data)` or `XWNode(mode=NodeMode.X)` |
| Put / get / delete | `node.put(key, value)`, `value = node.get(key)`, `node.delete(key)` |
| Choose strategy | `XWNode(mode=NodeMode.X)` or use presets (fast, optimized, adaptive, dual_adaptive) |
| List presets | `XWNode.create_with_preset(...)`, `list_available_presets()` |

---

## Developer persona (from REF_01_REQ sec. 5)

Developer: create with XWNode.from_native(data) or XWNode(mode=NodeMode.X); do put/get in 1–3 lines; choose strategy without reinventing the wheel.

---

## Easy vs advanced

| Easy (1–3 lines) | Advanced |
|------------------|----------|
| from_native(data), put/get/delete, mode=NodeMode.X | Strategy options, immutable/COW, path_cache_size, NodeMerger/NodeDiffer/NodePatcher, graph optimization, XWGraphManager, merge_nodes/diff_nodes/patch_nodes, get_config/set_config, XWNodeConfig. |

---

## Main entry points (from REF_01_REQ sec. 6)

- **Facade:** XWNode, XWEdge, XWFactory
- **Presets:** create_with_preset, list_available_presets; fast, optimized, adaptive, dual_adaptive
- **Modes:** NodeMode, EdgeMode, NodeTrait, EdgeTrait, GraphOptimization
- **Operations:** merge_nodes, diff_nodes, patch_nodes; XWGraphManager
- **Config:** get_config/set_config, XWNodeConfig

---

## Usability expectations (from REF_01_REQ sec. 8)

Single API, AUTO mode, presets; docs (API_REFERENCE, TUTORIAL_QUICK_START, architecture); clear error types (XWNodeError family, XWNodeSecurityError). "One import, one API"; unified interface across strategies.

---

*See [REF_01_REQ.md](REF_01_REQ.md), [REF_15_API.md](REF_15_API.md), and [REF_21_PLAN.md](REF_21_PLAN.md) for milestones. Per GUIDE_14_DX.*
