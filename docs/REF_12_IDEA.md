# Idea Reference — xwnode (REF_12_IDEA)

**Library:** exonware-xwnode  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) (GUIDE_01_REQ)  
**Producing guide:** [GUIDE_12_IDEA.md](../../docs/guides/GUIDE_12_IDEA.md)

---

## Purpose

Idea context and evaluation for xwnode, filled from REF_01_REQ. Used for traceability from idea → requirements → project.

---

## Core Idea (from REF_01_REQ sec. 1–2)

| Field | Content |
|-------|---------|
| **Problem statement** | Avoids locking into one strategy or one way of doing data structures; gives flexibility to choose; don't reinvent the wheel—select the strategy you want and execute. |
| **Solution direction** | Create data structures easily by selecting configurations (node strategy, edge strategy—edge can be none), plus caching; high performance; used everywhere (data, processing, logic; future TypeScript/frontend). |
| **One-sentence purpose** | Create data structures easily by selecting configurations (node strategy, edge strategy—edge can be none), plus caching; high performance; used everywhere (data, processing, logic; future TypeScript/frontend). |
| **Primary beneficiaries** | Mainly developers; primarily Exonware internal; possibly external later. Used for building databases, processing language, compiler, runtime. |
| **Top goals (ordered)** | (1) Support xwdata; (2) xwentity; (3) xwschema, xwaction—all through xwnode implementation in xwdata. |
| **Out of scope** | Actual format of data (disk vs RAM). Treat xwnode as node system, not data system. XWData handles data. No serialization in xwnode; serialization done outside. xwnode must implement XWQuery functionalities and support; avoid circular referencing so xwdata, xwschema, xwaction can extend and reuse. |

---

## Evaluation

| Criterion | Assessment |
|-----------|------------|
| **Status** | Approved (implemented; 60+ node strategies, 30+ edge strategies in codebase). |
| **Five Priorities** | Security, Usability, Maintainability, Performance, Extensibility — addressed in REF_01_REQ sec. 8 (path validation, single API, presets, REF_*, tests). |
| **Traceability** | REF_01_REQ → REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API, REF_21_PLAN. |

---

*See [REF_01_REQ.md](REF_01_REQ.md) for full requirements; [REF_22_PROJECT.md](REF_22_PROJECT.md) for project status. **Consumers:** xwdata, xwentity, xwschema, xwaction — see [REF_22_PROJECT](REF_22_PROJECT.md) traceability.*
