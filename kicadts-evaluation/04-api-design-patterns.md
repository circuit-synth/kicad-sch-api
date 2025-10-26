# API Design Patterns Comparison

## Overall API Philosophy

### kicadts: Fluent, Object-Oriented Interface
```typescript
// Fluent, chainable API with declarative style
const schematic = new KicadSch()
  .setVersion("20230620")
  .setPaper("A4")
  .addSymbol({
    lib_id: "Device:R",
    reference: "R1",
    value: "10k",
    at: [100, 100, 0]
  })
  .addWire({
    start: [100, 110],
    end: [150, 110]
  });

// Consistent getString() interface across all elements
const output = schematic.getString();
```

**Design Principles:**
- **Fluent Interface**: Method chaining for intuitive construction
- **Uniform API**: Every element has consistent interface (`getString()`)
- **Declarative**: Describe what you want, not how to build it
- **Immutable-friendly**: Methods often return new instances

### kicad-sch-api: Collection-Based, Explicit Operations
```python
# Explicit, step-by-step construction with collections
sch = ksa.create_schematic('My Circuit')
sch.set_version_info("20230620", "eeschema", "9.0")
sch.set_paper_size("A4")

# Collection-based component management
r1 = sch.components.add('Device:R', 'R1', '10k', (100, 100))
r1.footprint = 'Resistor_SMD:R_0603_1608Metric'

# Explicit wire creation
wire_uuid = sch.add_wire((100, 110), (150, 110))

# Explicit save operation
sch.save('circuit.kicad_sch')
```

**Design Principles:**
- **Explicit Operations**: Clear, named methods for each action
- **Collection Management**: Specialized collections for different element types
- **Stateful Objects**: Objects maintain and track their state
- **Professional Workflow**: Validation, error handling, performance tracking

## Component Creation Patterns

### kicadts: Multiple Creation Strategies
```typescript
// Strategy 1: Constructor-based
const resistor = new SchematicSymbol({
  lib_id: "Device:R",
  reference: "R1",
  value: "10k",
  at: [100, 100, 0]
});

// Strategy 2: Factory methods
const capacitor = SchematicSymbol.create("Device:C", "C1", "100nF");

// Strategy 3: Fluent builder
const inductor = new SchematicSymbol()
  .setLibId("Device:L")
  .setReference("L1")
  .setValue("10uH")
  .setPosition([200, 100, 0]);

// Strategy 4: Array-based configuration
const components = [
  ["Device:R", "R1", "10k", [100, 100]],
  ["Device:C", "C1", "100nF", [200, 100]]
].map(([lib_id, ref, val, pos]) => new SchematicSymbol({lib_id, reference: ref, value: val, at: pos}));
```

**Benefits:**
- **Flexibility**: Multiple ways to create components
- **Developer Choice**: Use the pattern that fits your workflow
- **Type Safety**: TypeScript ensures parameter correctness
- **IDE Support**: Excellent autocomplete and validation

### kicad-sch-api: Collection-Managed Creation
```python
# Primary pattern: Collection-based creation with validation
r1 = sch.components.add('Device:R', 'R1', '10k', (100, 100))

# Enhanced with property assignment
r1.footprint = 'Resistor_SMD:R_0603_1608Metric'
r1.set_property('MPN', 'RC0603FR-0710KL')

# Bulk operations for efficiency
components = sch.components.bulk_add([
    ('Device:R', 'R1', '10k', (100, 100)),
    ('Device:C', 'C1', '100nF', (200, 100)),
])

# Professional features: validation and error collection
try:
    r1 = sch.components.add('Invalid:Part', 'R1', '10k', (100, 100))
except ValidationError as e:
    print(f"Component creation failed: {e}")

# Performance optimization: bulk updates
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)
```

**Benefits:**
- **Performance**: Optimized for bulk operations
- **Validation**: Comprehensive validation at creation time
- **Consistency**: Uniform component management
- **Professional Features**: Error collection, statistics, caching

