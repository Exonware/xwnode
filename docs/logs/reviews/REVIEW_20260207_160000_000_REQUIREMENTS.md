# Review: Project/Requirements — xwnode (REF_01_REQ alignment)

**Date:** 07-Feb-2026 16:00:00.000  
**Artifact type:** Project/Requirements  
**Scope:** REF_01_REQ.md + code (src/) + tests (0.core–3.advance) + docs (REF_*, README, TUTORIAL)  
**Methodology:** GUIDE_35_REVIEW (six categories); PROMPT_01_REQ_03_UPDATE (Step 2).

---

## Summary

**Outcome:** Pass with gaps. REF_01_REQ is complete (14/14 clarity) and reflects sponsor direction. Downstream REFs (REF_22_PROJECT, REF_13_ARCH) exist but are not fully aligned with REF_01_REQ. REF_12_IDEA and REF_14_DX are missing. Code and tests largely reflect REF_01_REQ; main gaps are (1) explicit documentation of XWQuery integration without circular ref, (2) refresh of REF_22 and REF_13 from REF_01_REQ, (3) optional REF_12_IDEA and REF_14_DX. Implementation plan below addresses both existing REF_01_REQ gaps and downstream refresh.

---

## 1. Critical issues

| Finding | Location | Note |
|--------|----------|------|
| None blocking | — | No inconsistent or conflicting requirements in REF_01_REQ. |
| REF_22 vs REF_01_REQ | REF_22_PROJECT.md | REF_22 goals and milestones do not yet reflect REF_01_REQ: top goals (xwdata, xwentity, xwschema, xwaction) and M4 (XWQuery support without circular ref + ecosystem support) are in REF_01_REQ but REF_22 still has older M4 wording ("Consider Beta after production use"). |

---

## 2. Improvements

| Finding | Location | Suggestion |
|--------|----------|------------|
| REF_13 delegation | REF_13_ARCH.md | Add explicit statement that xwnode implements XWQuery support and avoids circular referencing so xwdata/xwschema/xwaction can extend. |
| REF_22 traceability | REF_22_PROJECT.md | Add traceability line: "Project ← REF_01_REQ (requirements source)." |
| REF_01_REQ link from REF_22 | REF_22_PROJECT.md | In traceability section, reference REF_01_REQ as the source of requirements. |

---

## 3. Optimizations

| Finding | Location | Suggestion |
|--------|----------|------------|
| Duplicate vision text | REF_22 vs REF_01_REQ | After refresh, keep REF_22 vision concise and aligned with REF_01_REQ section 1 (one sentence + goals). |
| Milestone numbering | REF_22 | Align M4/M5 with REF_01_REQ: M4 = XWQuery support (no circular ref) + xwdata/xwentity/xwschema/xwaction; M5 = Beta after production use. |

---

## 4. Missing features / alignment

| Gap | REF_01_REQ says | Code/Tests/Docs status |
|-----|------------------|------------------------|
| Downstream REFs from REF_01_REQ | Use REF_01_REQ to fill REF_12_IDEA, REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API (GUIDE_01_REQ). | REF_22 and REF_13 exist but not refreshed from REF_01_REQ. REF_12_IDEA and REF_14_DX missing. REF_15_API exists and is minimal. |
| XWQuery support without circular ref | In scope: xwnode must implement XWQuery functionalities and support; avoid circular referencing. | Integration with xwquery exists in codebase; architectural doc does not explicitly state "no circular ref" and "xwnode implements xwquery support" as design constraints. |
| M4 / M5 milestones | M4 pending (XWQuery + xwdata/xwentity/xwschema/xwaction); M5 future (Beta). | REF_22 has M4 as "Consider Beta after production use" only—no M4 for XWQuery and ecosystem support. |
| Goals in REF_22 | Top goals: (1) xwdata, (2) xwentity, (3) xwschema, xwaction (REF_01_REQ sec. 1). | REF_22 lists unified API, strategy-based, query, production features, Firebase parity—does not list xwdata/xwentity/xwschema/xwaction as ordered goals. |

---

## 5. Compliance & standards

| Check | Status |
|-------|--------|
| REF_01_REQ in project docs/ | Yes — xwnode/docs/REF_01_REQ.md |
| Five Priorities in REF_01_REQ | Yes — Section 8 |
| GUIDE_00_MASTER placement | Docs under docs/; REF in project. |
| Downstream REF ownership | REF_22 (GUIDE_22), REF_13 (GUIDE_13), REF_12 (GUIDE_12), REF_14 (GUIDE_14), REF_15 (GUIDE_15). |

---

## 6. Traceability

| Link | Status |
|------|--------|
| REF_01_REQ → REF_22, REF_13, REF_12, REF_14, REF_15 | REF_01_REQ states "use this content to fill" those REFs; refresh not yet done. |
| REF_22 → REF_01_REQ | Not stated in REF_22; should add. |
| REF_13 → REF_22 | Yes (REF_13 references REF_22). |
| Code/tests to REF_01_REQ | Implicit (code implements strategies, facade, operations); no orphan features identified. |

---

