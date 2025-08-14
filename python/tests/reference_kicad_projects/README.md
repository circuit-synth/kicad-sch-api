# Reference KiCAD Projects for Testing

This directory contains reference schematic projects for comprehensive testing of kicad-sch-api functionality. Each project tests specific KiCAD schematic elements and edge cases.

## 📋 **Test Project Checklist**

### **Phase 1: Core Elements** (HIGH PRIORITY)

#### **Basic Components**
- [ ] **01_simple_resistor** ✅ (Already exists)
  - Single resistor with basic properties
  - Tests: Basic component parsing, property access

- [ ] **02_multiple_passive_components**
  - Components: R1 (10k), C1 (0.1uF), L1 (10uH), D1 (LED)
  - Tests: Multiple component types, different libraries
  - Purpose: Validate basic component variety handling

- [ ] **03_complex_ics**
  - Components: ESP32-C6 (multi-unit), STM32F4 (BGA), Op-amp (multiple units)
  - Tests: Multi-unit symbols, complex pin arrangements, large component handling
  - Purpose: Test complex ICs with many pins and units

#### **Labels and Text**
- [ ] **04_label_types**
  - Elements: Local labels (VCC, GND), Global labels (USB_DP, USB_DM), Hierarchical labels (POWER_IN, SIGNAL_BUS)
  - Tests: Label parsing, text handling, different label types
  - Purpose: Validate all label and text element types

- [ ] **05_text_and_annotations**
  - Elements: Text boxes, multi-line descriptions, special characters (μ, Ω)
  - Tests: Text parsing, special character handling, font effects
  - Purpose: Ensure text elements are preserved correctly

#### **Connections**
- [ ] **06_wire_and_bus_connections**
  - Elements: Simple wires, bus wires, wire junctions, no-connect flags
  - Tests: Wire parsing, junction handling, bus connections
  - Purpose: Complete connection topology validation

- [ ] **07_complex_routing**
  - Elements: Angled wires, bus entries, net ties, wire crossovers
  - Tests: Complex routing patterns, special connection types
  - Purpose: Advanced connection handling

### **Phase 2: Hierarchical Design** (HIGH PRIORITY)

#### **Hierarchical Sheets**
- [ ] **08_simple_hierarchical** ✅ (Partially exists)
  - Structure: Main sheet + Power_Supply.kicad_sch sub-sheet
  - Tests: Sheet symbol parsing, hierarchical pin handling
  - Purpose: Basic hierarchical design validation

- [ ] **09_complex_hierarchical**
  - Structure: Main + MCU + USB + Power + LEDs sub-sheets
  - Tests: Complex hierarchy, multi-level nesting
  - Purpose: Professional hierarchical design patterns

- [ ] **10_deep_hierarchy**
  - Structure: 4+ levels of nesting (System → Board → Module → Circuit)
  - Tests: Deep nesting handling, path resolution
  - Purpose: Maximum hierarchy complexity

### **Phase 3: Complex Components** (MEDIUM PRIORITY)

#### **Symbol Library Complexity**
- [ ] **11_symbol_with_extends**
  - Components: Op-amps with extends (LM324 → Generic_Op_Amp)
  - Tests: Symbol inheritance, extends parsing, pin mapping
  - Purpose: Complex symbol library relationships

- [ ] **12_multi_unit_symbols**
  - Components: Quad op-amp (LM324), Hex inverter (74HC04), Dual gates
  - Tests: Multi-unit handling, unit numbering, shared properties
  - Purpose: Complex multi-unit symbol management

- [ ] **13_power_symbols_complex**
  - Components: Voltage regulators, power management ICs, power flags
  - Tests: Power component handling, special power flags
  - Purpose: Power management circuit validation

#### **Modern Complex Components**
- [ ] **14_esp32_c6_module**
  - Component: ESP32-C6 with WiFi/Bluetooth, 80+ pins
  - Tests: Modern MCU handling, peripheral pin mapping
  - Purpose: Ultimate MCU complexity test

- [ ] **15_usb_c_connector**
  - Component: USB-C with 24 pins, CC pins, shield connections
  - Tests: Complex connector handling, pin naming
  - Purpose: Modern connector complexity

- [ ] **16_stm32_microcontroller**
  - Component: STM32F407 with 100+ pins, multiple units
  - Tests: Large pin count, multi-unit MCU handling
  - Purpose: Professional MCU design patterns

### **Phase 4: Advanced Features** (MEDIUM PRIORITY)

#### **Graphics and Visual Elements**
- [ ] **17_graphical_elements**
  - Elements: Rectangles, circles, polylines, arcs
  - Tests: Graphical element parsing, shape handling
  - Purpose: Complete graphical element support

