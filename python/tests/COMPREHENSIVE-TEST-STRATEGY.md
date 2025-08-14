# Comprehensive Test Strategy for kicad-sch-api

## Reference Schematic Test Projects Needed

Based on analysis of KiCAD schematic elements and circuit-synth's existing test cases, here's a comprehensive test strategy for the reference_kicad_projects directory.

---

## 🎯 **Core Schematic Elements**

### **1. Basic Components** (Priority: HIGH)

#### **01_simple_resistor** ✅ (Already exists)
- Single resistor with basic properties
- Tests: Basic component parsing, property access

#### **02_multiple_passive_components**
```
Components: R1 (10k), C1 (0.1uF), L1 (10uH), D1 (LED)
Tests: Multiple component types, different libraries
Purpose: Validate basic component variety handling
```

#### **03_complex_ics**
```
Components: ESP32-C6 (multi-unit), STM32F4 (BGA), Op-amp (multiple units)
Tests: Multi-unit symbols, complex pin arrangements, large component handling
Purpose: Test complex ICs with many pins and units
```

---

### **2. Labels and Text** (Priority: HIGH)

#### **04_label_types**
```
Elements:
- Local labels: VCC, GND, DATA_IN, DATA_OUT
- Global labels: USB_DP, USB_DM, SYSTEM_RESET
- Hierarchical labels: POWER_IN, SIGNAL_BUS[0..7]
- Text boxes: "Power Supply Section", "USB Interface"

Tests: Label parsing, text handling, different label types
Purpose: Validate all label and text element types
```

#### **05_text_and_annotations**
```
Elements:
- Regular text: Component values, annotations
- Text boxes: Multi-line descriptions, design notes
- Special characters: Greek symbols (μ, Ω), subscripts, superscripts
- Different fonts and sizes

Tests: Text parsing, special character handling, font effects
Purpose: Ensure text elements are preserved correctly
```

---

### **3. Hierarchical Sheets** (Priority: HIGH)

#### **06_simple_hierarchical** ✅ (Partially exists)
```
Structure: 
- Main sheet with power supply sheet symbol
- Power_Supply.kicad_sch sub-sheet
- Hierarchical pins: VIN, VOUT, GND

Tests: Sheet symbol parsing, hierarchical pin handling, multi-file projects
Purpose: Basic hierarchical design validation
```

#### **07_complex_hierarchical**
```
Structure:
- Main board (ESP32_C6_Dev_Board.kicad_sch)
- Sub-sheets: MCU.kicad_sch, USB.kicad_sch, Power.kicad_sch, LEDs.kicad_sch
- Hierarchical labels with buses: SPI[0..3], I2C[0..1], GPIO[0..15]

Tests: Complex hierarchy, bus handling, multi-level nesting
Purpose: Professional hierarchical design patterns
```

---

### **4. Connection Elements** (Priority: HIGH)

#### **08_wire_and_bus_connections**
```
Elements:
- Simple wires: Point-to-point connections
- Bus wires: Multi-bit signal buses
- Wire junctions: T-connections, multi-way joins
- No-connect flags: Unused pins marked

Tests: Wire parsing, junction handling, bus connections
Purpose: Complete connection topology validation
```

#### **09_complex_routing**
```
Elements:
- Angled wires: 45-degree connections
- Bus entries: Bus-to-wire connections
- Net ties: Special connection elements
- Wire crossovers: Non-connecting wire intersections

Tests: Complex routing patterns, special connection types
Purpose: Advanced connection handling
```

---

### **5. Power and Ground Symbols** (Priority: MEDIUM)

#### **10_power_symbols**
```
Components:
- Power symbols: VCC, VDD, VBAT, +5V, +3.3V
- Ground symbols: GND, DGND, AGND, Earth
- Power flags: PWR_FLAG for power sources

Tests: Power symbol handling, special symbol types
Purpose: Power distribution network validation
```

---

### **6. Special Components** (Priority: MEDIUM)

#### **11_complex_connectors**
```
Components:
- USB connectors: USB-C, USB-A, Micro-USB
- Pin headers: 2x5 IDC, 1x40 pin header
- Card edge connectors: PCIe, memory slots
- RF connectors: SMA, U.FL

Tests: Multi-pin connectors, pin numbering schemes
Purpose: Complex connector handling
```

