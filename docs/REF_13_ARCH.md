# Architecture Reference — xwnode

**Library:** exonware-xwnode  
**Last Updated:** 07-Feb-2026

Architecture and design (output of GUIDE_13_ARCH). **Requirements source:** [REF_01_REQ.md](REF_01_REQ.md). Per REF_35_REVIEW.

---

## Overview

xwnode provides a **graph-based data engine** with strategy-based node and edge implementations, multiple query language adapters, and production features (WAL, Bloom filters, atomic CAS). The public API is the XWNode facade; internals follow contracts/base/facade and strategy patterns. **xwnode implements XWQuery functionalities and support**; the design **avoids circular referencing** so xwdata, xwschema, and xwaction can extend and reuse xwnode.

---

## Boundaries

- **Public API:** XWNode facade; from_native, put, get, add_edge, query, search, etc.
- **Strategies:** 60+ node strategies (e.g. HashMap, Learned Index) and 30+ edge/graph representations (adjacency list, matrix, compressed). Strategy selection via AUTO or explicit mode.
- **Engines:** Core engine coordinates strategies, WAL, Bloom filters, and query adapters.
- **Query layer:** 35+ query languages (SQL, GraphQL, Cypher, SPARQL, XPath, etc.) via adapters.
- **No circular ref:** xwnode does not depend on xwdata or xwquery in a way that would prevent xwdata, xwschema, or xwaction from depending on xwnode.

---

## Layering

1. **Contracts:** Node/edge strategy interfaces, engine contracts.
2. **Base:** Abstract strategy and engine implementations.
3. **Facade:** XWNode and high-level operations.
4. **Strategies:** Concrete node/edge implementations; query adapters.

---

## Delegation

- **xwsystem:** Serialization, security, utilities (e.g. path validation, audit). xwnode depends on xwsystem only (no xwquery/xwdata in xwnode’s dependency graph).
- **xwdata:** Format-agnostic data and conversion when used together (consumers use xwnode + xwdata; xwnode does not depend on xwdata).
- **xwquery:** xwnode implements or integrates XWQuery support so that xwdata, xwschema, xwaction can extend and reuse; query execution and language routing where integrated, without circular dependency.

---

## XWQuery integration (no circular ref)

xwnode provides the node/graph layer that query layers (e.g. xwquery) and data layers (xwdata) build on. xwnode **implements XWQuery functionalities and support** (per REF_01_REQ scope) and is designed to **avoid circular referencing**: xwnode’s runtime dependencies are xwsystem (and optional numpy/scipy/sklearn for some strategies). xwdata, xwschema, xwaction, and xwquery can depend on xwnode; xwnode does not depend on them, so they can extend and reuse xwnode safely.

---

## Design Patterns

- **Strategy:** Node and edge strategies are pluggable.
- **Facade:** XWNode is the single entry point.
- **Adapter:** Query language adapters translate to internal operations.
- **Cache strategies:** LRU_CACHE and related cache strategies use ACachedStrategy/AKeyValueStrategy; documented in strategy docs and REF_15. Legacy strategy documentation (STRATEGY_*, DESIGN_PATTERNS, QUERY_OPERATIONS_ARCHITECTURE) value consolidated here and in [logs/reviews/REVIEW_20260207_ARCHIVE_CONSOLIDATION.md](logs/reviews/REVIEW_20260207_ARCHIVE_CONSOLIDATION.md).
- **Migration:** All MIGRATE features (MigrationPlan, StrategyMigrator, registry, node/edge implementations) verified in main library.

---

*See GUIDE_13_ARCH.md for architecture process. Requirements: [REF_01_REQ.md](REF_01_REQ.md) → [REF_22_PROJECT.md](REF_22_PROJECT.md).*
