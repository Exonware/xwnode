# Requirements Reference (REF_01_REQ)

**Project:** xwnode  
**Sponsor:** ExonWare  
**Version:** 0.0.1  
**Last Updated:** 07-Feb-2026  
**Produced by:** [GUIDE_01_REQ.md](../../docs/guides/GUIDE_01_REQ.md)

---

## Purpose of This Document

This document is the **single source of raw and refined requirements** collected from the project sponsor and stakeholders. It is updated on every requirements-gathering run. When the **Clarity Checklist** (section 12) reaches the agreed threshold, use this content to fill REF_11_COMP, REF_12_IDEA, REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API, and REF_21_PLAN (planning artifacts). Template structure: [GUIDE_01_REQ.md](../../docs/guides/GUIDE_01_REQ.md).

---

## 1. Vision and Goals

| Field | Content |
|-------|---------|
| One-sentence purpose | Create data structures easily by selecting configurations (node strategy, edge strategy—edge can be none), plus caching; high performance; used everywhere (data, processing, logic; future TypeScript/frontend). |
| Primary users/beneficiaries | Mainly developers; primarily Exonware internal; possibly external later. Used for building databases, processing language, compiler, runtime. |
| Success (6 mo / 1 yr) | Already in production with many strategies (60+ node strategies, 30+ edge strategies in codebase). Need more use cases to ensure it does what we want. |
| Top 3–5 goals (ordered) | (1) Support xwdata; (2) xwentity; (3) xwschema, xwaction—all through xwnode implementation in xwdata. |
| Problem statement | Avoids locking into one strategy or one way of doing data structures; gives flexibility to choose; don’t reinvent the wheel—select the strategy you want and execute. |

## 2. Scope and Boundaries

| In scope | Out of scope | Dependencies | Anti-goals |
|----------|--------------|--------------|------------|
| v1: reverse-engineer all existing capabilities—graph configuration, number of strategies for edges, number of strategies for nodes. **xwnode must implement XWQuery functionalities and support; avoid circular referencing** so xwdata, xwschema, xwaction can extend and reuse. | Actual format of data (disk vs RAM). Treat xwnode as node system, not data system. XWData handles data. No serialization in xwnode; serialization done outside. | Whatever is in the library now (e.g. xwsystem). | Not specific to a certain market; extremely broad. Focus on theory of nodes so others focus on business; xwnode focuses on node logic, others on the rest. |

## 3. Stakeholders and Sponsor

| Sponsor (name, role, final say) | Main stakeholders | External customers/partners | Doc consumers |
|----------------------------------|-------------------|-----------------------------|---------------|
| ExonWare (same as other projects). | Developers and product uses of the advanced libraries. | No external users for now; maybe in the future Python sponsorship and showcase of the library. | Mostly developers and other users. |

## 4. Compliance and Standards

| Regulatory/standards | Security & privacy | Certifications/evidence |
|----------------------|--------------------|--------------------------|
| No standard in mind for this version; developed with highest standards in mind; will review when we reach a version that requires MARS standard. | Same: no specific requirements for this version; will review at MARS version. | Same: no specific for this version; will review when MARS version. |

## 5. Product and User Experience

| Main user journeys/use cases | Developer persona & 1–3 line tasks | Usability/accessibility | UX/DX benchmarks |
|-----------------------------|------------------------------------|--------------------------|------------------|
| (1) Create node from native data or with explicit strategy (NodeMode/EdgeMode). (2) put/get/delete/size/iterate. (3) Graph/tree with edge strategy (edge can be none). (4) Query via xwquery adapters (35+ languages). (5) merge/diff/patch operations. (6) Presets and performance modes (fast, optimized, adaptive, dual_adaptive). (7) Path navigation with optional path cache. | Developer: create with XWNode.from_native(data) or XWNode(mode=NodeMode.X); do put/get in 1–3 lines; choose strategy without reinventing the wheel. | Clear errors (XWNodeError family); README, TUTORIAL_QUICK_START, API_REFERENCE; AUTO mode for zero-config. | "One import, one API"; unified interface across strategies; like multiple backends (Redis/Neo4j/Firestore-style) with one API and strategy selection. |

## 6. API and Surface Area

| Main entry points / "key code" | Easy (1–3 lines) vs advanced | Integration/existing APIs | Not in public API |
|--------------------------------|------------------------------|---------------------------|-------------------|
| XWNode, XWEdge, XWFactory; create_with_preset, list_available_presets; fast, optimized, adaptive, dual_adaptive; NodeMode, EdgeMode, NodeTrait, EdgeTrait, GraphOptimization; merge_nodes, diff_nodes, patch_nodes; XWGraphManager; get_config/set_config, XWNodeConfig. | Easy: from_native(data), put/get/delete, mode=NodeMode.X. Advanced: strategy options, immutable/COW, path_cache_size, NodeMerger/NodeDiffer/NodePatcher, graph optimization. | xwquery (query execution), xwsystem (serialization, security, metrics), xwdata when used together. | Internal strategy classes, base/contracts implementation details, _strategy_manager, _nav_cache, registry internals. |

## 7. Architecture and Technology

| Required/forbidden tech | Preferred patterns | Scale & performance | Multi-language/platform |
|-------------------------|--------------------|----------------------|-------------------------|
| Python ≥3.12; exonware-xwsystem; numpy/scipy/scikit-learn for some strategies (learned index, etc.). No serialization in xwnode (done outside). | Facade (XWNode single entry), Strategy (node/edge pluggable), Adapter (query languages), Registry for strategy discovery. | Scales from KB to TB (README); path cache for 30–50x on cache hits; benchmarks in benchmarks/; async support in codebase. | Python now; TypeScript/frontend later (per vision). |