- [ ] **18_images_and_logos**
  - Elements: Embedded images, company logos, component photos
  - Tests: Image embedding, format handling
  - Purpose: Documentation and branding elements

#### **Professional Features**
- [ ] **19_simulation_elements**
  - Components: SPICE models, behavioral sources, simulation flags
  - Tests: Simulation element handling, SPICE integration
  - Purpose: Simulation workflow support

- [ ] **20_design_rule_elements**
  - Elements: Design rule annotations, assembly notes, version control
  - Tests: Metadata handling, design rule integration
  - Purpose: Professional design workflow support

### **Phase 5: Stress Tests** (LOW PRIORITY)

#### **Performance and Edge Cases**
- [ ] **21_stress_test_large**
  - Scale: 1000+ components, complex hierarchy, many nets
  - Tests: Performance validation, memory usage
  - Purpose: Large-scale design handling

- [ ] **22_unicode_and_special_chars**
  - Elements: Unicode (μ, Ω, °C), trademark symbols, international names
  - Tests: Character encoding, special symbol handling
  - Purpose: International design support

- [ ] **23_edge_case_formats**
  - Elements: Minimal valid schematic, maximum nesting, very long names
  - Tests: Format edge cases, parser robustness
  - Purpose: Robustness and edge case handling

### **Phase 6: Specialized Components** (LOW PRIORITY)

#### **Industry-Specific Components**
- [ ] **24_rf_components**
  - Components: RF switches, amplifiers, antennas, S-parameter models
  - Tests: RF component handling, frequency-dependent properties
  - Purpose: RF design support

- [ ] **25_power_management_ics**
  - Components: Buck converters, LDOs, battery management, thermal pads
  - Tests: Power IC special properties, thermal considerations
  - Purpose: Power electronics design

- [ ] **26_high_speed_differential**
  - Components: LVDS drivers, USB 3.0, PCIe, differential pairs
  - Tests: High-speed signal handling, impedance control
  - Purpose: High-speed digital design

- [ ] **27_analog_frontend**
  - Components: ADCs, DACs, analog switches, reference voltages
  - Tests: Analog component handling, precision requirements
  - Purpose: Analog and mixed-signal design

- [ ] **28_motor_control**
  - Components: Stepper drivers, motor controllers, high-current handling
  - Tests: High-current component handling, protection circuits
  - Purpose: Motor control and power electronics

---

## 🎯 **Recommended Implementation Order**

### **Start with These 4** (Essential Foundation):
1. **02_multiple_passive_components** - Basic component variety
2. **04_label_types** - Essential for real circuits
3. **06_wire_and_bus_connections** - Core connectivity
4. **11_symbol_with_extends** - Complex inheritance (your main concern)

### **Then Add These 4** (Core Functionality):
5. **08_simple_hierarchical** - Basic hierarchy
6. **12_multi_unit_symbols** - Professional component handling
7. **14_esp32_c6_module** - Modern MCU complexity
8. **17_graphical_elements** - Visual elements

### **Finally These 4** (Professional Polish):
9. **09_complex_hierarchical** - Advanced hierarchy
10. **21_stress_test_large** - Performance validation
11. **22_unicode_and_special_chars** - International support
12. **18_images_and_logos** - Documentation elements

---

## 📊 **Current Status**

✅ **01_simple_resistor** - Basic component (working)  
✅ **single_label** - Basic label (exists)  
✅ **single_label_hierarchical** - Hierarchical label (exists)  

**Next to implement**: 25 additional reference projects for comprehensive coverage

---

## 🔍 **Complex Component Examples**

### **Components with "extends" to Focus On**:

#### **STM32 Family** (Highest Priority):
- **Base**: Generic microcontroller symbol
- **Extends**: STM32F103 → STM32F407 → STM32H7 series
- **Complexity**: 100+ pins, multiple power domains, peripheral multiplexing

#### **Op-Amp Families**:
- **Base**: Generic op-amp symbol  
- **Extends**: LM324 → TL074 → AD8220 → specialized variants
- **Complexity**: Multiple units per package, power pins, compensation

#### **Logic Gate Families**:
- **Base**: Generic logic gate
- **Extends**: 74HC00 → 74LS00 → 74LVC00 → specialized variants
- **Complexity**: Different logic families, power requirements, speed grades

#### **Connector Families**:
- **Base**: Generic connector
- **Extends**: Header → USB → Specialized connectors
- **Complexity**: Pin arrangements, shield connections, mechanical constraints

This list provides a structured approach to build comprehensive test coverage over time, focusing on the most critical and complex elements first while ensuring complete KiCAD schematic support.

**You can implement these at your own pace, starting with the Phase 1 high-priority items!**