## Property Management Approaches

### kicadts: Object Property Interface
```typescript
interface ComponentProperties {
  Reference: PropertyValue;
  Value: PropertyValue;
  Footprint?: PropertyValue;
  Datasheet?: PropertyValue;
  Description?: PropertyValue;
  [key: string]: PropertyValue | undefined;  // Custom properties
}

class SchematicSymbol {
  private properties: ComponentProperties;

  setProperty(name: string, value: string, options?: PropertyOptions) {
    this.properties[name] = {
      value,
      at: options?.position || [0, 0, 0],
      effects: options?.effects || defaultEffects
    };
  }

  getProperty(name: string): PropertyValue | undefined {
    return this.properties[name];
  }
}
```

**Characteristics:**
- **Type-Safe**: Properties are strongly typed
- **Consistent Interface**: Standard getter/setter pattern
- **Flexible**: Support for custom properties
- **IDE-Friendly**: Autocomplete for known properties

### kicad-sch-api: Dynamic Property System
```python
class SchematicSymbol:
    def __init__(self, **kwargs):
        self._data = ComponentData(**kwargs)
        self._properties = {}

    @property
    def footprint(self) -> Optional[str]:
        """Get/set footprint with validation."""
        return self.get_property('Footprint')

    @footprint.setter
    def footprint(self, value: str):
        self.set_property('Footprint', value)

    def set_property(self, name: str, value: str, **options):
        """Set property with comprehensive validation."""
        # Validation, position calculation, format preservation
        validated_value = self._validate_property(name, value)
        self._properties[name] = validated_value

    def get_property(self, name: str, default=None):
        """Get property with fallback."""
        return self._properties.get(name, default)
```

**Characteristics:**
- **Validation**: Properties validated at assignment time
- **Pythonic**: Uses property decorators for natural access
- **Flexible**: Dynamic property system supports any KiCAD property
- **Professional**: Error collection and validation reporting

## Wire and Connection Management

### kicadts: Direct Wire Objects
```typescript
class Wire {
  private points: Point[];
  private stroke: StrokeProperties;

  constructor(start: Point, end: Point, options?: WireOptions) {
    this.points = [start, end];
    this.stroke = options?.stroke || defaultStroke;
  }

  addPoint(point: Point): Wire {
    return new Wire([...this.points, point]);
  }

  getString(): string {
    return `(wire (pts ${this.points.map(p => `(xy ${p.x} ${p.y})`).join(' ')}))`;
  }
}

// Usage
const wire = new Wire([100, 100], [200, 100]);
const polyWire = wire.addPoint([200, 150]).addPoint([100, 150]);
```

**Benefits:**
- **Simple**: Direct object manipulation
- **Immutable**: Operations return new instances
- **Chainable**: Fluent interface for complex routing

### kicad-sch-api: Collection-Based Wire Management
```python
class WireCollection:
    def add(self, start: Point, end: Point, **options) -> str:
        """Add wire with validation and routing."""
        wire = Wire(
            uuid=str(uuid.uuid4()),
            points=[start, end],
            wire_type=options.get('wire_type', WireType.WIRE)
        )
        self._wires.append(wire)
        return wire.uuid

    def auto_route_pins(self, comp1_ref: str, pin1: str, comp2_ref: str, pin2: str,
                       routing_mode: str = "direct") -> Optional[str]:
        """Intelligent routing between component pins."""
        # Advanced routing algorithms with obstacle avoidance

# High-level connection methods
wire_uuid = sch.add_wire((100, 100), (200, 100))
sch.connect_pins_with_wire('R1', '1', 'R2', '2')
sch.auto_route_pins('R1', '1', 'R2', '2', routing_mode='manhattan')
```

**Benefits:**
- **Intelligent Routing**: Built-in routing algorithms
- **Pin-Aware**: Direct pin-to-pin connections
- **Professional**: Obstacle avoidance and grid snapping
- **Validation**: Connection validation and error reporting