## 8. Non-Functional Requirements (Five Priorities)

| Security | Usability | Maintainability | Performance | Extensibility |
|----------|-----------|-----------------|-------------|---------------|
| Path validation, input sanitization, audit (xwsystem); XWNodeSecurityError, path security; review at MARS version. | Single API, AUTO mode, presets; docs (API_REFERENCE, TUTORIAL_QUICK_START, architecture); clear error types. | Contracts/base/facade layering; tests 0.core, 1.unit, 2.integration, 3.advance; REF_* and docs under docs/. | Benchmarks; path cache; async-first where implemented; strategy-specific performance claims. | Pluggable strategies, registry, no hard-coded strategy limits; versioning/compatibility. |

## 9. Milestones and Timeline

| Major milestones | Definition of done (first) | Fixed vs flexible |
|------------------|----------------------------|-------------------|
| M1 Core strategies and engine (Done). M2 Query languages, WAL/Bloom/CAS (Done). M3 REF and review compliance (Done). M4 XWQuery support without circular ref, xwdata/xwentity/xwschema/xwaction support (pending). M5 Beta after production use (future). | First milestone DoD: strategies + engine + XWNode facade working; put/get/delete/size/iterate and at least one graph path. | Scope (xwdata, xwquery, xwschema, xwaction) is fixed as goal; dates flexible. |

## 10. Risks and Assumptions

| Top risks | Assumptions | Kill/pivot criteria |
|-----------|-------------|----------------------|
| (1) Circular dependency with xwquery/xwdata—mitigation: explicit no circular ref; xwnode implements xwquery support. (2) Strategy proliferation complexity—mitigation: contracts, registry, tests. (3) Performance regression—mitigation: benchmarks, path cache. | Python 3.12+; xwsystem available; xwquery integration expected; developers consume docs and presets. | If xwdata/xwquery support cannot be achieved without circular ref; or core strategy set becomes unmaintainable. |

## 11. Workshop / Session Log (Optional)

| Date | Type | Participants | Outcomes |
|------|------|---------------|----------|
| 07-Feb-2026 | Batch 1 — Vision and scope | Sponsor | Sections 1–2 filled from sponsor answers; strategy counts verified (60+ node, 30+ edge). |
| 07-Feb-2026 | Batch 2 — Stakeholders and compliance | Sponsor | Sections 3–4 filled; XWQuery support and no circular ref added to scope. |
| 07-Feb-2026 | Batch 3 — Reverse-engineered from codebase | Sponsor | Sections 5–10 filled from codebase (README, __init__, facade, REF_13/22/15, pyproject, tests, benchmarks). |
| 07-Feb-2026 | PROMPT_01_REQ_03_UPDATE — downstream refresh and plan | Sponsor | Direction confirmed; requirements review and implementation plan produced (REVIEW_*_REQUIREMENTS.md). |
| 07-Feb-2026 | Cont downstream (GUIDE_01_USAGE, REF_51, README) | Agent | GUIDE_01_USAGE expanded (quick start, REF links); REF_51_TEST expanded (DoD, layers, Running tests); README docs section added Requirements & REFs block. |

## 12. Clarity Checklist

| # | Criterion | ☐ |
|---|-----------|---|
| 1 | Vision and one-sentence purpose filled and confirmed | ☑ |
| 2 | Primary users and success criteria defined | ☑ |
| 3 | Top 3–5 goals listed and ordered | ☑ |
| 4 | In-scope and out-of-scope clear | ☑ |
| 5 | Dependencies and anti-goals documented | ☑ |
| 6 | Sponsor and main stakeholders identified | ☑ |
| 7 | Compliance/standards stated or deferred | ☑ |
| 8 | Main user journeys / use cases listed | ☑ |
| 9 | API / "key code" expectations captured | ☑ |
| 10 | Architecture/technology constraints captured | ☑ |
| 11 | NFRs (Five Priorities) addressed | ☑ |
| 12 | Milestones and DoD for first milestone set | ☑ |
| 13 | Top risks and assumptions documented | ☑ |
| 14 | Sponsor confirmed vision, scope, priorities | ☑ |

**Clarity score:** 14 / 14. **Ready to fill downstream docs?** ☑ Yes

---

## Traceability (downstream REFs)

- **REF_11_COMP:** [REF_11_COMP.md](REF_11_COMP.md) — Compliance stance (sec. 4)
- **REF_12_IDEA:** [REF_12_IDEA.md](REF_12_IDEA.md) — Idea context (sec. 1–2)
- **REF_22_PROJECT:** [REF_22_PROJECT.md](REF_22_PROJECT.md) — Vision, FR/NFR, milestones
- **REF_13_ARCH:** [REF_13_ARCH.md](REF_13_ARCH.md) — Architecture (sec. 7)
- **REF_14_DX:** [REF_14_DX.md](REF_14_DX.md) — Developer experience (sec. 5–6)
- **REF_15_API:** [REF_15_API.md](REF_15_API.md) — API reference (sec. 6)
- **REF_21_PLAN:** [REF_21_PLAN.md](REF_21_PLAN.md) — Milestones and roadmap (sec. 9)

---

*Per GUIDE_01_REQ. Collect thoroughly, then feed downstream REFs.*
