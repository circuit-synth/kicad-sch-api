# Interfaces Module

Type definitions and protocol classes for extensibility.

## Overview

This module defines abstract interfaces and protocols that allow other code to extend or implement custom functionality. It uses Python's `typing` module and PEP 544 protocols for structural subtyping.

## Protocol Classes

### Element Protocol
- **Purpose**: Define interface for schematic elements
- **Defines**: Common properties all elements should have
- **Properties**:
  - `uuid` - Unique identifier
  - `modified` - Change tracking
  - `to_dict()` - Serialize to dictionary

### Parser Protocol
- **Purpose**: Define parser interface
- **Requires**:
  - `parse()` - Parse S-expression
  - `format()` - Format back to S-expression
  - `validate()` - Validate element

### Manager Protocol
- **Purpose**: Define manager interface
- **Requires**:
  - `initialize()` - Initialize manager
  - `validate()` - Validate state
  - `cleanup()` - Cleanup resources

## Type Definitions

### Common Types
- `ElementID` - UUID string for element
- `Reference` - Component reference (e.g., "R1")
- `LibID` - Library identifier (e.g., "Device:R")
- `Point` - Tuple[float, float] for coordinates
- `BoundingBox` - Dict with bounds
- `PropertyDict` - Dict[str, Any] for properties

## Design Patterns

### Protocol Pattern
```python
from typing import Protocol

class ElementProtocol(Protocol):
    """Interface for schematic elements"""

    @property
    def uuid(self) -> str:
        """Get unique identifier"""
        ...

    @property
    def modified(self) -> bool:
        """Get modification status"""
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        ...
```

### Implementing Protocol
```python
class MyComponent:
    """Custom component implementation"""

    def __init__(self):
        self._uuid = generate_uuid()
        self._modified = False

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def modified(self) -> bool:
        return self._modified

    def to_dict(self) -> Dict[str, Any]:
        return {'uuid': self._uuid}

# MyComponent automatically satisfies ElementProtocol
# due to structural subtyping (no explicit inheritance needed)
```

## Extensibility Points

### Custom Element Types
Users can create custom element types by:
1. Implementing the Element protocol
2. Registering with parser registry
3. Adding manager support

### Custom Managers
Users can create custom managers by:
1. Implementing the Manager protocol
2. Integrating with Schematic class
3. Defining public API

### Custom Collections
Users can create custom collections by:
1. Extending collection base classes
2. Adding custom filtering/queries
3. Integrating with element types

## Interface Benefits

✅ **Type Safety** - mypy can verify implementations
✅ **Extensibility** - Users can implement interfaces
✅ **Documentation** - Clear contracts between components
✅ **Flexibility** - Structural typing (no inheritance needed)
✅ **Backward Compatibility** - New types work with existing code

## Current Interfaces

Review `interfaces/` directory for specific protocol definitions:

- `element.py` - Element type protocols
- `manager.py` - Manager protocols
- `parser.py` - Parser protocols
- `collection.py` - Collection protocols

## Usage Example

### Implementing Custom Element
```python
from typing import Dict, Any
from kicad_sch_api.interfaces import ElementProtocol

class CustomElement:
    """Custom element implementation"""

    def __init__(self, name: str):
        self._uuid = generate_uuid()
        self.name = name

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def modified(self) -> bool:
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {'uuid': self._uuid, 'name': self.name}

# Can be used anywhere ElementProtocol is expected
element: ElementProtocol = CustomElement('my_element')
```

### Implementing Custom Manager
```python
from kicad_sch_api.interfaces import ManagerProtocol

class CustomManager:
    """Custom manager implementation"""

    def initialize(self) -> None:
        pass

    def validate(self) -> bool:
        return True

    def cleanup(self) -> None:
        pass
```

## Type Checking

With protocols, mypy provides strong typing:

```bash
# Type check code
mypy --strict kicad_sch_api/

# Verifies:
# - All protocol implementations are correct
# - No type errors
# - All required methods exist
```

## Known Issues

1. **Documentation** - Protocol documentation could be more complete
2. **Examples** - More examples of custom implementations needed
3. **Validation** - Runtime protocol checking not implemented
4. **Performance** - Protocol overhead minimal but not benchmarked

## Future Improvements

- [ ] Runtime protocol validation
- [ ] More detailed protocol documentation
- [ ] Example custom implementations
- [ ] Protocol inheritance hierarchies
- [ ] Composite protocols
- [ ] Protocol mixins

## References

- Python Protocols: https://peps.python.org/pep-0544/
- Type Checking: https://mypy.readthedocs.io/
- Design Patterns: See `CODEBASE_ANALYSIS.md`