## Implementation plan

Action items to (1) implement what is already in REF_01_REQ and (2) put the downstream refresh in place.

### Priority 1 — High (align direction and docs)

| # | Action | Owner | Outcome |
|---|--------|--------|---------|
| P1.1 | **Refresh REF_22_PROJECT from REF_01_REQ** | Docs | Vision and goals (section 1) and milestones (section 9) from REF_01_REQ reflected in REF_22; add top goals (1) xwdata (2) xwentity (3) xwschema/xwaction; set M4 = XWQuery support without circular ref + xwdata/xwentity/xwschema/xwaction support (pending), M5 = Beta after production use (future); add traceability to REF_01_REQ. |
| P1.2 | **Refresh REF_13_ARCH from REF_01_REQ** | Docs | In Boundaries or Delegation, add: xwnode implements XWQuery functionalities and support; design avoids circular referencing so xwdata, xwschema, xwaction can extend and reuse. Add traceability to REF_01_REQ. |
| P1.3 | **Update REF_15_API if needed** | Docs | Confirm main entry points in REF_15 (or API_REFERENCE) match REF_01_REQ sec. 6 (XWNode, XWFactory, presets, performance modes, NodeMode/EdgeMode, merge/diff/patch, XWGraphManager, config). Add one-line traceability to REF_01_REQ if missing. |

### Priority 2 — Medium (optional REFs and clarity)

| # | Action | Owner | Outcome |
|---|--------|--------|---------|
| P2.1 | **Create or defer REF_12_IDEA** | Docs | Per GUIDE_01_REQ handoffs, REF_01_REQ can feed REF_12_IDEA. Either create xwnode/docs/REF_12_IDEA.md from REF_01_REQ (vision, problem statement, evaluation context) or document "REF_12_IDEA deferred" in REF_22 or REF_35. |
| P2.2 | **Create or defer REF_14_DX** | Docs | Per GUIDE_01_REQ, REF_01_REQ can feed REF_14_DX (developer experience, "key code" goals). Either create REF_14_DX from REF_01_REQ sec. 5–6 or document deferral. |
| P2.3 | **Document XWQuery integration constraint in REF_13 or design doc** | Docs | One short paragraph: xwnode provides or integrates XWQuery support without introducing circular dependencies (xwnode does not depend on xwdata/xwquery in a way that prevents xwdata/xwschema/xwaction from depending on xwnode). |

### Priority 3 — Lower (ongoing)

| # | Action | Owner | Outcome |
|---|--------|--------|---------|
| P3.1 | **Verify no circular ref in dependency graph** | Dev | Confirm package dependencies (pyproject.toml, imports) show xwnode depending only on xwsystem (and optional xwlazy); xwquery/xwdata depend on xwnode where needed, not the reverse. |
| P3.2 | **Plan/REF_21_PLAN** | Plan | If REF_21_PLAN or equivalent exists, align phases with REF_01_REQ milestones (M4, M5). If not, consider adding a short plan or linking milestones to backlog. |

---

## Next steps (suggested order)

1. ~~Execute P1.1 and P1.2~~ ✅ Done.
2. ~~Execute P1.3~~ ✅ Done.
3. ~~Decide on P2.1 and P2.2~~ ✅ Deferred; documented in REF_22.
4. ~~Execute P2.3~~ ✅ Done (REF_13).
5. ~~Execute P3.1 and P3.2~~ ✅ Done (see below).

---

## Plan execution (07-Feb-2026)

| # | Action | Status | Outcome |
|---|--------|--------|---------|
| P1.1 | Refresh REF_22 from REF_01_REQ | Done | Vision, goals (1–6), M4/M5, traceability to REF_01_REQ; Deferred REFs section added. |
| P1.2 | Refresh REF_13 from REF_01_REQ | Done | Overview, Boundaries, Delegation updated; "XWQuery integration (no circular ref)" section added; traceability to REF_01_REQ. |
| P1.3 | REF_15_API vs REF_01_REQ sec. 6 | Done | REF_15 updated with entry points from REF_01_REQ sec. 6 and traceability to REF_01_REQ. |
| P2.1–P2.2 | REF_12_IDEA / REF_14_DX | Deferred | Documented in REF_22 "Deferred REFs" with fill source (REF_01_REQ). |
| P2.3 | XWQuery note in REF_13 | Done | New subsection "XWQuery integration (no circular ref)" in REF_13. |
| P3.1 | **Dependency check (no circular ref)** | Verified | pyproject.toml: xwnode depends only on exonware-xwsystem, numpy, scipy, scikit-learn. No xwquery or xwdata dependency; xwdata/xwschema/xwaction/xwquery can depend on xwnode. **No circular ref.** |
| P3.2 | **REF_21_PLAN alignment** | Documented | REF_21_PLAN not present in xwnode/docs. REF_22 Traceability now states: "REF_21_PLAN not yet present; when added, align phases with M4/M5." |

---

*Produced per PROMPT_01_REQ_03_UPDATE (Step 2). Review scope: REF_01_REQ + code + tests + docs. Plan executed (items 1–6).*
