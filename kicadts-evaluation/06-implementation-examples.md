# Implementation Examples: Bridging kicadts and kicad-sch-api Approaches

## Overview
This document provides concrete implementation examples showing how to incorporate the best features of kicadts into kicad-sch-api while maintaining our core strengths.

## Enhanced Type Safety Implementation

### Current kicad-sch-api Approach
```python
def add_component(self, lib_id: str, reference: str, value: str, position) -> SchematicSymbol:
    # Basic type hints, limited validation
```

### Enhanced Approach (Inspired by kicadts TypeScript)
```python
from typing import TypedDict, Union, Literal, Unpack
from dataclasses import dataclass

# Define comprehensive type structures
class ComponentPosition(TypedDict):
    x: float
    y: float
    rotation: float

class ComponentOptions(TypedDict, total=False):
    unit: int
    exclude_from_sim: bool
    in_bom: bool
    on_board: bool
    properties: Dict[str, str]
    footprint: str
    datasheet: str

PinType = Literal["input", "output", "bidirectional", "tri_state", "passive", "unspecified", "power_in", "power_out", "open_collector", "open_emitter", "no_connect"]

@dataclass
class ValidationPosition:
    line: int
    column: int
    file_path: Optional[str] = None

# Enhanced component creation with comprehensive typing
class ComponentCollection:
    def add(
        self,
        lib_id: str,
        reference: str,
        value: str,
        position: Union[Point, Tuple[float, float], ComponentPosition],
        **options: Unpack[ComponentOptions]
    ) -> SchematicSymbol:
        """
        Add component with comprehensive type safety.

        Type safety benefits:
        - IDE autocomplete for all options
        - Compile-time validation of parameters
        - Clear documentation of expected types
        """
        # Implementation with enhanced validation
        validated_position = self._validate_position(position)
        validated_options = self._validate_options(options)

        return self._create_component(lib_id, reference, value, validated_position, validated_options)
```

## Fluent Interface Implementation

### Optional Fluent Interface (kicadts-inspired)
```python
class FluentSchematic:
    """Optional fluent interface wrapper for intuitive component creation."""

    def __init__(self, schematic: Schematic):
        self._schematic = schematic

    def add_resistor(
        self,
        reference: str,
        value: str,
        position: Union[Point, Tuple[float, float]],
        **options
    ) -> 'FluentSchematic':
        """Add resistor with fluent interface."""
        self._schematic.components.add('Device:R', reference, value, position, **options)
        return self

    def add_capacitor(
        self,
        reference: str,
        value: str,
        position: Union[Point, Tuple[float, float]],
        **options
    ) -> 'FluentSchematic':
        """Add capacitor with fluent interface."""
        self._schematic.components.add('Device:C', reference, value, position, **options)
        return self

    def add_ic(
        self,
        lib_id: str,
        reference: str,
        value: str,
        position: Union[Point, Tuple[float, float]],
        **options
    ) -> 'FluentSchematic':
        """Add IC with fluent interface."""
        self._schematic.components.add(lib_id, reference, value, position, **options)
        return self

    def connect_pins(
        self,
        comp1_ref: str,
        pin1: str,
        comp2_ref: str,
        pin2: str,
        routing: str = "direct"
    ) -> 'FluentSchematic':
        """Connect component pins with fluent interface."""
        self._schematic.auto_route_pins(comp1_ref, pin1, comp2_ref, pin2, routing_mode=routing)
        return self

    def save(self, file_path: str) -> Schematic:
        """Save and return original schematic object."""
        self._schematic.save(file_path)
        return self._schematic

# Usage example
circuit = (ksa.create_schematic('Voltage Divider')
          .fluent
          .add_resistor('R1', '10k', (100, 100))
          .add_resistor('R2', '10k', (100, 150))
          .connect_pins('R1', '2', 'R2', '1')
          .save('voltage_divider.kicad_sch'))
```