#### **12_mechanical_components**
```
Components:
- Mounting holes: M3, standoffs
- Test points: TP1, TP2, TP3
- Fiducials: Assembly alignment markers
- Mechanical symbols: Enclosure outlines

Tests: Non-electrical components, mechanical elements
Purpose: Complete BOM and mechanical handling
```

---

### **7. Symbol Library Complexity** (Priority: HIGH)

#### **13_symbol_with_extends**
```
Components: Symbols that use "extends" inheritance
- Base symbol: Generic Op-Amp
- Extended symbols: LM358, TL072, etc.
- Multiple inheritance levels

Tests: Symbol inheritance, extends parsing, pin mapping
Purpose: Complex symbol library relationships
```

#### **14_multi_unit_symbols**
```
Components:
- Quad op-amp: LM324 (4 units)
- Hex inverter: 74HC04 (6 units)  
- Dual transistor arrays

Tests: Multi-unit handling, unit numbering, shared properties
Purpose: Complex multi-unit symbol management
```

#### **15_power_symbols_complex**
```
Components:
- Voltage regulators: LM7805, AMS1117
- Power management ICs: Battery chargers, DC-DC converters
- Power symbols with special properties

Tests: Power component handling, special power flags
Purpose: Power management circuit validation
```

---

### **8. Graphics and Images** (Priority: MEDIUM)

#### **16_graphical_elements**
```
Elements:
- Rectangles: Board outlines, section boundaries
- Circles: Component outlines, mechanical boundaries
- Polylines: Custom shapes, arrows
- Arcs: Curved connections, decorative elements

Tests: Graphical element parsing, shape handling
Purpose: Complete graphical element support
```

#### **17_images_and_logos**
```
Elements:
- Embedded images: Company logos, component photos
- Different formats: PNG, SVG (if supported)
- Image positioning and scaling

Tests: Image embedding, format handling
Purpose: Documentation and branding elements
```

---

### **9. Advanced Features** (Priority: MEDIUM)

#### **18_simulation_elements**
```
Components:
- SPICE models: Behavioral sources, simulation-only components
- Simulation-specific properties: .model, .subckt
- Exclude from simulation flags

Tests: Simulation element handling, SPICE integration
Purpose: Simulation workflow support
```

#### **19_design_rule_elements**
```
Elements:
- Design rule annotations: Critical net markers
- Assembly notes: Special handling instructions
- Version control elements: Revision tracking

Tests: Metadata handling, design rule integration
Purpose: Professional design workflow support
```

---

### **10. Edge Cases and Stress Tests** (Priority: HIGH)

#### **20_stress_test_large**
```
Scale: 1000+ components, complex hierarchy, many nets
Components: Microprocessor system with memory, peripherals
Purpose: Performance validation, memory usage, large file handling
```

#### **21_unicode_and_special_chars**
```
Elements:
- Unicode characters: μ, Ω, °C, ±
- Special symbols: Trademark, copyright
- Non-ASCII component names: International components

Tests: Character encoding, special symbol handling
Purpose: International design support
```

#### **22_edge_case_formats**
```
Elements:
- Minimal valid schematic (absolute minimum)
- Maximum nesting depth
- Very long component names/values
- Empty sections and optional elements

Tests: Format edge cases, parser robustness
Purpose: Robustness and edge case handling
```

---

## 🔬 **Component Complexity Analysis**

### **Components with "extends" (HIGH COMPLEXITY)**

From KiCAD libraries, these components use inheritance:

#### **Microcontrollers (STM32, ESP32)**
```
Base: Generic microcontroller symbol
Extends: STM32F103, STM32F407, ESP32-C6, etc.
Complexity: 100+ pins, multiple units, specialized pin functions
Test Focus: Pin mapping, unit handling, complex inheritance
```

#### **Op-Amps and Analog ICs**
```
Base: Generic op-amp
Extends: LM324, TL074, AD8220, etc.
Complexity: Multiple units per package, power pins, special symbols
Test Focus: Multi-unit symbols, power pin handling
```

