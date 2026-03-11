# Planning Reference — xwnode (REF_21_PLAN)

**Library:** exonware-xwnode  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 9  
**Producing guide:** [GUIDE_21_PLAN.md](../../docs/guides/GUIDE_21_PLAN.md)

---

## Purpose

Milestones and roadmap for xwnode, filled from REF_01_REQ. Execution order and phase gates per GUIDE_21_PLAN.

---

## Milestones (from REF_01_REQ sec. 9 / REF_22_PROJECT)

| Milestone | Target | Definition of done | Status |
|-----------|--------|--------------------|--------|
| M1 — Core strategies and engine | v0.1.x | Strategies + engine + XWNode facade working; put/get/delete/size/iterate and at least one graph path. | Done |
| M2 — Query languages, WAL/Bloom/CAS | v0.1.x | Query language support; WAL, Bloom filters, atomic CAS. | Done |
| M3 — REF_* and review compliance | v0.1.x | REF_22, REF_13, REF_35, REF_12, REF_14, REF_15, REF_21, docs under docs/. | Done |
| M4 — XWQuery support without circular ref | v0.1.x / next | xwdata/xwentity/xwschema/xwaction support; no circular referencing. | Pending |
| M5 — Beta after production use | Future | Beta designation after production validation. | Pending |

---

## Roadmap (from REF_01_REQ sec. 9)

| Phase | Target | Focus |
|-------|--------|--------|
| v0.1.x | Current | M1–M3 done; M4 in progress. Scope (xwdata, xwquery, xwschema, xwaction) fixed as goal; dates flexible. |
| Beta | Future | After production use. |
| TypeScript/frontend | Later | Per vision (REF_01_REQ sec. 1). |

---

## Traceability

- **Requirements:** [REF_01_REQ.md](REF_01_REQ.md)
- **Project status:** [REF_22_PROJECT.md](REF_22_PROJECT.md)
- **Idea:** [REF_12_IDEA.md](REF_12_IDEA.md) | **DX:** [REF_14_DX.md](REF_14_DX.md) | **API:** [REF_15_API.md](REF_15_API.md) | **Architecture:** [REF_13_ARCH.md](REF_13_ARCH.md)
- **Roadmap detail:** Project README, docs/changes/

---

*Per GUIDE_21_PLAN. See REF_01_REQ.md sec. 9 for fixed vs flexible.*
