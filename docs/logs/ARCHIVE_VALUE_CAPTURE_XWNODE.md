# Archive value capture — xwnode

**Date:** 07-Feb-2026  
**Purpose:** Record where value from `docs/_archive/` was moved (per GUIDE_41_DOCS). All added value preserved in REFs, logs, or summaries below; empty/redundant files removed from _archive.

---

## Destination map (by file)

| File | Destination |
|------|-------------|
| _archive_legacy_file | (empty/legacy placeholder — deleted) |
| ALL_ISSUES_RESOLVED.md | REF_22 status, logs/reviews |
| ALL_VERSIONS_COMPARISON.md | REF_54, logs/benchmarks; summary below |
| API_REFERENCE.md | REF_15_API |
| ARCHITECTURE_COMPARISON.md | REF_13_ARCH; summary below |
| ASYNC_FIRST_IMPLEMENTATION_SUCCESS.md | changes / logs/project; summary below |
| ASYNC_USAGE_EXAMPLES.md | GUIDE_01_USAGE, REF_15_API |
| AUDIT_PHASE1_FINDINGS.md | logs/reviews (REVIEW_20251011_000000_000_AUDIT_AND_SECURITY, etc.); summary below |
| BAAS_INTEGRATION.md | REF_13, REF_22; summary below |
| BACKUP_MANIFEST.md | (operational — summary below) |
| BENCHMARK_ANALYSIS_AND_IMPROVEMENTS.md | logs/benchmarks, REF_54 |
| BENCHMARK_BASELINE_RESULTS.md | logs/benchmarks, REF_54 |
| BENCHMARK_LRU_COMPARISON_FINDINGS.md | logs/benchmarks |
| BENCHMARK_RESULTS_10X.md | logs/benchmarks |
| benchmark_results_summary.md | logs/benchmarks |
| BENCHMARK_RESULTS_V2.md | logs/benchmarks |
| BENCHMARK_SETUP_SUMMARY.md | logs/benchmarks, REF_54 |
| CACHE_SYSTEM_IMPLEMENTATION_V0.0.1.29.md | REF_13, changes; summary below |
| COMPARISON_TABLE.md | logs/benchmarks; summary below |
| COMPETITOR_ANALYSIS.md | REF_12_IDEA / logs; summary below |
| CONSOLE_IMPLEMENTATION_SUMMARY.md | changes; summary below |
| COW_IMPACT_RESULTS.md | logs/benchmarks; summary below |
| DESIGN_PATTERNS.md | REF_13_ARCH |
| DEV_GUIDELINES_COMPLIANCE.md | REF_11_COMP, logs/reviews; summary below |
| DOCUMENTATION_REVIEW_FINDINGS.md | logs/reviews (REVIEW_20250101_000000_000_DOCUMENTATION_FINDINGS); summary below |
| DETAILED_BREAKDOWN.md, DETAILED_BREAKDOWN_10X.md | logs/benchmarks |
| ENHANCED_STRATEGY_SYSTEM.md | REF_13, REF_15; summary below |
| EXECUTIVE_SUMMARY.md | REF_22, logs/project |
| EXHAUSTIVE_SEARCH_RESULTS.md, EXHAUSTIVE_SEARCH_RESULTS_10X.md | logs/benchmarks |
| EXPLANATION.md | (context doc — summary below) |
| FINAL_* (IMPLEMENTATION_SUMMARY, OUTCOME, PERFORMANCE_REPORT, etc.) | REF_22, logs/project, logs/benchmarks; summary below |
| FULL_820_SWEEP_PREVIEW.md | logs/project; summary below |
| GRAPH_MANAGER_*.md | REF_13, REF_15; summary below |
| GUIDELINES_ARCHITECTURE_REFACTORING.md | REF_13, logs/reviews |
| IMPLEMENTATION_SUCCESS_SUMMARY.md | changes, REF_22 |
| INDIVIDUAL_STRATEGY_TESTS_PROGRESS.md | REF_51; summary below |
| INDUSTRY_FIRST_FINDINGS.md | logs/reviews; summary below |
| INSTALL_DEPS.md | GUIDE_01_USAGE (REF_22 already has install note) |
| MIGRATE_FEATURE_VERIFICATION.md | changes, REF_22 (migration verified) |
| MISSING_STRATEGIES_IMPLEMENTATION_PLAN.md | REF_13, changes; summary below |
| NEW_STRATEGIES_*.md | REF_13, changes; summary below |
| NODE_INHERITANCE_AUDIT.md | logs/reviews; summary below |
| OPERATIONS_STATUS.md | REF_22, logs/project |
| OPTIMIZATION_* (all) | REF_54, logs/benchmarks, changes; summary below |
| PERFORMANCE_* (all) | REF_54, logs/benchmarks; summary below |
| PRODUCTION_READINESS_*.md, PRODUCTION_QUALITY_CHECKLIST.md | REF_22 (link to logs/project/PROJECT_20251011_*), logs/reviews |
| PROJECT_PHASES.md | REF_22_PROJECT sec.  Historical phases |
| QUERY_OPERATIONS_ARCHITECTURE.md | REF_13_ARCH |
| QUICK_OPERATIONS_REFERENCE.md | REF_15_API, GUIDE_01 |
| README_*.md, RECOMMENDATIONS.md | INDEX, REF_22; summary below |
| REORGANIZATION_*, REVERT_*, REAL_EXECUTIVE_ENGINE_* | logs/project; summary below |
| REQUIREMENTS.md | REF_01_REQ, REF_22 |
| SAFE_UPDATE_STATUS.md, SECURITY_AUDIT_PLAN.md | logs/reviews, REF_35 |
| SESSION_* (all) | logs/project; summary below |
| SERIALIZATION_LIMITATIONS_RESOLVED.md | changes; summary below |
| START_HERE.md | INDEX, GUIDE_01 |
| STATISTICS_AND_SERIALIZATION_ANALYSIS.md | logs/benchmarks; summary below |
| STRATEGIES.md, STRATEGY_*.md | REF_13, REF_15; summary below |
| TEST_COVERAGE.md, TEST_STATUS_*, TEST_SUCCESS_* | REF_51_TEST; summary below |
| TUTORIAL_QUICK_START.md | GUIDE_01_USAGE |
| ULTIMATE_FINDINGS.md, THE_ULTIMATE_TRUTH.md, YOUR_FINAL_OUTCOME.md | logs/project; summary below |
| V028_*, V029_*, V030_*, V28B_* | REF_22 status, changes; summary below |
| WHAT_REMAINS_TODO.md | REF_22, REF_21_PLAN |
| XSYSTEM_INTEGRATION.md, XWSYSTEM_OPTIMIZATION_PLAN.md | REF_13; summary below |
| XWNODE_ENHANCEMENT_PLAN.md | REF_21_PLAN, REF_22 |
| XWNODE_XWQUERY_*.md | REF_22, changes; summary below |

