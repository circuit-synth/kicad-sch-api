# Discovery Module

Component search and indexing with SQLite backend.

## Overview

This module provides component discovery and search functionality using a SQLite-based search index for fast, efficient component lookup across libraries.

## Search Index (`search_index.py`)

### Purpose
Create and maintain a searchable index of components across multiple symbol libraries.

### Key Classes

#### SearchIndex
- **Purpose**: SQLite-based component search
- **Database**: `~/.kicad_sch_api/search_index.db`
- **Key Methods**:
  - `add_component()` - Index component
  - `search()` - Search indexed components
  - `search_by_name()` - Find by name
  - `search_by_property()` - Find by property
  - `rebuild_index()` - Rebuild from libraries
  - `clear_index()` - Clear all entries

### Database Schema

```sql
-- Components table
CREATE TABLE components (
    id INTEGER PRIMARY KEY,
    lib_id TEXT UNIQUE,          -- Device:R
    name TEXT,                    -- Resistor
    description TEXT,             -- "General resistor"
    keywords TEXT,                -- "R resistor ohm"
    category TEXT,                -- "Passive/Resistor"
    library TEXT,                 -- Device
    symbol TEXT,                  -- R
    footprints TEXT,              -- JSON array of footprints
    properties TEXT,              -- JSON properties
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Index for fast lookup
CREATE INDEX idx_lib_id ON components(lib_id);
CREATE INDEX idx_name ON components(name);
CREATE INDEX idx_category ON components(category);
```

### Search Capabilities

#### By Library ID
```python
index = SearchIndex()
result = index.search_by_name('Device:R')
```

#### By Name/Pattern
```python
# Find all resistors
results = index.search('resistor')

# Pattern search with wildcards
results = index.search('*ohm*')
```

#### By Category
```python
# Find passive components
results = index.search_by_property('category', 'Passive')

# Find resistors
results = index.search_by_property('category', 'Passive/Resistor')
```

#### By Keywords
```python
# Find components with specific keywords
results = index.search('high power resistor')
```

### Search Results

Each search returns list of ComponentInfo objects:

```python
@dataclass
class ComponentInfo:
    lib_id: str              # Device:R
    name: str                # Resistor
    description: str         # Component description
    keywords: str            # Search keywords
    category: str            # Component category
    footprints: List[str]   # Common footprints
    properties: Dict[str, str]  # Additional properties
```

### Index Maintenance

#### Rebuilding Index
```python
index = SearchIndex()

# Full rebuild from KiCAD libraries
index.rebuild_index()
```

#### Updating Entry
```python
# Update single component entry
index.add_component({
    'lib_id': 'Device:R',
    'name': 'Resistor',
    ...
})
```

#### Clearing Index
```python
# Clear all entries
index.clear_index()
```

### Integration with Symbol Cache

The search index complements the symbol cache:

```
User searches for component
    ↓
Search index returns matches (fast)
    ↓
Symbol cache provides detailed info (with caching)
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| First search | 100-500ms | Rebuilds index if needed |
| Subsequent search | 1-10ms | SQLite query |
| Rebuild index | 1-5s | Scans all libraries |
| Database size | 1-5MB | Depends on library count |

## Use Cases

### Component Selection
```python
# User searching for resistor
results = index.search('resistor 10k')

# Display options and let user pick
for result in results:
    print(f"{result.lib_id}: {result.description}")
```

### Auto-Complete
```python
# In IDE/tool, suggest completions
results = index.search('Device:')
suggestions = [r.lib_id for r in results]
```

### Library Management
```python
# What resistor values are available?
resistor_results = index.search('resistor')

# Find specific value
resistor_10k = [r for r in resistor_results
                if '10k' in r.name]
```

## Known Issues

1. **Index Staleness** - Index may be out of date if libraries change
2. **Search Performance** - Large libraries may have slow initial searches
3. **Memory Usage** - Index loaded entirely in memory for search
4. **Update Detection** - No automatic detection of library changes

## Implementation Notes

### SQLite Location
- **Default Path**: `~/.kicad_sch_api/search_index.db`
- **Environment Override**: Set `KICAD_SEARCH_INDEX` to override
- **Cleanup**: Delete database file to rebuild

### Thread Safety
- **Current Status**: NOT thread-safe
- **Recommendation**: Serialize access or add locks
- **Future**: Consider concurrent access patterns

### Query Examples

```python
# Complex search
index.search('resistor AND 10k AND SMD')

# Category search
index.search('category:Passive/Resistor')

# Footprint search
index.search('footprint:*0603*')
```

## Testing

Tests located in `../../tests/`:
- `test_search_index.py` - Index functionality
- `test_search_queries.py` - Query types
- Integration tests with real libraries

## Future Improvements

- [ ] Full-text search support
- [ ] Fuzzy matching
- [ ] Relevance ranking
- [ ] Advanced query syntax
- [ ] Search history/suggestions
- [ ] Thread-safe implementation
- [ ] Incremental index updates
- [ ] Distributed indexing

## References

- SQLite: https://www.sqlite.org/
- Search patterns: See `CODEBASE_ANALYSIS.md`
- Symbol library: See `library/cache.py`