### Maintaining Collection Benefits
```python
class Schematic:
    @property
    def fluent(self) -> FluentSchematic:
        """Access fluent interface for intuitive operations."""
        return FluentSchematic(self)

    # Original collection-based interface remains for performance
    def bulk_operations_example(self):
        """Demonstrate maintaining performance-optimized operations."""
        # Bulk component creation (performance-optimized)
        component_specs = [
            ('Device:R', 'R1', '10k', (100, 100)),
            ('Device:R', 'R2', '20k', (200, 100)),
            ('Device:C', 'C1', '100nF', (150, 150))
        ]
        components = self.components.bulk_add(component_specs)

        # Bulk property updates (performance-optimized)
        self.components.bulk_update(
            criteria={'lib_id': 'Device:R'},
            updates={'properties': {'Tolerance': '1%'}}
        )

        return components
```

## Multiple Creation Patterns Implementation

### Dictionary-Based Creation (kicadts-style)
```python
class ComponentCollection:
    def add_from_dict(self, component_spec: Dict[str, Any]) -> SchematicSymbol:
        """Create component from dictionary specification (kicadts-inspired)."""
        required_fields = ['lib_id', 'reference', 'value', 'position']

        # Validate required fields
        missing = [field for field in required_fields if field not in component_spec]
        if missing:
            raise ValidationError(f"Missing required fields: {missing}")

        # Extract position
        position = component_spec['position']
        if isinstance(position, (list, tuple)) and len(position) >= 2:
            position = Point(position[0], position[1])

        # Extract optional parameters
        options = {k: v for k, v in component_spec.items()
                  if k not in required_fields}

        return self.add(
            lib_id=component_spec['lib_id'],
            reference=component_spec['reference'],
            value=component_spec['value'],
            position=position,
            **options
        )

    def add_bulk_from_specs(self, component_specs: List[Dict[str, Any]]) -> List[SchematicSymbol]:
        """Create multiple components from specification dictionaries."""
        return [self.add_from_dict(spec) for spec in component_specs]

# Usage examples demonstrating flexibility
sch = ksa.create_schematic('Multi-Pattern Example')

# Pattern 1: Traditional explicit creation
r1 = sch.components.add('Device:R', 'R1', '10k', (100, 100))

# Pattern 2: Dictionary-based creation (kicadts-style)
r2 = sch.components.add_from_dict({
    'lib_id': 'Device:R',
    'reference': 'R2',
    'value': '20k',
    'position': [200, 100],
    'rotation': 90,
    'properties': {'Tolerance': '1%'}
})

# Pattern 3: Bulk creation from specifications
components = sch.components.add_bulk_from_specs([
    {'lib_id': 'Device:C', 'reference': 'C1', 'value': '100nF', 'position': [150, 150]},
    {'lib_id': 'Device:L', 'reference': 'L1', 'value': '10uH', 'position': [250, 150]},
])

# Pattern 4: Fluent interface
sch.fluent.add_resistor('R3', '5k', (300, 100)).add_capacitor('C2', '47nF', (350, 100))
```

## Enhanced Error Reporting Implementation

