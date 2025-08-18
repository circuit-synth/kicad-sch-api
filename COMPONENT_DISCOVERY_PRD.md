# PRD: Component Discovery Tools for KiCAD-Sch-API MCP Server

## Executive Summary

This PRD outlines the development of component discovery tools that enable AI agents to search, browse, and validate KiCAD symbol libraries and footprint libraries. This is a critical missing piece that makes the MCP server practical for real AI-driven schematic creation.

## Problem Statement

**Current Issue**: AI agents using the MCP server must guess component names and footprints:
- ❌ Guessing lib_ids: `"Device:R"` vs `"Resistor:R"` vs `"Components:Resistor"`
- ❌ Guessing footprints: `"Resistor_SMD:R_0603_1608Metric"` vs `"R_0603"` vs `"SMD_0603"`
- ❌ No way to discover what libraries or components exist
- ❌ No validation before attempting to add components

**Impact**: 
- High failure rate for AI-generated schematics
- Poor user experience with trial-and-error component naming
- Limited practical utility of the MCP server

## Product Vision

Enable AI agents to intelligently discover and select appropriate KiCAD components and footprints through comprehensive search and browsing tools, making AI-driven schematic creation reliable and professional.

## Target Users

**Primary Users:**
- AI agents (Claude, GPT, etc.) creating schematics through MCP
- Circuit designers using AI assistance for component selection
- Automated circuit generation systems

**Secondary Users:**
- Educational tools teaching component selection
- Circuit design validation systems
- Component library management tools

## Goals & Success Metrics

### Goals
- **G1**: AI agents can discover available components without guessing
- **G2**: Provide intelligent component suggestions for common circuit patterns
- **G3**: Enable validation of components before adding to schematics
- **G4**: Leverage existing kicad-sch-api symbol cache system

### Success Metrics
- **M1**: 95%+ success rate for AI component additions (vs current ~30%)
- **M2**: Sub-500ms response time for component searches
- **M3**: AI can find appropriate footprints for 90% of common components
- **M4**: Zero failed component additions due to invalid lib_ids

## Technical Requirements

### Core Discovery Tools

#### 1. **Component Search & Discovery**
```python
@mcp.tool()
def search_components(
    query: str, 
    library: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """Search for components across KiCAD symbol libraries"""
    
@mcp.tool()
def get_component_details(lib_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific component"""
    
@mcp.tool()
def suggest_components(component_type: str) -> Dict[str, Any]:
    """Get intelligent suggestions for component types (resistor, capacitor, etc.)"""
```

#### 2. **Library Browsing**
```python
@mcp.tool()
def list_libraries() -> Dict[str, Any]:
    """List all available KiCAD symbol libraries"""
    
@mcp.tool()
def browse_library(library_name: str, limit: int = 50) -> Dict[str, Any]:
    """Browse components in a specific library"""
    
@mcp.tool()
def get_library_stats(library_name: str) -> Dict[str, Any]:
    """Get statistics about a library (component count, categories, etc.)"""
```

#### 3. **Footprint Discovery**
```python
@mcp.tool()
def search_footprints(
    component_type: str,
    package: Optional[str] = None,
    size: Optional[str] = None
) -> Dict[str, Any]:
    """Search for appropriate footprints for component types"""
    
@mcp.tool()
def validate_footprint(footprint_name: str) -> Dict[str, Any]:
    """Validate that a footprint exists in KiCAD libraries"""
    
@mcp.tool()
def suggest_footprints(lib_id: str) -> Dict[str, Any]:
    """Suggest appropriate footprints for a component"""
```

#### 4. **Validation & Verification**
```python
@mcp.tool()
def validate_component_combination(
    lib_id: str, 
    footprint: str
) -> Dict[str, Any]:
    """Validate that component and footprint are compatible"""
    
@mcp.tool()
def check_component_exists(lib_id: str) -> Dict[str, Any]:
    """Quick check if component exists before adding to schematic"""
```

### Resource Providers

