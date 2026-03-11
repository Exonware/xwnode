# Project Reference — xwnode

**Library:** exonware-xwnode  
**Last Updated:** 07-Feb-2026

Requirements and project status (output of GUIDE_22_PROJECT). **Requirements source:** [REF_01_REQ.md](REF_01_REQ.md). Per REF_35_REVIEW.

---

## Scope and boundaries (REF_01_REQ sec. 2)

| In scope | Out of scope | Dependencies | Anti-goals |
|----------|--------------|--------------|------------|
| v1: reverse-engineer all existing capabilities—graph configuration, node/edge strategies. XWQuery support; avoid circular referencing so xwdata, xwschema, xwaction can extend and reuse. | Actual format of data (disk vs RAM). Treat xwnode as node system, not data system. No serialization in xwnode (XWData handles data). | Whatever is in the library now (e.g. xwsystem). | Not specific to one market; focus on theory of nodes so others focus on business; xwnode on node logic, others on the rest. |

---

## Vision

Create data structures easily by selecting configurations (node strategy, edge strategy—edge can be none), plus caching; high performance; used everywhere (data, processing, logic; future TypeScript/frontend). xwnode is the **graph-based data engine** for the eXonware ecosystem, providing 60+ node strategies, 30+ edge/graph representations, and 35+ query languages in a single API, with WAL, Bloom filters, atomic CAS, and scale from KB to TB.

---

## Goals (from REF_01_REQ, ordered)

1. **Support xwdata** — xwnode implementation in xwdata.
2. **Support xwentity** — through xwnode in xwdata.
3. **Support xwschema and xwaction** — all through xwnode implementation in xwdata.
4. **Unified graph API:** One interface for multiple backends and representations (adjacency list, matrix, compressed, etc.); 60+ node strategies, 30+ edge strategies; AUTO mode.
5. **XWQuery support without circular ref:** xwnode implements XWQuery functionalities and support so xwdata, xwschema, xwaction can extend and reuse.
6. **Production features:** WAL, Bloom filters, atomic CAS, async-first.

---

## Functional Requirements (Summary)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | Node strategies (57+) and edge strategies (28+) | High | Done |
| FR-002 | Query language support (35+) | High | Done |
| FR-003 | WAL, Bloom filters, lock-free, atomic CAS | High | Done |
| FR-004 | XWNode facade and engine abstraction | High | Done |
| FR-005 | xwquery and xwdata integration | High | Done |
| FR-006 | Benchmarks and 4-layer tests | High | Done |

---

## Non-Functional Requirements (5 Priorities)

1. **Security:** Path validation, input sanitization, audit (see docs).
2. **Usability:** Single API, AUTO mode, clear docs (API_REFERENCE, architecture, benchmarks).
3. **Maintainability:** Contracts/base/facade, REF_*, logs under docs/.
4. **Performance:** Benchmarks, scaling to large graphs.
5. **Extensibility:** Pluggable strategies, no hard-coded limits.

---

## Project Status Overview

- **Current phase:** Alpha (High). ~88%; 174+ files; 0.core, 1.unit, 2.integration, 3.advance; many docs in docs/ (architecture, benchmarks, changes).
- **Docs:** REF_01_REQ (source), REF_11_COMP, REF_22_PROJECT (this file), REF_13_ARCH, REF_15_API, REF_35_REVIEW, REF_51_TEST, REF_54_BENCH; logs/reviews/; MASTER_INDEX and existing docs retained.
- **Firebase alignment:** Graph/query role for Firestore/Realtime DB replacement.
- **Historical production readiness (Oct 2025):** Overall 65/100 (foundation excellent; validation pending). Security 60/100 (suite created; execution tracked); Usability 85/100. 51/51 strategies production-ready; 566/605 core tests passing. See [logs/project/PROJECT_20251011_000000_000_PRODUCTION_READINESS.md](logs/project/PROJECT_20251011_000000_000_PRODUCTION_READINESS.md).
- **Install (avoid xwlazy delays):** `pip install exonware-xwsystem` then `pip install numpy>=1.24.0 scipy>=1.10.0 scikit-learn>=1.2.0` then `pip install exonware-xwnode` (or `pip install -r requirements.txt`). See [GUIDE_01_USAGE.md](GUIDE_01_USAGE.md).
- **Migration:** All MIGRATE features verified in main library (MigrationPlan, StrategyMigrator, registry, node/edge strategies). See REF_13_ARCH.

---

## Milestones (from REF_01_REQ)

| Milestone | Target | Status |
|-----------|--------|--------|
| M1 — Core strategies and engine | v0.1.x | Done |
| M2 — Query languages and WAL/Bloom/CAS | v0.1.x | Done |
| M3 — REF_* and review compliance | v0.1.x | Done |
| M4 — XWQuery support without circular ref; xwdata/xwentity/xwschema/xwaction support | v0.1.x / next | Pending |
| M5 — Beta after production use | Future | Pending |

**Definition of done (first milestone):** Strategies + engine + XWNode facade working; put/get/delete/size/iterate and at least one graph path.

### Historical phases (xwnode roadmap)

*Value from _archive/PROJECT_PHASES.md (captured 07-Feb-2026).*

- **Version 0 (experimental):** Core node/edge framework, graph traversal, memory-efficient structures, type-safe ops, test coverage, benchmarking tools. Status: foundation complete.
- **Version 1 (production):** Production hardening, benchmarks, security audit, CI/CD. Target: Q1 2026.
- **Version 2–4:** MARS draft (Q2), Rust core (Q3), MARS implementation (Q4).

---

## Success criteria (REF_01_REQ sec. 1)

- **6 mo / 1 yr:** Already in production with many strategies (60+ node, 30+ edge). Need more use cases to ensure it does what we want.

---

## Risks and assumptions (REF_01_REQ sec. 10)

- **Risks:** Circular dependency with xwquery/xwdata (mitigation: no circular ref; xwnode implements XWQuery support). Strategy proliferation (mitigation: contracts, registry, tests). Performance regression (mitigation: benchmarks, path cache).
- **Assumptions:** Python 3.12+; xwsystem available; xwquery integration expected; developers consume docs and presets.
- **Kill/pivot:** If xwdata/xwquery support cannot be achieved without circular ref; or core strategy set becomes unmaintainable.

---

## Traceability

- **Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) (single source).
- **Ideas:** [REF_12_IDEA.md](REF_12_IDEA.md) | **DX:** [REF_14_DX.md](REF_14_DX.md) | **API:** [REF_15_API.md](REF_15_API.md) | **Planning:** [REF_21_PLAN.md](REF_21_PLAN.md).
- **Project → Arch:** This document → [REF_13_ARCH.md](REF_13_ARCH.md).
- **Review evidence:** [REF_35_REVIEW.md](REF_35_REVIEW.md), [logs/reviews/](logs/reviews/).

---

*See GUIDE_22_PROJECT.md for requirements process.*