### Position-Aware Error Handling (kicadts-inspired)
```python
@dataclass
class ParsePosition:
    line: int
    column: int
    character_offset: int
    file_path: Optional[str] = None

    def __str__(self) -> str:
        location = f"line {self.line}, column {self.column}"
        if self.file_path:
            location = f"{self.file_path}:{location}"
        return location

@dataclass
class ValidationIssue:
    level: ValidationLevel
    message: str
    element_type: str
    element_id: Optional[str] = None
    position: Optional[ParsePosition] = None
    suggestions: List[str] = field(default_factory=list)
    context: Optional[str] = None  # Additional context for debugging

    def __str__(self) -> str:
        result = f"{self.level.value.upper()}: {self.message}"
        if self.position:
            result = f"{self.position}: {result}"
        if self.suggestions:
            result += f"\n  Suggestions: {', '.join(self.suggestions)}"
        if self.context:
            result += f"\n  Context: {self.context}"
        return result

class EnhancedSExpressionParser(SExpressionParser):
    """Enhanced parser with position tracking and detailed error reporting."""

    def parse_with_positions(self, content: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Parse with detailed position tracking for enhanced error reporting."""
        self._line_offsets = self._calculate_line_offsets(content)
        self._file_path = file_path

        try:
            return self.parse_string(content)
        except Exception as e:
            # Enhance error with position information
            position = self._calculate_error_position(str(e), content)
            raise ValidationError(
                f"Parse error at {position}: {e}",
                position=position
            ) from e

    def _calculate_line_offsets(self, content: str) -> List[int]:
        """Calculate character offsets for each line for position tracking."""
        offsets = [0]
        for i, char in enumerate(content):
            if char == '\n':
                offsets.append(i + 1)
        return offsets

    def _calculate_error_position(self, error_msg: str, content: str) -> ParsePosition:
        """Calculate line/column position from error information."""
        # Implementation to extract position from error context
        # This would need to be adapted based on sexpdata error formats
        return ParsePosition(line=1, column=1, character_offset=0, file_path=self._file_path)

# Enhanced validation with detailed reporting
class ComponentValidator:
    """Enhanced component validation with detailed error reporting."""

    def validate_component(self, component: SchematicSymbol) -> List[ValidationIssue]:
        """Comprehensive component validation with detailed error reporting."""
        issues = []

        # Reference validation
        if not self._is_valid_reference(component.reference):
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Invalid reference format: '{component.reference}'",
                element_type="component",
                element_id=component.uuid,
                suggestions=[
                    "Use format like R1, C1, U1 (letter prefix + number)",
                    "Avoid special characters except numbers",
                    "Ensure reference is unique in schematic"
                ],
                context=f"Component at position {component.position}"
            ))

        # Value validation
        if not component.value or component.value.strip() == "":
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message=f"Component {component.reference} has empty value",
                element_type="component",
                element_id=component.uuid,
                suggestions=[
                    "Add meaningful value (e.g., '10k', '100nF', 'LM358')",
                    "Use '~' for components without specific values"
                ]
            ))

        # Footprint validation
        if not component.footprint:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                message=f"Component {component.reference} has no footprint assigned",
                element_type="component",
                element_id=component.uuid,
                suggestions=[
                    "Assign appropriate footprint for PCB layout",
                    "Use component.footprint = 'Library:Footprint_Name'"
                ]
            ))

        return issues
```

## Deterministic Output Mode Implementation

### Optional Clean Formatting (kicadts-inspired)
```python
from enum import Enum

class FormattingMode(Enum):
    PRESERVE_ORIGINAL = "preserve"    # Default - maintains exact formatting
    DETERMINISTIC_CLEAN = "clean"     # kicadts-style clean formatting
    MINIMAL_COMPACT = "compact"       # Space-optimized output

class DeterministicFormatter:
    """Clean, deterministic S-expression formatting inspired by kicadts."""

    def __init__(self, indent_size: int = 2):
        self.indent_size = indent_size

    def format_deterministic(self, sexp_data: Any, level: int = 0) -> str:
        """Generate clean, deterministic S-expression output."""
        if isinstance(sexp_data, list):
            if not sexp_data:
                return "()"

            # Format as single line for short lists
            if self._should_format_inline(sexp_data):
                inner = " ".join(self.format_deterministic(item, level) for item in sexp_data)
                return f"({inner})"

            # Format as multi-line for complex structures
            indent = " " * (level * self.indent_size)
            next_indent = " " * ((level + 1) * self.indent_size)

            result = f"({self.format_deterministic(sexp_data[0], level)}"
            for item in sexp_data[1:]:
                formatted_item = self.format_deterministic(item, level + 1)
                result += f"\n{next_indent}{formatted_item}"
            result += ")"

            return result

        elif isinstance(sexp_data, str):
            # Handle string quoting consistently
            if self._needs_quoting(sexp_data):
                return f'"{sexp_data}"'
            return sexp_data

        else:
            # Handle numbers, symbols, etc.
            return str(sexp_data)

    def _should_format_inline(self, sexp_list: List) -> bool:
        """Determine if list should be formatted on single line."""
        # Format inline for simple lists (position, effects, etc.)
        if len(sexp_list) <= 4 and all(not isinstance(item, list) for item in sexp_list[1:]):
            return True
        return False

    def _needs_quoting(self, s: str) -> bool:
        """Determine if string needs quoting."""
        return " " in s or any(char in s for char in "()\"\\")

class Schematic:
    def save(
        self,
        file_path: Optional[Union[str, Path]] = None,
        formatting: FormattingMode = FormattingMode.PRESERVE_ORIGINAL
    ):
        """Save with configurable formatting options."""
        # ... existing validation and setup code ...

        # Generate content based on formatting mode
        sexp_data = self._parser._schematic_data_to_sexp(self._data)

        if formatting == FormattingMode.DETERMINISTIC_CLEAN:
            formatter = DeterministicFormatter()
            content = formatter.format_deterministic(sexp_data)
        elif formatting == FormattingMode.MINIMAL_COMPACT:
            formatter = DeterministicFormatter(indent_size=1)
            content = formatter.format_deterministic(sexp_data)
        else:  # PRESERVE_ORIGINAL
            content = self._formatter.format_preserving_write(sexp_data, self._original_content)

        # ... existing file writing code ...

# Usage example
sch = ksa.create_schematic('Clean Output Example')
sch.components.add('Device:R', 'R1', '10k', (100, 100))

# Save with original formatting preservation (default)
sch.save('original_format.kicad_sch')

# Save with clean, deterministic formatting
sch.save('clean_format.kicad_sch', formatting=FormattingMode.DETERMINISTIC_CLEAN)

# Save with compact formatting
sch.save('compact_format.kicad_sch', formatting=FormattingMode.MINIMAL_COMPACT)
```