## Error Handling Patterns

### kicadts: Exception-Based with TypeScript Safety
```typescript
class KicadSchematicError extends Error {
  constructor(message: string, public position?: Position) {
    super(message);
    this.name = 'KicadSchematicError';
  }
}

class SchematicSymbol {
  setReference(reference: string): void {
    if (!this.isValidReference(reference)) {
      throw new KicadSchematicError(
        `Invalid reference: ${reference}`,
        this.position
      );
    }
    this.properties.Reference.value = reference;
  }

  private isValidReference(ref: string): boolean {
    return /^[A-Z]+[0-9]*$/.test(ref);
  }
}

// Usage with type safety
try {
  component.setReference("Invalid123!");
} catch (error) {
  if (error instanceof KicadSchematicError) {
    console.error(`Error at ${error.position}: ${error.message}`);
  }
}
```

### kicad-sch-api: Professional Validation Framework
```python
@dataclass
class ValidationIssue:
    level: ValidationLevel
    message: str
    element_type: str
    element_id: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)

class SchematicValidator:
    def validate_component(self, component: SchematicSymbol) -> List[ValidationIssue]:
        """Comprehensive component validation."""
        issues = []

        # Reference validation
        if not self._is_valid_reference(component.reference):
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Invalid reference format: {component.reference}",
                element_type="component",
                element_id=component.uuid,
                suggestions=["Use format like R1, C1, U1"]
            ))

        return issues

# Usage with issue collection
issues = sch.validate()
errors = [issue for issue in issues if issue.level == ValidationLevel.ERROR]
if errors:
    for error in errors:
        print(f"ERROR: {error.message}")
        if error.suggestions:
            print(f"  Suggestions: {', '.join(error.suggestions)}")
```

## Performance and Scalability Patterns

### kicadts: Object-Oriented Overhead
```typescript
// Each element is a full object instance
class SchematicSymbol {
  private properties: Map<string, PropertyValue>;
  private pins: Map<string, Pin>;
  private graphics: GraphicsElement[];

  // Methods for each element
  getString(): string { /* generate S-expression */ }
  validate(): ValidationResult { /* validate element */ }
  clone(): SchematicSymbol { /* deep copy */ }
}

// Memory overhead: Object instance + methods + properties per component
// Good for: Small to medium schematics (< 500 components)
// Challenging for: Large professional schematics (1000+ components)
```

### kicad-sch-api: Collection-Optimized Performance
```python
class ComponentCollection:
    def __init__(self, components: List[SchematicSymbol]):
        self._components = components
        self._index_by_reference = {comp.reference: comp for comp in components}
        self._index_by_lib_id = defaultdict(list)
        for comp in components:
            self._index_by_lib_id[comp.lib_id].append(comp)

    def bulk_update(self, criteria: Dict, updates: Dict) -> int:
        """Optimized bulk operations."""
        count = 0
        for component in self._filter_by_criteria(criteria):
            self._apply_updates(component, updates)
            count += 1
        return count

    def get_statistics(self) -> Dict[str, Any]:
        """Performance analytics."""
        return {
            "component_count": len(self._components),
            "unique_lib_ids": len(self._index_by_lib_id),
            "memory_usage": self._calculate_memory_usage()
        }
```

## API Documentation and Developer Experience

### kicadts: TypeScript Self-Documentation
```typescript
/**
 * Create a schematic symbol component
 * @param lib_id - Library identifier (e.g., "Device:R")
 * @param reference - Component reference (e.g., "R1")
 * @param value - Component value (e.g., "10k")
 * @param position - Position [x, y, rotation] in mm
 */
interface SymbolOptions {
  lib_id: string;
  reference: string;
  value: string;
  position: [number, number, number];
  unit?: number;
  exclude_from_sim?: boolean;
  in_bom?: boolean;
  on_board?: boolean;
  properties?: Record<string, PropertyValue>;
}

class SchematicSymbol {
  constructor(options: SymbolOptions) {
    // TypeScript provides compile-time validation
    // IDE provides autocomplete and type checking
  }
}
```