#### **Logic Families (74xx series)**
```
Base: Generic logic gate
Extends: 74HC00, 74LS138, 74LVC245, etc.
Complexity: Various gate types, different supply voltages
Test Focus: Logic symbol variants, pin numbering schemes
```

#### **Connectors**
```
Base: Generic connector
Extends: USB-C, HDMI, Ethernet, Card slots
Complexity: Complex pin arrangements, shield connections
Test Focus: Multi-pin connectors, pin naming conventions
```

### **Power Management Components**
```
Examples: Buck converters, LDOs, battery management
Complexity: Enable pins, feedback networks, thermal pads
Test Focus: Power component special properties
```

---

## 🧪 **Testing Strategy by Priority**

### **Phase 1: Core Elements** (Week 1)
```
Priority Tests:
✅ 01_simple_resistor (working)
🔲 02_multiple_passive_components  
🔲 04_label_types
🔲 06_simple_hierarchical
🔲 08_wire_and_bus_connections
🔲 13_symbol_with_extends
```

### **Phase 2: Advanced Features** (Week 2)
```
Advanced Tests:
🔲 07_complex_hierarchical
🔲 11_complex_connectors  
🔲 14_multi_unit_symbols
🔲 16_graphical_elements
🔲 20_stress_test_large
```

### **Phase 3: Professional Features** (Week 3)
```
Professional Tests:
🔲 17_images_and_logos
🔲 18_simulation_elements
🔲 21_unicode_and_special_chars
🔲 22_edge_case_formats
```

---

## 📋 **Test Implementation Plan**

### **For Each Reference Schematic**:

1. **Create KiCAD project manually** with target elements
2. **Export test schematic** to reference_kicad_projects/
3. **Write pytest test** to validate parsing and round-trip
4. **Add format preservation test** (load → save → compare)
5. **Add manipulation test** (modify elements, validate changes)

### **Test Structure Template**:
```python
class TestReferenceSchematic{Name}:
    """Test {specific_feature} handling."""
    
    @pytest.fixture
    def reference_schematic(self):
        """Load reference schematic."""
        return load_reference_schematic("{name}")
    
    def test_parse_{name}(self, reference_schematic):
        """Test parsing {specific_feature}."""
        # Validate parsing without errors
        # Check specific elements are extracted correctly
        
    def test_round_trip_{name}(self, reference_schematic):
        """Test round-trip format preservation."""
        # load → save → compare byte-level differences
        
    def test_modify_{name}(self, reference_schematic):
        """Test modifying {specific_feature}."""
        # Make changes, validate they work correctly
```

---

## 🎲 **Complex Component Examples to Test**

### **High Priority Complex Components**:

#### **STM32 Microcontrollers**
- **Complexity**: 100+ pins, multiple units (MCU + power), extends relationships
- **Test Focus**: Multi-unit handling, complex pin arrangements, power pin management

#### **ESP32-C6 (Already in circuit-synth)**
- **Complexity**: WiFi/Bluetooth module, dual-core, many peripherals
- **Test Focus**: Modern MCU handling, peripheral pin mapping

#### **USB-C Connectors**
- **Complexity**: 24 pins, CC pins, shield connections, alternate modes
- **Test Focus**: Complex connector handling, pin naming

#### **Power Management ICs**
- **Examples**: TPS63000 (buck-boost), LM3478 (LED driver)
- **Complexity**: Enable pins, feedback networks, thermal considerations
- **Test Focus**: Power component special properties

#### **High-Speed Differential Components**
- **Examples**: LVDS drivers, USB 3.0 hubs, PCIe switches
- **Complexity**: Differential pairs, impedance control requirements
- **Test Focus**: High-speed signal handling

### **Medium Priority**:

#### **RF Components**
- **Examples**: RF switches, amplifiers, antennas
- **Complexity**: S-parameter models, frequency-dependent properties

#### **Analog Frontend Components**
- **Examples**: ADCs, DACs, analog switches
- **Complexity**: Reference voltage pins, analog/digital ground separation