---

## Summary by category (value preserved)

- **API / architecture:** API_REFERENCE → REF_15; ARCHITECTURE_COMPARISON, DESIGN_PATTERNS, QUERY_OPERATIONS_ARCHITECTURE → REF_13. Graph manager, strategy system, cache implementation, BaaS/XWQuery integration → REF_13/REF_15 scope.
- **Project / status:** PROJECT_PHASES → REF_22 sec.  Historical phases. Production readiness, milestones, install → REF_22 and GUIDE_01. Session summaries, final outcomes, reorganization, revert plans → logs/project; REF_22 points to PROJECT_20251011_000000_000_PRODUCTION_READINESS.
- **Reviews / audits:** AUDIT_PHASE1_FINDINGS, DOCUMENTATION_REVIEW_FINDINGS, NODE_INHERITANCE_AUDIT, PRODUCTION_READINESS_*, SECURITY_AUDIT_PLAN → logs/reviews (REVIEW_20251011_000000_000_AUDIT_AND_SECURITY, REVIEW_20250101_000000_000_DOCUMENTATION_FINDINGS, etc.). Findings: e.g. try/except imports (DEV_GUIDELINES), strategy doc gaps (LRU_CACHE), production checklist.
- **Benchmarks / performance:** All BENCHMARK_*, PERFORMANCE_*, COW_IMPACT, OPTIMIZATION_*, COMPARISON_TABLE, DETAILED_BREAKDOWN*, EXHAUSTIVE_SEARCH_*, STATISTICS_* → REF_54 and logs/benchmarks. Evidence: baseline, LRU comparison, 10X results, V2, V28 vs V30, optimization summaries.
- **Tests:** TEST_COVERAGE, TEST_STATUS_*, TEST_SUCCESS_*, INDIVIDUAL_STRATEGY_TESTS_PROGRESS → REF_51_TEST.
- **Implementation / migration:** MIGRATE_FEATURE_VERIFICATION → REF_22 (migration verified). NEW_STRATEGIES_*, MISSING_STRATEGIES_*, CACHE_SYSTEM_IMPLEMENTATION, SERIALIZATION_LIMITATIONS_RESOLVED, CONSOLE_IMPLEMENTATION, ASYNC_FIRST_IMPLEMENTATION → changes / REF_13.
- **Usage / install:** INSTALL_DEPS, TUTORIAL_QUICK_START, ASYNC_USAGE_EXAMPLES, QUICK_OPERATIONS_REFERENCE, START_HERE → GUIDE_01_USAGE, REF_15_API.
- **Other:** BACKUP_MANIFEST (operational manifest); EXPLANATION, REQUIREMENTS (context); COMPETITOR_ANALYSIS (REF_12_IDEA / strategy context). README_* → INDEX and REF_22.

---

*All added value is in REF documents or in logs (reviews, project, benchmarks). Empty or duplicate files removed from _archive.*
