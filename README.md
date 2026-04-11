# xwnode

Graph-shaped data with one API: many node and edge strategies, lots of query languages behind the same surface, and `AUTO` when you want the implementation chosen for you.

Longer write-up: [README_LONG.md](README_LONG.md).

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

---

## 📦 Install

| Install | What you get | When to use |
|---------|--------------|-------------|
| `pip install exonware-xwnode` | **Lite** - core only | Smallest install. |
| `pip install exonware-xwnode[lazy]` | **Lazy** - backends pulled in when first used | Local dev. |
| `pip install exonware-xwnode[full]` | **Full** - common strategies pre-installed | CI or production bundles. |

Requires xwsystem. Extras only add dependencies; the import path stays the same.

---

## 🚀 Quick start

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

## ✨ What you get

| Area | Contents |
|------|----------|
| **Node strategies** | Hash maps, ordered structures, LSM-style trees, tries, learned indexes, and more behind one API. |
| **Edge strategies** | Adjacency, compressed graphs, HNSW, R-tree, quadtree, temporal layouts, … |
| **Query** | Many languages (SQL, GraphQL, Cypher, XPath, …) via xwquery. |
| **Operations** | WAL, Bloom filters, lock-free options, automatic strategy selection where enabled. |

Status and roadmap: [REF_22_PROJECT](docs/REF_22_PROJECT.md). Full strategy lists: [REF_15_API](docs/REF_15_API.md), [docs/](docs/).

---

## 📊 Strategy Matrix - Possibilities

# **94 IMPLEMENTATIONS**
## **63 NODE STRATEGIES x 31 EDGE STRATEGIES = 1,953 MIX-AND-MATCH COMBINATIONS**

Choose any node strategy and pair it with any edge strategy under the same `XWNode` API surface.

> Scientific compatibility note:
> Not every node-edge combination is semantically valid for every workload.
> Use strategy pairs that match the data model and query physics.
> Example: matrix/sparse-matrix representations and tree-centric representations solve different structural problems, so they should not be treated as equivalent.

### Node strategy implementations (63)

| Implementation | File |
|---|---|
| `AdjacencyListStrategy` | `adjacency_list.py` |
| `AhoCorasickStrategy` | `aho_corasick.py` |
| `ArrayListStrategy` | `array_list.py` |
| `ARTStrategy` | `art.py` |
| `ASTStrategy` | `ast.py` |
| `AVLTreeStrategy` | `avl_tree.py` |
| `BPlusTreeStrategy` | `b_plus_tree.py` |
| `BTreeStrategy` | `b_tree.py` |
| `BitmapStrategy` | `bitmap.py` |
| `BitsetDynamicStrategy` | `bitset_dynamic.py` |
| `BloomFilterStrategy` | `bloom_filter.py` |
| `BloomierFilterStrategy` | `bloomier_filter.py` |
| `BwTreeStrategy` | `bw_tree.py` |
| `CircularBufferStrategy` | `circular_buffer.py` |
| `CountMinSketchStrategy` | `count_min_sketch.py` |
| `COWTreeStrategy` | `cow_tree.py` |
| `CRDTMapStrategy` | `crdt_map.py` |
| `CuckooHashStrategy` | `cuckoo_hash.py` |
| `DataInterchangeOptimizedStrategy` | `data_interchange_optimized.py` |
| `DawgStrategy` | `dawg.py` |
| `DequeStrategy` | `deque.py` |
| `ExtendibleHashStrategy` | `extendible_hash.py` |
| `FenwickTreeStrategy` | `fenwick_tree.py` |
| `HAMTStrategy` | `hamt.py` |
| `HashMapStrategy` | `hash_map.py` |
| `HeapStrategy` | `heap.py` |
| `HistogramStrategy` | `histogram.py` |
| `HopscotchHashStrategy` | `hopscotch_hash.py` |
| `HyperLogLogStrategy` | `hyperloglog.py` |
| `IntervalTreeStrategy` | `interval_tree.py` |
| `KdTreeStrategy` | `kd_tree.py` |
| `LearnedIndexStrategy` | `learned_index.py` |
| `LinearHashStrategy` | `linear_hash.py` |
| `LinkedListStrategy` | `linked_list.py` |
| `LRUCacheStrategy` | `lru_cache.py` |
| `LSMTreeStrategy` | `lsm_tree.py` |
| `MasstreeStrategy` | `masstree.py` |
| `OrderedMapStrategy` | `ordered_map.py` |
| `OrderedMapBalancedStrategy` | `ordered_map_balanced.py` |
| `PatriciaStrategy` | `patricia.py` |
| `PersistentTreeStrategy` | `persistent_tree.py` |
| `PriorityQueueStrategy` | `priority_queue.py` |
| `QueueStrategy` | `queue.py` |
| `RadixTrieStrategy` | `radix_trie.py` |
| `RangeMapStrategy` | `range_map.py` |
| `RedBlackTreeStrategy` | `red_black_tree.py` |
| `RoaringBitmapStrategy` | `roaring_bitmap.py` |
| `RopeStrategy` | `rope.py` |
| `SegmentTreeStrategy` | `segment_tree.py` |
| `SetHashStrategy` | `set_hash.py` |
| `SetTreeStrategy` | `set_tree.py` |
| `SkipListStrategy` | `skip_list.py` |
| `SparseMatrixStrategy` | `sparse_matrix.py` |
| `SplayTreeStrategy` | `splay_tree.py` |
| `StackStrategy` | `stack.py` |
| `SuffixArrayStrategy` | `suffix_array.py` |
| `TDigestStrategy` | `t_digest.py` |
| `TTreeStrategy` | `t_tree.py` |
| `TreapStrategy` | `treap.py` |
| `TreeGraphHybridStrategy` | `tree_graph_hybrid.py` |
| `TrieStrategy` | `trie.py` |
| `UnionFindStrategy` | `union_find.py` |
| `VebTreeStrategy` | `veb_tree.py` |