## Performance Benchmarking Implementation

### Benchmark Suite (Inspired by kicadts Testing)
```python
import time
import memory_profiler
from typing import Dict, Any, List
import matplotlib.pyplot as plt

class PerformanceBenchmark:
    """Performance benchmarking suite for comparing with other libraries."""

    def __init__(self):
        self.results = {}

    def benchmark_component_creation(self, counts: List[int] = None) -> Dict[str, Any]:
        """Benchmark component creation performance."""
        if counts is None:
            counts = [10, 50, 100, 500, 1000]

        results = {"counts": counts, "times": [], "memory_usage": []}

        for count in counts:
            # Measure time
            start_time = time.time()
            sch = ksa.create_schematic(f'Benchmark_{count}')

            for i in range(count):
                sch.components.add(
                    'Device:R',
                    f'R{i+1}',
                    f'{10*(i+1)}k',
                    (100 + (i % 10) * 20, 100 + (i // 10) * 20)
                )

            end_time = time.time()
            creation_time = end_time - start_time

            # Measure memory usage
            memory_usage = memory_profiler.memory_usage((lambda: None,))[0]

            results["times"].append(creation_time)
            results["memory_usage"].append(memory_usage)

            print(f"Created {count} components in {creation_time:.3f}s, Memory: {memory_usage:.1f}MB")

        return results

    def benchmark_parsing(self, file_sizes: List[str] = None) -> Dict[str, Any]:
        """Benchmark parsing performance with different file sizes."""
        if file_sizes is None:
            file_sizes = ["small", "medium", "large"]

        results = {"file_sizes": file_sizes, "parse_times": [], "save_times": []}

        for size in file_sizes:
            # Create test schematic of appropriate size
            component_count = {"small": 50, "medium": 200, "large": 1000}[size]
            test_file = f"benchmark_{size}.kicad_sch"

            # Create and save test schematic
            sch = self._create_test_schematic(component_count)
            sch.save(test_file)

            # Benchmark parsing
            start_time = time.time()
            loaded_sch = ksa.load_schematic(test_file)
            parse_time = time.time() - start_time

            # Benchmark saving
            start_time = time.time()
            loaded_sch.save(f"resaved_{test_file}")
            save_time = time.time() - start_time

            results["parse_times"].append(parse_time)
            results["save_times"].append(save_time)

            print(f"{size} schematic ({component_count} components): "
                  f"Parse: {parse_time:.3f}s, Save: {save_time:.3f}s")

        return results

    def benchmark_bulk_operations(self) -> Dict[str, Any]:
        """Benchmark bulk operations performance."""
        sch = ksa.create_schematic('Bulk Operations Test')

        # Create base components
        base_count = 500
        for i in range(base_count):
            sch.components.add('Device:R', f'R{i+1}', f'{10*(i+1)}k',
                             (100 + (i % 20) * 15, 100 + (i // 20) * 15))

        results = {}

        # Benchmark bulk update
        start_time = time.time()
        count = sch.components.bulk_update(
            criteria={'lib_id': 'Device:R'},
            updates={'properties': {'Tolerance': '1%'}}
        )
        bulk_update_time = time.time() - start_time
        results["bulk_update"] = {"time": bulk_update_time, "count": count}

        # Benchmark filtering
        start_time = time.time()
        filtered = sch.components.filter(lambda c: int(c.reference[1:]) % 10 == 0)
        filter_time = time.time() - start_time
        results["filtering"] = {"time": filter_time, "count": len(filtered)}

        # Benchmark statistics
        start_time = time.time()
        stats = sch.components.get_statistics()
        stats_time = time.time() - start_time
        results["statistics"] = {"time": stats_time, "stats": stats}

        return results

    def _create_test_schematic(self, component_count: int) -> 'Schematic':
        """Create test schematic with specified number of components."""
        sch = ksa.create_schematic(f'Test_{component_count}')

        components_per_row = 20
        component_types = [
            ('Device:R', 'R', '10k'),
            ('Device:C', 'C', '100nF'),
            ('Device:L', 'L', '10uH'),
        ]

        for i in range(component_count):
            lib_id, prefix, value = component_types[i % len(component_types)]
            ref = f'{prefix}{i+1}'
            pos = (100 + (i % components_per_row) * 20, 100 + (i // components_per_row) * 20)

            sch.components.add(lib_id, ref, value, pos)

        return sch

    def plot_results(self, results: Dict[str, Any], title: str = "Performance Benchmark"):
        """Plot benchmark results."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot creation times
        if "times" in results:
            ax1.plot(results["counts"], results["times"], 'b-o')
            ax1.set_xlabel('Component Count')
            ax1.set_ylabel('Time (seconds)')
            ax1.set_title('Component Creation Performance')
            ax1.grid(True)

        # Plot memory usage
        if "memory_usage" in results:
            ax2.plot(results["counts"], results["memory_usage"], 'r-s')
            ax2.set_xlabel('Component Count')
            ax2.set_ylabel('Memory (MB)')
            ax2.set_title('Memory Usage')
            ax2.grid(True)

        plt.suptitle(title)
        plt.tight_layout()
        plt.show()

# Usage example
if __name__ == "__main__":
    benchmark = PerformanceBenchmark()

    # Run benchmarks
    creation_results = benchmark.benchmark_component_creation()
    parsing_results = benchmark.benchmark_parsing()
    bulk_results = benchmark.benchmark_bulk_operations()

    # Plot results
    benchmark.plot_results(creation_results, "Component Creation Benchmark")

    # Print summary
    print("\nBenchmark Summary:")
    print(f"Creation performance: {creation_results['times'][-1]:.3f}s for 1000 components")
    print(f"Bulk update performance: {bulk_results['bulk_update']['time']:.3f}s")
    print(f"Filtering performance: {bulk_results['filtering']['time']:.3f}s")
```