#### 1. **Common Components**
```python
@mcp.resource("components://resistors")
def get_common_resistors() -> str:
    """List of common resistor components with lib_ids and footprints"""
    
@mcp.resource("components://capacitors")
def get_common_capacitors() -> str:
    """List of common capacitor components with lib_ids and footprints"""
    
@mcp.resource("components://integrated-circuits")
def get_common_ics() -> str:
    """List of common IC components with lib_ids and footprints"""
```

#### 2. **Library Information**
```python
@mcp.resource("libraries://all")
def get_all_libraries() -> str:
    """Complete list of available symbol libraries"""
    
@mcp.resource("footprints://packages")
def get_footprint_packages() -> str:
    """Available footprint packages (0603, 0805, QFN, etc.)"""
```

## Architecture & Implementation

### Integration with Existing System

**Leverage Current Infrastructure:**
- Use existing `SymbolLibraryCache` from `kicad_sch_api.library.cache`
- Extend existing symbol parsing in `kicad_sch_api.core.parser`
- Build on proven symbol discovery in `get_symbol_cache()`

**New Module Structure:**
```
kicad_sch_api/
├── discovery/
│   ├── __init__.py
│   ├── component_search.py    # Component search engine
│   ├── footprint_discovery.py # Footprint search and validation
│   ├── library_browser.py     # Library browsing tools
│   └── suggestion_engine.py   # Smart component suggestions
├── mcp/
│   ├── server.py             # Enhanced with discovery tools
│   └── discovery_tools.py    # MCP tool wrappers
```

### Search Implementation Strategy

**Symbol Library Parsing:**
- Parse all `.kicad_sym` files in KiCAD installation
- Extract component names, descriptions, pin information
- Build searchable index with fuzzy matching capabilities
- Cache results for performance

**Footprint Library Integration:**
- Parse footprint libraries (`.pretty` directories)
- Match footprints to component categories
- Provide size/package recommendations

## Circuit-Synth Integration Discovery

**Found Existing Search Infrastructure in Circuit-Synth:**
- ✅ `search_engine.py` - Advanced schematic search with multi-criteria matching
- ✅ `fast_search.py` - Optimized component search with caching patterns  
- ✅ `library_sourcing/cache.py` - Professional caching system with TTL
- ✅ `ComponentValueParser` - Handles component values (10k, 4.7µF, etc.)
- ✅ Proven search patterns: exact/contains/regex/wildcard matching

**Key Patterns to Adopt:**
- **Multi-field search**: Search across name, description, properties simultaneously
- **Intelligent caching**: File-based cache with expiration and invalidation
- **Structured results**: Rich metadata for LLM consumption
- **Performance optimization**: Lazy loading with index building

## Key Design Questions ✅ **UPDATED WITH RESEARCH**

### 1. **Search Algorithm Strategy** 
**Your Decision**: Multi-field search leveraging circuit-synth patterns
- ✅ **Adopted**: Multi-criteria search (name + description + properties)
- **Implementation**: Use circuit-synth `SearchEngine` patterns with `MatchType` enum
- **Performance**: ~10-15ms response time based on circuit-synth benchmarks

**Search Techniques Comparison:**
- **String Matching**: ~1ms, exact matches only - good for known components
- **Fuzzy Search**: ~10ms, handles typos - good for "STM32G4" → "STM32G401"
- **Multi-Field**: ~15ms, comprehensive - searches name+description+properties
- **Semantic**: ~100ms+, requires ML - understands "regulator" → "LM7805"

**Recommendation**: Start with multi-field, add fuzzy later