### Edge strategy implementations (31)

| Implementation | File |
|---|---|
| `AdjListStrategy` | `adj_list.py` |
| `AdjMatrixStrategy` | `adj_matrix.py` |
| `BidirWrapperStrategy` | `bidir_wrapper.py` |
| `BitemporalStrategy` | `bitemporal.py` |
| `BlockAdjMatrixStrategy` | `block_adj_matrix.py` |
| `BVGraphStrategy` | `bv_graph.py` |
| `CompressedGraphStrategy` | `compressed_graph.py` |
| `COOStrategy` | `coo.py` |
| `CSCStrategy` | `csc.py` |
| `CSRStrategy` | `csr.py` |
| `DynamicAdjListStrategy` | `dynamic_adj_list.py` |
| `EdgeListStrategy` | `edge_list.py` |
| `EdgePropertyStoreStrategy` | `edge_property_store.py` |
| `EulerTourStrategy` | `euler_tour.py` |
| `FlowNetworkStrategy` | `flow_network.py` |
| `GraphBLASStrategy` | `graphblas.py` |
| `HNSWStrategy` | `hnsw.py` |
| `Hop2LabelsStrategy` | `hop2_labels.py` |
| `HyperEdgeSetStrategy` | `hyperedge_set.py` |
| `IncidenceMatrixStrategy` | `incidence_matrix.py` |
| `K2TreeStrategy` | `k2_tree.py` |
| `LinkCutStrategy` | `link_cut.py` |
| `MultiplexStrategy` | `multiplex.py` |
| `NeuralGraphStrategy` | `neural_graph.py` |
| `OctreeStrategy` | `octree.py` |
| `QuadTreeStrategy` | `quadtree.py` |
| `RoaringAdjStrategy` | `roaring_adj.py` |
| `RTreeStrategy` | `rtree.py` |
| `TemporalEdgeSetStrategy` | `temporal_edgeset.py` |
| `TreeGraphBasicStrategy` | `tree_graph_basic.py` |
| `WeightedGraphStrategy` | `weighted_graph.py` |

> Source of truth: strategy classes discovered in `src/exonware/xwnode/nodes/strategies/` and `src/exonware/xwnode/edges/strategies/`.

---

## 🌐 Ecosystem functional contributions

`xwnode` owns structural representation; sibling libs add query, data transport, validation, and persistence capabilities around that structure.
You can use `xwnode` standalone as a graph/tree/strategy data engine.
The full XW ecosystem is optional and is mainly for enterprise and mission-critical scenarios where structure, query, validation, and storage need unified self-managed infrastructure.

| Supporting XW lib | What it provides to xwnode | Functional requirement it satisfies |
|------|----------------|----------------|
| **XWQuery** | Multi-language query execution over node/edge structures. | Rich graph/tree querying without binding to a single query syntax. |
| **XWData** | Data load/save/transform bridges to and from node structures. | Interchange between external formats and in-memory graph models. |
| **XWSystem** | Core runtime foundations (serialization, caching, utilities, base contracts). | Performance and consistency for node strategies and runtime behavior. |
| **XWSchema** | Optional schema constraints for node payload integrity. | Validation guarantees for graph payloads and structured updates. |
| **XWStorage** | Durable backend persistence for node-driven datasets. | Persistent graph/state storage beyond process memory. |
| **XWEntity** | Domain entity alignment for graph-backed business models. | Domain-aware graph operations rather than raw structural manipulation only. |

Competitive edge: `xwnode` is not only a graph container; it is a strategy-rich structure engine that plugs directly into query, validation, and storage layers.

---

## 📖 Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md).
- **Usage:** [docs/GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md).
- **REFs:** [REF_01_REQ](docs/REF_01_REQ.md), [REF_22_PROJECT](docs/REF_22_PROJECT.md), [REF_13_ARCH](docs/REF_13_ARCH.md), [REF_14_DX](docs/REF_14_DX.md), [REF_15_API](docs/REF_15_API.md), [REF_51_TEST](docs/REF_51_TEST.md).
- **Tests:** [docs/REF_51_TEST.md](docs/REF_51_TEST.md). Run: `python tests/runner.py` from repo root.

---

## 📜 License and links

Apache-2.0 - see [LICENSE](LICENSE).

- **Homepage:** https://exonware.com  
- **Repository:** https://github.com/exonware/xwnode  

## ⏱️ Async Support

<!-- async-support:start -->
- xwnode includes asynchronous execution paths in production code.
- Source validation: 522 async def definitions and 0 await usages under src/.
- Use async APIs for I/O-heavy or concurrent workloads to improve throughput and responsiveness.
<!-- async-support:end -->
Version: 0.9.0.24 | Updated: 11-Apr-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