#### **Motor Driver ICs**
- **Examples**: A4988 stepper driver, brushed DC motor controllers
- **Complexity**: High-current pins, thermal pads, protection circuits

---

## 🎯 **Recommended Implementation Order**

### **Week 1: Foundation Elements**
1. **02_multiple_passive_components** - R, L, C, D variety
2. **04_label_types** - Local, global, hierarchical labels
3. **08_wire_and_bus_connections** - Basic connectivity
4. **13_symbol_with_extends** - Inheritance testing

### **Week 2: Complex Features**  
5. **06_simple_hierarchical** - Basic sheet symbols
6. **14_multi_unit_symbols** - Quad op-amps, hex inverters
7. **11_complex_connectors** - USB-C, pin headers
8. **16_graphical_elements** - Rectangles, polylines

### **Week 3: Professional Features**
9. **07_complex_hierarchical** - Multi-level hierarchy
10. **20_stress_test_large** - Performance validation
11. **21_unicode_and_special_chars** - International support
12. **17_images_and_logos** - Documentation elements

### **Week 4: Edge Cases**
13. **18_simulation_elements** - SPICE integration
14. **22_edge_case_formats** - Parser robustness
15. **19_design_rule_elements** - Professional metadata

---

## 🔍 **GitHub Issue Analysis**

You mentioned there might be GitHub issues in circuit-synth related to complex components. Let me check for any documented issues:

### **Potential Issues from Analysis**:

#### **Symbol Inheritance ("extends")**
- **Issue**: Complex inheritance chains in symbol libraries
- **Test Need**: Verify extends relationships are preserved correctly
- **Components**: Op-amps, logic gates, microcontrollers

#### **Multi-Unit Symbol Handling**
- **Issue**: Components with multiple units (gates, amplifiers)  
- **Test Need**: Ensure unit numbering and shared properties work
- **Components**: 74xx logic, quad op-amps, multi-gate ICs

#### **Unicode and Special Characters**
- **Issue**: International component names, Greek symbols (μ, Ω)
- **Test Need**: Character encoding preservation
- **Components**: European/Asian components, measurement units

#### **Large Component Count Performance**
- **Issue**: Slow parsing with 1000+ component schematics
- **Test Need**: Performance benchmarking and optimization
- **Scope**: Industrial designs, FPGA boards, memory arrays

---

## 📊 **Test Coverage Matrix**

| Element Type | Simple | Complex | Edge Cases | Status |
|--------------|--------|---------|------------|---------|
| **Components** | ✅ Resistor | 🔲 ESP32-C6 | 🔲 Multi-unit | Started |
| **Labels** | 🔲 Local | 🔲 Hierarchical | 🔲 Unicode | Not Started |
| **Hierarchy** | 🔲 Single sheet | 🔲 Multi-level | 🔲 Deep nesting | Not Started |
| **Connections** | 🔲 Simple wire | 🔲 Bus connections | 🔲 Complex routing | Not Started |
| **Graphics** | 🔲 Rectangle | 🔲 Polylines | 🔲 Images | Not Started |
| **Text** | 🔲 Basic text | 🔲 Text boxes | 🔲 Special chars | Not Started |
| **Power** | 🔲 VCC/GND | 🔲 Power flags | 🔲 Power management | Not Started |
| **Libraries** | 🔲 Device lib | 🔲 Custom libs | 🔲 Extends chains | Not Started |

---

## 🚀 **Immediate Next Steps**

### **Create These Reference Projects First**:

1. **02_multiple_passive_components** - Foundation for component variety
2. **04_label_types** - Essential for any real circuit  
3. **08_wire_and_bus_connections** - Core connectivity testing
4. **13_symbol_with_extends** - Complex library handling

### **Test Implementation Strategy**:

1. **Manual creation** in KiCAD 9 with specific elements
2. **Save as reference** in reference_kicad_projects/
3. **Write corresponding pytest** for each reference
4. **Validate parsing accuracy** and format preservation
5. **Test modification operations** (add/remove/update elements)

This comprehensive strategy ensures kicad-sch-api can handle the full complexity of professional KiCAD schematics while maintaining exact format preservation and high performance.

**Should I help you create specific reference schematics or implement the tests for any of these categories?**