### 2. **Library Caching Strategy** ✅ **DECIDED**
**Your Decision**: Lazy loading with caching after first load
- ✅ **Adopted**: Circuit-synth `LibraryCache` pattern with TTL expiration
- **Implementation**: Build index on first search, cache to `~/.kicad-sch-api/cache/`
- **Cache Duration**: 24 hours (libraries don't change frequently)
- **Update Detection**: File modification time checking

**Benefits**: Fast startup, cached searches, automatic cache invalidation

### 3. **Search Result Format** ✅ **DECIDED** 
**Your Decision**: Structured lists for optimal LLM consumption
- ✅ **Format**: JSON objects with lib_id, description, category, pins, footprints
- **Based on**: Circuit-synth `FastSearchResult` patterns + LLM optimization research
- **Include**: Usage context and common footprint recommendations

**Optimal LLM Format**:
```json
{
  "success": true,
  "results": [
    {
      "lib_id": "Device:R",
      "name": "R", 
      "description": "Resistor",
      "category": "passive",
      "pins": 2,
      "common_footprints": [
        "Resistor_SMD:R_0603_1608Metric",
        "Resistor_SMD:R_0805_2012Metric"
      ],
      "usage_context": "Use R_0603 for <0.1W signals, R_0805 for 0.1-0.25W power"
    }
  ],
  "search_time_ms": 15,
  "total_found": 25
}
```

### 4. **Footprint Recommendation Intelligence**
**Question**: How smart should footprint suggestions be?
- **Option A**: List all possible footprints for component type
- **Option B**: Recommend based on component value/power rating
- **Option C**: Machine learning from existing successful designs
- **Option D**: Rule-based recommendations (0603 for <1W, etc.)

### 5. **Performance vs. Completeness Trade-off**
**Question**: How much library data should we index?
- **Option A**: Component names only (fast, limited utility)
- **Option B**: Names + descriptions (medium performance, good utility)
- **Option C**: Full component metadata (slow, comprehensive)
- **Option D**: Configurable depth based on use case

### 6. **Library Update Detection**
**Question**: How should we handle KiCAD library updates?
- **Option A**: Manual cache refresh command
- **Option B**: Automatic detection of library file changes
- **Option C**: Version-based update checking
- **Option D**: Time-based cache expiration

### 7. **AI Agent Guidance Strategy**
**Question**: How much guidance should we provide to AI agents?
- **Option A**: Raw search results (AI figures out usage)
- **Option B**: Usage examples in search results  
- **Option C**: Context-aware suggestions (based on current schematic)
- **Option D**: Step-by-step component selection guidance

**Example guidance levels:**
```
// Option A - Raw
"Device:R - Resistor"

// Option C - Context-aware  
"Device:R - Resistor. For your power supply schematic, consider 
R_0805 footprint for power resistors or R_0603 for signal resistors."

// Option D - Guided
"To add a resistor: 1) Use lib_id='Device:R' 2) Choose footprint: 
R_0603_1608Metric (for <0.1W) or R_0805_2012Metric (for 0.1-0.25W) 
3) Set appropriate value like '10k' or '1M'"
```

### 8. **Integration with Existing Symbol Cache** ✅ **DECIDED**
**Your Decision**: Search libraries, then use existing cache for symbols
- ✅ **Approach**: Separate search index + existing symbol cache
- **Implementation**: Build search index of lib_ids, use `SymbolLibraryCache` for symbol loading
- **Benefits**: Preserves existing format preservation, adds search capability

### 9. **Error Handling for Missing Components**
**Question**: How should we help AI agents when components aren't found?
- **Option A**: Simple "not found" message
- **Option B**: Suggest similar/alternative components
- **Option C**: Provide search tips and common alternatives
- **Option D**: Auto-correct common naming mistakes

### 10. **Development Priority** ✅ **DECIDED** 
**Your Decision**: Component symbol search first
- ✅ **Phase 1**: Basic component search in symbol libraries (immediate need)
- **Phase 2**: Footprint discovery and validation tools  
- **Phase 3**: Smart suggestions and usage context
- **Phase 4**: Advanced filtering and recommendation engine

## Technical Implementation Considerations

### **Existing Assets to Leverage:**
- `SymbolLibraryCache` in `kicad_sch_api.library.cache`
- Symbol discovery in `/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols`
- Existing library loading and parsing logic

### **New Components Needed:**
- Search indexing system for fast component lookup
- Footprint library scanning and parsing
- Fuzzy/semantic search algorithms
- Component categorization and tagging system

### **Performance Requirements:**
- Search response time: <200ms for interactive AI use
- Library scanning: Complete index rebuild <10 seconds
- Memory usage: Reasonable index size for common libraries
- Incremental updates: Fast detection of library changes

## Success Criteria

**Immediate Success:**
- AI agents can reliably find common components (resistors, capacitors, ICs)
- Footprint selection success rate >90% for standard packages
- Search results help AI understand component usage

**Long-term Success:**
- AI generates professional schematics with appropriate component choices
- Users trust AI component selection without manual verification
- Discovery tools become standard reference for circuit design automation

## Additional Design Questions for Final Implementation

Based on circuit-synth integration findings, here are the specific questions to finalize the design:

### 11. **Symbol Library Parsing Strategy** ✅ **CURRENT STATE ANALYSIS**
**Current Implementation**: We already parse comprehensive symbol data:
- ✅ **Symbol names, descriptions, keywords, datasheet URLs**
- ✅ **Pin definitions with positions, types, and shapes** 
- ✅ **Graphic elements and bounding boxes**
- ✅ **Raw KiCAD data for format preservation**
- ✅ **Performance metrics and access tracking**

**Current Data Available for Search:**
```python
class SymbolDefinition:
    lib_id: str              # "Device:R"
    name: str               # "R" 
    description: str        # "Resistor"
    keywords: str           # Search keywords
    reference_prefix: str   # "R"
    pins: List[SchematicPin] # Pin metadata
    raw_kicad_data: Any     # Complete symbol data
```

**Question**: Should we add search indexing to existing `SymbolDefinition` or create separate search index?
- **Option A**: Extend `SymbolDefinition` with search metadata
- **Option B**: Create separate lightweight search index pointing to symbols
- **Option C**: Build search index from existing cached `SymbolDefinition` objects

### 12. **Search Index Storage** ✅ **ANALYSIS FOR MULTI-SOURCE LIBRARIES**
**Context**: 224 symbol libraries (210MB), future sources (DigiKey, SnapEDA, custom)

**Storage Options Analysis:**

**Option A: In-Memory Only**
- ✅ Pros: Fastest access (~1ms), simple implementation
- ❌ Cons: Lost on restart, high memory usage (210MB+ loaded), no persistence
- **Multi-source**: Each source needs separate in-memory indexes

**Option B: JSON Files (Circuit-Synth Pattern)**
- ✅ Pros: Human readable, existing patterns, TTL support, ~50MB compressed
- ✅ Pros: Separate files per source, easy backup/sync
- ❌ Cons: Slower than SQLite for complex queries, JSON parsing overhead
- **Multi-source**: Natural fit - separate JSON per source

**Option C: SQLite Database**  
- ✅ Pros: Fast complex queries, efficient storage, ACID transactions
- ✅ Pros: Easy multi-source support with source_id column
- ❌ Cons: Additional dependency, more complex, harder to debug
- **Multi-source**: Excellent - single DB with source tracking

**Option D: Extend Existing `SymbolLibraryCache`**
- ✅ Pros: Leverages existing system, consistent with current architecture
- ❌ Cons: Existing cache is symbol-loading focused, not search optimized
- **Multi-source**: Would need significant refactoring

**Recommendation for Multi-Source Future**: **SQLite** for structured queries across sources

### 13. **Component Categorization**
**Question**: How should we categorize components for better AI understanding?
- **Option A**: Use KiCAD library names as categories (`Device`, `Connector`, etc.)
- **Option B**: Create semantic categories (`passive`, `active`, `power`, `digital`)
- **Option C**: Multi-level categorization (type → subtype → variant)
- **Option D**: Learn from circuit-synth component classification patterns

### 14. **Footprint Library Integration** ❓ **YOUR INPUT NEEDED**
**Your Concern**: "Wanted schematics only but maybe need some .pretty parsing"

**Context**: 146 footprint libraries, essential for AI component selection

**Options for Footprint Handling:**

**Option A: No Footprint Scanning (Schematic-Only)**
- ✅ Pros: Simple, focused on schematics, faster implementation
- ❌ Cons: AI still guesses footprints, high failure rate
- **Reality**: AI needs valid footprints for `add_component()` to work

**Option B: Basic Footprint Name Scanning**
- **Implementation**: Scan `.pretty` folder names, list available footprints
- **Pros**: Enables footprint validation, moderate complexity
- **Cons**: No footprint metadata (size, pin count validation)

**Option C: Intelligent Component→Footprint Mapping**
- **Implementation**: Curated mappings like "Device:R" → ["R_0603", "R_0805", "R_1206"]
- **Pros**: Smart suggestions, no .pretty parsing needed
- **Cons**: Manual curation, limited to known mappings

**Option D: Hybrid - Mappings + Scanning**
- **Implementation**: Pre-defined mappings for common components + .pretty scanning for validation
- **Pros**: Best of both worlds
- **Cons**: Most complex

**Question**: Do you want to tackle footprint discovery now or leave it for later phase?

### 15. **Error Handling & Suggestions**
**Question**: How should we handle failed searches and provide suggestions?
- **Option A**: Return empty results with search tips
- **Option B**: Suggest similar components using fuzzy matching
- **Option C**: Provide category browsing when specific search fails
- **Option D**: Auto-correct common typos (STM32 → STM32F4, etc.)

### 16. **Performance vs. Completeness** ✅ **PACKAGING SIZE ANALYSIS**
**Current KiCAD Library Stats:**
- **224 symbol libraries** totaling **210MB** on disk
- **Device.kicad_sym alone**: 155,422 lines (most commonly used)
- **Current scan time**: ~0.04s for library discovery

**Pre-Indexed Package Size Options:**

**Option A: Core Libraries Only (Device, Connector, power)**
- **Size**: ~5-10MB compressed JSON index
- **Components**: ~2,000 most common components
- **PyPI Impact**: Minimal, acceptable package bloat
- **Coverage**: 80% of typical schematic needs

**Option B: All Standard KiCAD Libraries**  
- **Size**: ~50-100MB compressed index
- **Components**: ~15,000+ total components
- **PyPI Impact**: Significant package bloat, slower pip installs
- **Coverage**: 100% of KiCAD standard components

**Option C: No Pre-Indexing (First-Run Scan)**
- **Size**: 0MB package bloat
- **First scan time**: ~5-10 seconds to index all libraries
- **Subsequent**: Instant from cache
- **User experience**: One-time delay on first use

**Option D: Hybrid - Core Pre-Indexed + Extended On-Demand**
- **Size**: ~10MB for core, extended libraries scanned as needed
- **Best of both**: No bloat + comprehensive coverage
- **Implementation**: Ship with Device/Connector/power, scan others on first search

**Recommendation**: **Option D - Hybrid approach** for best user experience

### 17. **AI Agent Guidance Level** ✅ **DECIDED**
**Your Decision**: Provide infrastructure, not intelligence
- ✅ **Approach**: Supply structured data + basic context, let AI decide
- **Include**: Component properties, common footprints, basic usage notes
- **Avoid**: Design decisions, component selection logic, circuit analysis

**Example Context Level:**
```json
{
  "lib_id": "Device:R",
  "properties": {"pins": 2, "type": "passive"},
  "common_footprints": ["R_0603_1608Metric", "R_0805_2012Metric"],
  "context": "R_0603 for <0.1W, R_0805 for 0.1-0.25W"
}
```
**NOT**: "Use 10k resistor for voltage divider with this ratio..."

### 18. **Integration with Existing Tools** ✅ **DECIDED**
**Your Decision**: Incorporate into core MCP server (critical functionality)
- ✅ **Integration**: Add discovery tools directly to `kicad_sch_api/mcp/server.py`
- **New Tools**: `search_components()`, `list_libraries()`, `validate_component()`
- **Enhanced**: Improve `add_component()` error messages with suggestions
- **Architecture**: Discovery is fundamental infrastructure, not optional feature

**Implementation Pattern:**
```python
@mcp.tool()
def search_components(query: str, library: Optional[str] = None) -> Dict[str, Any]:
    """Search for components in KiCAD libraries - core MCP functionality"""

@mcp.tool() 
def add_component(lib_id: str, reference: str, value: str, position: tuple):
    """Enhanced with discovery-powered error messages"""
    try:
        # Existing add logic
    except ComponentNotFound:
        suggestions = search_components(lib_id.split(':')[1])  # Search by symbol name
        return {"success": False, "message": "Component not found", "suggestions": suggestions}
```

This feature will transform the MCP server from a "basic manipulation tool" into an "intelligent schematic design assistant" by providing the component knowledge that AI agents currently lack.