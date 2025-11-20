# Revert Plan to v0.0.1.28

**Goal:** Restore last known good state (v0.0.1.28)  
**Reason:** Wrong async architecture in attempted v0.0.1.30

---

## Files to Restore:

### **1. Recreate: `nodes/strategies/contracts.py`**
- Had INodeStrategy with optimizations
- Had async as abstract
- Had sync as concrete (asyncio.run wrappers)
- Had __slots__, __init_subclass__, caching

### **2. Revert: `nodes/strategies/base.py`**
- Remove wrong async wrappers (lines 238-373)
- Remove wrong sync abstract methods
- Restore: extends iNodeStrategy (parent package)

### **3. Revert: `contracts.py` (parent)**
- Keep old iNodeStrategy (lowercase)
- Remove unified INodeStrategy changes
- No NodeType enum here

### **4. Revert: All strategy imports (55 files)**
- Change back: `from ...contracts import` → `from .contracts import`

### **5. Revert: `base.py` (parent package)**
- Change: INodeStrategy → iNodeStrategy
- Change: IEdgeStrategy → iEdgeStrategy

### **6. Revert: `edges/strategies/base.py`**
- Change: IEdgeStrategy → iEdgeStrategy
- Remove get_mode/get_traits

### **7. Revert: `facade.py`**
- Keep version 0.0.1.30 (just metadata)
- get_mode/get_traits calls still there (will work after revert)

---

## Manual Restoration Required:

Since no git history and no backups exist, I'll need to:
1. Recreate nodes/strategies/contracts.py from v0.0.1.28 content
2. Fix all imports
3. Test thoroughly

**Ready to proceed?**

