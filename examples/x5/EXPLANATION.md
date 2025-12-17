# How JSON Utils Find Records

## Two Different Approaches

### V1 (Streaming) - Finds by **Property Value/Path**

**How it works:**
- Scans the file line-by-line from the beginning
- Uses a **match function** to find records by property values
- Returns the **first** record that matches

**Example:**
```python
from json_utils import stream_read, match_by_id

# Finds by property value (id field == "user_123")
user = stream_read("file.jsonl", match_by_id("id", "user_123"))

# Finds by any custom match function
def is_admin(obj):
    return obj.get("role") == "admin"

admin = stream_read("file.jsonl", is_admin)
```

**Characteristics:**
- ✅ Finds by **property value** (field values)
- ✅ Flexible matching (any custom match function)
- ❌ Must scan from start (O(n) worst case)
- ❌ Returns first match only

---

### V2 (Indexed) - Finds by **Line Number** OR **Property Value (ID)**

**Two modes:**

#### 1. Find by Line Number (Direct Access)

```python
from json_utils_indexed import indexed_get_by_line

# Finds by line number (0-based index)
record = indexed_get_by_line("file.jsonl", line_number=42)
```

**How it works:**
- Uses pre-built index with byte offsets
- Jumps directly to the line (O(1) access)
- No scanning needed

**Characteristics:**
- ✅ O(1) random access
- ✅ Fast for known line numbers
- ❌ Requires knowing the line number
- ❌ Requires index to be built first

#### 2. Find by Property Value (ID) - Using Index

```python
from json_utils_indexed import indexed_get_by_id

# Finds by property value (id field) using ID index
user = indexed_get_by_id("file.jsonl", id_value="user_123", id_field="id")
```

**How it works:**
- Uses pre-built **ID index** (id_value → line_number mapping)
- Looks up line number in ID index (O(1))
- Then uses `indexed_get_by_line` to get the record
- Falls back to streaming scan if ID not in index

**Characteristics:**
- ✅ O(1) lookup if ID is indexed
- ✅ Fast for ID-based lookups
- ✅ Falls back to streaming if ID not indexed
- ❌ Requires ID index to be built (with `id_field` parameter)

---

## Comparison Table

| Function | Finds By | Method | Speed | Requires Index |
|----------|---------|--------|-------|----------------|
| `stream_read()` | Property value | Linear scan | O(n) | No |
| `indexed_get_by_line()` | Line number | Direct seek | O(1) | Yes |
| `indexed_get_by_id()` | Property value (ID) | ID index lookup | O(1) | Yes (ID index) |
| `get_page()` | Line numbers | Direct seek | O(page_size) | Yes |

---

## Path Extraction

All functions support **path extraction** to get specific fields:

```python
# Get full record
user = stream_read("file.jsonl", match_by_id("id", "user_123"))

# Get only email field (path extraction)
email = stream_read("file.jsonl", match_by_id("id", "user_123"), path=["email"])

# Get nested field
likes = stream_read("file.jsonl", match_by_id("id", "post_456"), path=["likes_count"])
```

**Path extraction:**
- Works with both V1 and V2
- Extracts specific fields without loading full object
- Supports nested paths: `["user", "profile", "email"]`
- Supports array indices: `["tags", 0]` (first tag)

---

## Summary

- **V1 (Streaming)**: Finds by **property value** using match functions (flexible, but scans)
- **V2 (Indexed)**: Finds by **line number** (direct) OR **property value (ID)** (using index)
- **Path extraction**: Both support extracting specific fields/paths from matched records

The key difference:
- V1: **"Find the record where id='user_123'"** (scans until found)
- V2: **"Get record at line 42"** OR **"Find id='user_123' using index"** (direct access)