### kicad-sch-api: Professional Documentation with Examples
```python
def add_component(
    self,
    lib_id: str,
    reference: str,
    value: str,
    position: Union[Point, Tuple[float, float]],
    *,
    rotation: float = 0.0,
    unit: int = 1,
    exclude_from_sim: bool = False,
    in_bom: bool = True,
    on_board: bool = True,
    properties: Optional[Dict[str, str]] = None
) -> SchematicSymbol:
    """
    Add a component to the schematic.

    Args:
        lib_id: Component library identifier (e.g., 'Device:R')
        reference: Component reference designator (e.g., 'R1')
        value: Component value (e.g., '10k', '100nF')
        position: Component position as (x, y) coordinates in mm
        rotation: Rotation angle in degrees (default: 0.0)
        unit: Unit number for multi-unit components (default: 1)
        exclude_from_sim: Exclude from simulation (default: False)
        in_bom: Include in bill of materials (default: True)
        on_board: Include on PCB (default: True)
        properties: Additional component properties

    Returns:
        Created SchematicSymbol object

    Raises:
        ValidationError: If component parameters are invalid
        LibraryError: If lib_id is not found in symbol libraries

    Example:
        >>> resistor = sch.components.add('Device:R', 'R1', '10k', (100, 100))
        >>> resistor.footprint = 'Resistor_SMD:R_0603_1608Metric'
        >>> resistor.set_property('Tolerance', '1%')
    """
```

## Recommendations for kicad-sch-api

### Adopt from kicadts
1. **Fluent Interface Options**: Add chainable methods for common operations
2. **Consistent Method Naming**: Adopt consistent `get`/`set` patterns
3. **Type Hints Enhancement**: Improve type safety with better annotations
4. **Multiple Creation Patterns**: Offer both explicit and fluent interfaces

### Maintain kicad-sch-api Strengths
1. **Collection Performance**: Keep optimized bulk operations
2. **Professional Validation**: Maintain comprehensive error handling
3. **Format Preservation**: Continue exact KiCAD compatibility
4. **Python Integration**: Leverage Python ecosystem strengths

### Implementation Examples
```python
# Enhanced fluent interface (optional)
class FluentSchematic(Schematic):
    def add_resistor(self, reference: str, value: str, position: Point) -> 'FluentSchematic':
        """Fluent interface for resistor creation."""
        self.components.add('Device:R', reference, value, position)
        return self

    def add_capacitor(self, reference: str, value: str, position: Point) -> 'FluentSchematic':
        """Fluent interface for capacitor creation."""
        self.components.add('Device:C', reference, value, position)
        return self

# Usage
circuit = (FluentSchematic.create('My Circuit')
          .add_resistor('R1', '10k', (100, 100))
          .add_capacitor('C1', '100nF', (200, 100))
          .save('circuit.kicad_sch'))

# Enhanced component creation with multiple patterns
class ComponentCollection:
    def add_from_dict(self, component_dict: Dict) -> SchematicSymbol:
        """Create component from dictionary (kicadts-style)."""
        return self.add(**component_dict)

    def add_bulk_from_list(self, component_list: List[Tuple]) -> List[SchematicSymbol]:
        """Create multiple components from tuple list."""
        return [self.add(*args) for args in component_list]
```

## Conclusion

Both APIs have distinct advantages:

**kicadts excels in:**
- Developer experience with TypeScript
- Intuitive fluent interfaces
- Consistent object-oriented patterns
- Excellent IDE support

**kicad-sch-api excels in:**
- Professional validation framework
- Performance with large schematics
- Comprehensive error handling
- Python ecosystem integration

The optimal approach would combine kicadts' intuitive API patterns with kicad-sch-api's professional features and performance optimizations.