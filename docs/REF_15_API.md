<!-- docs/REF_15_API.md (output of GUIDE_15_API) -->
# xwnode — API Reference

**Last Updated:** 07-Feb-2026

API reference for xwnode (output of GUIDE_15_API). **Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 6.

**Main entry points / key code:** XWNode, XWEdge, XWFactory; create_with_preset, list_available_presets; fast, optimized, adaptive, dual_adaptive; NodeMode, EdgeMode, NodeTrait, EdgeTrait, GraphOptimization; merge_nodes, diff_nodes, patch_nodes; XWGraphManager; get_config/set_config, XWNodeConfig.

**Core:** XWNode, strategies (HashMap, B-Tree, Trie, Adjacency List, LRU Cache, etc.), put/get/delete/size/iteration, edge operations.

**Node operations:** put/insert, get/find (default for missing), delete, size/len, keys/values/items (iteration). **Edge operations:** add_edge, has_edge, get_neighbors, get_incoming. **Strategy selection:** NodeMode (e.g. HASH_MAP, LRU_CACHE, B_TREE), EdgeMode; from_native(data) or mode=NodeMode.AUTO for auto-selection. **Node strategies (64):** Basic (HASH_MAP, ARRAY_LIST, LINKED_LIST, STACK, QUEUE, DEQUE), trees (B_TREE, B_PLUS_TREE, AVL_TREE, RED_BLACK_TREE, TRIE, RADIX_TRIE), specialized (BLOOM_FILTER, LRU_CACHE, UNION_FIND, SEGMENT_TREE), advanced (ART, HAMT, MASSTREE, LEARNED_INDEX). **Edge strategies (32):** ADJ_LIST, ADJ_MATRIX, EDGE_LIST, CSR, CSC, COO, R_TREE, QUADTREE, OCTREE, GRAPHBLAS, HNSW, COMPRESSED_GRAPH. **Errors:** XWNodeError, XWNodeTypeError, XWNodeValueError, XWNodeUnsupportedCapabilityError. **Performance (typical):** HashMap O(1) insert/lookup/delete; B-Tree O(log n); Array list O(1) insert/lookup, O(n) delete. *Legacy full API text was in _archive/API_REFERENCE.md; value consolidated here and in [logs/reviews/REVIEW_20260207_ARCHIVE_CONSOLIDATION.md](logs/reviews/REVIEW_20260207_ARCHIVE_CONSOLIDATION.md).*

---

*Per GUIDE_00_MASTER and GUIDE_15_API.*