## Usage Examples Demonstrating Hybrid Approach

### Complete Circuit Example
```python
"""
Example demonstrating the hybrid approach combining:
- kicadts-inspired fluent interface
- kicad-sch-api performance optimizations
- Enhanced error reporting
- Multiple creation patterns
"""

def create_voltage_divider_example():
    """Create voltage divider using multiple API patterns."""

    # Method 1: Fluent interface (kicadts-inspired)
    print("Method 1: Fluent Interface")
    circuit1 = (ksa.create_schematic('Voltage Divider - Fluent')
               .fluent
               .add_resistor('R1', '10k', (100, 100))
               .add_resistor('R2', '10k', (100, 150))
               .connect_pins('R1', '2', 'R2', '1')
               .save('voltage_divider_fluent.kicad_sch'))

    # Method 2: Dictionary-based creation (kicadts-style)
    print("Method 2: Dictionary-based Creation")
    circuit2 = ksa.create_schematic('Voltage Divider - Dict')
    components = circuit2.components.add_bulk_from_specs([
        {
            'lib_id': 'Device:R',
            'reference': 'R1',
            'value': '10k',
            'position': [100, 100],
            'properties': {'Tolerance': '1%', 'Power': '0.25W'}
        },
        {
            'lib_id': 'Device:R',
            'reference': 'R2',
            'value': '10k',
            'position': [100, 150],
            'properties': {'Tolerance': '1%', 'Power': '0.25W'}
        }
    ])
    circuit2.auto_route_pins('R1', '2', 'R2', '1')
    circuit2.save('voltage_divider_dict.kicad_sch')

    # Method 3: Collection-based (optimized for performance)
    print("Method 3: Collection-based Performance")
    circuit3 = ksa.create_schematic('Voltage Divider - Performance')
    r1 = circuit3.components.add('Device:R', 'R1', '10k', (100, 100))
    r2 = circuit3.components.add('Device:R', 'R2', '10k', (100, 150))

    # Bulk property update
    circuit3.components.bulk_update(
        criteria={'lib_id': 'Device:R'},
        updates={'properties': {'Tolerance': '1%', 'Power': '0.25W'}}
    )

    circuit3.auto_route_pins('R1', '2', 'R2', '1')

    # Save with different formatting options
    circuit3.save('voltage_divider_original.kicad_sch',
                  formatting=FormattingMode.PRESERVE_ORIGINAL)
    circuit3.save('voltage_divider_clean.kicad_sch',
                  formatting=FormattingMode.DETERMINISTIC_CLEAN)

    # Validation and error reporting
    issues = circuit3.validate()
    if issues:
        print("Validation Issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("All circuits validated successfully!")

    return circuit1, circuit2, circuit3

def create_complex_circuit_example():
    """Create more complex circuit demonstrating advanced features."""

    # Create op-amp based circuit
    circuit = ksa.create_schematic('Op-Amp Circuit')

    # Add components using different methods
    # Op-amp using dictionary method
    op_amp = circuit.components.add_from_dict({
        'lib_id': 'Amplifier_Operational:LM358',
        'reference': 'U1',
        'value': 'LM358',
        'position': [150, 100],
        'unit': 1,
        'properties': {
            'Datasheet': 'http://www.ti.com/lit/ds/symlink/lm358.pdf',
            'Description': 'Low-Power, Dual Operational Amplifiers'
        }
    })

    # Resistors using fluent interface
    circuit.fluent.add_resistor('R1', '10k', (50, 80)).add_resistor('R2', '100k', (200, 80))

    # Capacitors using traditional method
    c1 = circuit.components.add('Device:C', 'C1', '100nF', (50, 120))
    c2 = circuit.components.add('Device:C', 'C2', '10uF', (200, 120))

    # Power connections
    circuit.components.add('power:+5V', '#PWR01', '+5V', (100, 50))
    circuit.components.add('power:GND', '#PWR02', 'GND', (100, 170))

    # Intelligent routing with different strategies
    circuit.auto_route_pins('R1', '2', 'U1', '2', routing_mode='direct')  # Direct connection
    circuit.auto_route_pins('U1', '1', 'R2', '1', routing_mode='manhattan')  # Manhattan routing

    # Add labels for clarity
    circuit.add_label('INPUT', (30, 80))
    circuit.add_label('OUTPUT', (220, 80))

    # Set title block
    circuit.set_title_block(
        title='Op-Amp Non-Inverting Amplifier',
        date='2024-01-15',
        rev='1.0',
        company='Example Electronics'
    )

    # Comprehensive validation
    issues = circuit.validate()
    print(f"Validation found {len(issues)} issues")

    # Performance statistics
    stats = circuit.get_performance_stats()
    print(f"Performance: {stats}")

    # Save with clean formatting
    circuit.save('op_amp_circuit.kicad_sch', formatting=FormattingMode.DETERMINISTIC_CLEAN)

    return circuit

if __name__ == "__main__":
    # Run examples
    print("Creating voltage divider examples...")
    circuits = create_voltage_divider_example()

    print("\nCreating complex op-amp circuit...")
    complex_circuit = create_complex_circuit_example()

    print("\nRunning performance benchmark...")
    benchmark = PerformanceBenchmark()
    results = benchmark.benchmark_component_creation([10, 50, 100])
    print(f"Benchmark results: {results}")
```

## Conclusion

These implementation examples demonstrate how to successfully combine the best features of both libraries:

1. **Type Safety**: Enhanced Python type hints inspired by TypeScript
2. **Fluent Interfaces**: Optional intuitive API without sacrificing performance
3. **Multiple Patterns**: Support for different creation styles
4. **Enhanced Errors**: Detailed error reporting with suggestions
5. **Performance**: Maintain bulk operations and optimization
6. **Flexibility**: Different formatting modes for different use cases

The hybrid approach allows developers to choose the API style that best fits their workflow while maintaining the professional features and performance optimizations that make kicad-sch-api suitable for production use.