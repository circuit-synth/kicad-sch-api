#!/usr/bin/env python3
"""
Python MCP interface for kicad-sch-api.

This script provides the Python side of the MCP bridge, handling commands
from the TypeScript MCP server and executing them using kicad-sch-api.
"""

import json
import logging
import sys
import traceback
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger('kicad_sch_api.mcp')

# Import kicad-sch-api components
try:
    from ..core.schematic import Schematic
    from ..core.components import Component
    from ..library.cache import get_symbol_cache
    from ..utils.validation import ValidationError, ValidationIssue
except ImportError as e:
    logger.error(f"Failed to import kicad-sch-api modules: {e}")
    sys.exit(1)


class MCPInterface:
    """MCP command interface for kicad-sch-api."""
    
    def __init__(self):
        """Initialize the MCP interface."""
        self.current_schematic: Optional[Schematic] = None
        self.symbol_cache = get_symbol_cache()
        
        # Command handlers
        self.handlers = {
            'ping': self.ping,
            'load_schematic': self.load_schematic,
            'save_schematic': self.save_schematic,
            'create_schematic': self.create_schematic,
            'add_component': self.add_component,
            'update_component': self.update_component,
            'remove_component': self.remove_component,
            'get_component': self.get_component,
            'find_components': self.find_components,
            'add_wire': self.add_wire,
            'connect_components': self.connect_components,
            'bulk_update_components': self.bulk_update_components,
            'validate_schematic': self.validate_schematic,
            'get_schematic_summary': self.get_schematic_summary,
            'search_library_symbols': self.search_library_symbols,
            'add_library_path': self.add_library_path,
        }
        
        logger.info("MCP interface initialized")

    def ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Health check command."""
        return {
            'success': True,
            'message': 'kicad-sch-api MCP interface is ready',
            'version': '1.0.0'
        }

    def load_schematic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Load a schematic file."""
        try:
            file_path = params.get('file_path')
            if not file_path:
                return {'success': False, 'error': 'file_path parameter required'}

            self.current_schematic = Schematic.load(file_path)
            summary = self.current_schematic.get_summary()
            
            return {
                'success': True,
                'message': f'Loaded schematic: {file_path}',
                'summary': summary
            }
        except Exception as e:
            logger.error(f"Error loading schematic: {e}")
            return {'success': False, 'error': str(e)}

    def save_schematic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save the current schematic."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            file_path = params.get('file_path')
            preserve_format = params.get('preserve_format', True)
            
            self.current_schematic.save(file_path, preserve_format)
            
            return {
                'success': True,
                'message': f'Saved schematic to: {self.current_schematic.file_path}'
            }
        except Exception as e:
            logger.error(f"Error saving schematic: {e}")
            return {'success': False, 'error': str(e)}

    def create_schematic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new schematic."""
        try:
            name = params.get('name', 'New Circuit')
            self.current_schematic = Schematic.create(name)
            
            return {
                'success': True,
                'message': f'Created new schematic: {name}',
                'summary': self.current_schematic.get_summary()
            }
        except Exception as e:
            logger.error(f"Error creating schematic: {e}")
            return {'success': False, 'error': str(e)}

    def add_component(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a component to the schematic."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            lib_id = params.get('lib_id')
            if not lib_id:
                return {'success': False, 'error': 'lib_id parameter required'}

            # Extract parameters
            reference = params.get('reference')
            value = params.get('value', '')
            position = params.get('position')
            footprint = params.get('footprint')
            properties = params.get('properties', {})

            # Convert position if provided
            pos_tuple = None
            if position:
                pos_tuple = (position['x'], position['y'])

            # Add component
            component = self.current_schematic.components.add(
                lib_id=lib_id,
                reference=reference,
                value=value,
                position=pos_tuple,
                footprint=footprint,
                **properties
            )

            return {
                'success': True,
                'message': f'Added component: {component.reference}',
                'component': component.to_dict()
            }
        except Exception as e:
            logger.error(f"Error adding component: {e}")
            return {'success': False, 'error': str(e)}

    def update_component(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a component's properties."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            reference = params.get('reference')
            if not reference:
                return {'success': False, 'error': 'reference parameter required'}

            component = self.current_schematic.components.get(reference)
            if not component:
                return {'success': False, 'error': f'Component not found: {reference}'}

            # Apply updates
            updates = 0
            if 'value' in params:
                component.value = params['value']
                updates += 1
            
            if 'position' in params:
                pos = params['position']
                component.position = (pos['x'], pos['y'])
                updates += 1
            
            if 'footprint' in params:
                component.footprint = params['footprint']
                updates += 1
            
            if 'properties' in params:
                for name, value in params['properties'].items():
                    component.set_property(name, value)
                    updates += 1

            return {
                'success': True,
                'message': f'Updated component {reference} ({updates} changes)',
                'component': component.to_dict()
            }
        except Exception as e:
            logger.error(f"Error updating component: {e}")
            return {'success': False, 'error': str(e)}

    def remove_component(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a component from the schematic."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            reference = params.get('reference')
            if not reference:
                return {'success': False, 'error': 'reference parameter required'}

            success = self.current_schematic.components.remove(reference)
            
            if success:
                return {
                    'success': True,
                    'message': f'Removed component: {reference}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Component not found: {reference}'
                }
        except Exception as e:
            logger.error(f"Error removing component: {e}")
            return {'success': False, 'error': str(e)}

    def get_component(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a component."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            reference = params.get('reference')
            if not reference:
                return {'success': False, 'error': 'reference parameter required'}

            component = self.current_schematic.components.get(reference)
            if not component:
                return {'success': False, 'error': f'Component not found: {reference}'}

            return {
                'success': True,
                'component': component.to_dict()
            }
        except Exception as e:
            logger.error(f"Error getting component: {e}")
            return {'success': False, 'error': str(e)}

    def find_components(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find components by criteria."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            # Filter out None values and convert to filter criteria
            criteria = {k: v for k, v in params.items() if v is not None}
            
            # Special handling for in_area
            if 'in_area' in criteria:
                area = criteria['in_area']
                if len(area) == 4:
                    criteria['in_area'] = tuple(area)

            components = self.current_schematic.components.filter(**criteria)
            
            return {
                'success': True,
                'count': len(components),
                'components': [comp.to_dict() for comp in components]
            }
        except Exception as e:
            logger.error(f"Error finding components: {e}")
            return {'success': False, 'error': str(e)}

    def add_wire(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a wire connection."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            start = params.get('start')
            end = params.get('end')
            
            if not start or not end:
                return {'success': False, 'error': 'start and end parameters required'}

            wire_uuid = self.current_schematic.add_wire(
                (start['x'], start['y']),
                (end['x'], end['y'])
            )

            return {
                'success': True,
                'message': f'Added wire from {start} to {end}',
                'wire_uuid': wire_uuid
            }
        except Exception as e:
            logger.error(f"Error adding wire: {e}")
            return {'success': False, 'error': str(e)}

    def connect_components(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Connect two component pins with a wire."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            from_comp = params.get('from_component')
            from_pin = params.get('from_pin')
            to_comp = params.get('to_component')
            to_pin = params.get('to_pin')

            if not all([from_comp, from_pin, to_comp, to_pin]):
                return {'success': False, 'error': 'All connection parameters required'}

            # Get component pin positions
            comp1 = self.current_schematic.components.get(from_comp)
            comp2 = self.current_schematic.components.get(to_comp)

            if not comp1:
                return {'success': False, 'error': f'Component not found: {from_comp}'}
            if not comp2:
                return {'success': False, 'error': f'Component not found: {to_comp}'}

            pin1_pos = comp1.get_pin_position(from_pin)
            pin2_pos = comp2.get_pin_position(to_pin)

            if not pin1_pos or not pin2_pos:
                return {'success': False, 'error': 'Could not determine pin positions'}

            # Add wire between pins
            wire_uuid = self.current_schematic.add_wire(pin1_pos, pin2_pos)

            return {
                'success': True,
                'message': f'Connected {from_comp}.{from_pin} to {to_comp}.{to_pin}',
                'wire_uuid': wire_uuid
            }
        except Exception as e:
            logger.error(f"Error connecting components: {e}")
            return {'success': False, 'error': str(e)}

    def bulk_update_components(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update multiple components matching criteria."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            criteria = params.get('criteria', {})
            updates = params.get('updates', {})

            if not criteria or not updates:
                return {'success': False, 'error': 'criteria and updates parameters required'}

            count = self.current_schematic.components.bulk_update(criteria, updates)

            return {
                'success': True,
                'message': f'Updated {count} components',
                'count': count
            }
        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            return {'success': False, 'error': str(e)}

    def validate_schematic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the current schematic."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            issues = self.current_schematic.validate()
            
            # Categorize issues
            errors = [issue for issue in issues if issue.level.value in ('error', 'critical')]
            warnings = [issue for issue in issues if issue.level.value == 'warning']
            
            return {
                'success': True,
                'valid': len(errors) == 0,
                'issue_count': len(issues),
                'errors': [str(issue) for issue in errors],
                'warnings': [str(issue) for issue in warnings]
            }
        except Exception as e:
            logger.error(f"Error validating schematic: {e}")
            return {'success': False, 'error': str(e)}

    def get_schematic_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of current schematic."""
        try:
            if not self.current_schematic:
                return {'success': False, 'error': 'No schematic loaded'}

            summary = self.current_schematic.get_summary()
            
            return {
                'success': True,
                'summary': summary
            }
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return {'success': False, 'error': str(e)}

    def search_library_symbols(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for symbols in libraries."""
        try:
            query = params.get('query')
            if not query:
                return {'success': False, 'error': 'query parameter required'}

            library = params.get('library')
            limit = params.get('limit', 20)

            symbols = self.symbol_cache.search_symbols(query, library, limit)
            
            symbol_results = []
            for symbol in symbols:
                symbol_results.append({
                    'lib_id': symbol.lib_id,
                    'name': symbol.name,
                    'library': symbol.library,
                    'description': symbol.description,
                    'reference_prefix': symbol.reference_prefix,
                    'pin_count': len(symbol.pins)
                })

            return {
                'success': True,
                'count': len(symbol_results),
                'symbols': symbol_results
            }
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return {'success': False, 'error': str(e)}

    def add_library_path(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a custom library path."""
        try:
            library_path = params.get('library_path')
            if not library_path:
                return {'success': False, 'error': 'library_path parameter required'}

            success = self.symbol_cache.add_library_path(library_path)
            
            if success:
                return {
                    'success': True,
                    'message': f'Added library: {library_path}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to add library: {library_path}'
                }
        except Exception as e:
            logger.error(f"Error adding library: {e}")
            return {'success': False, 'error': str(e)}

    def process_commands(self):
        """Main command processing loop."""
        logger.info("Starting command processing loop")
        
        try:
            for line in sys.stdin:
                try:
                    # Parse command
                    request = json.loads(line.strip())
                    command = request.get('command')
                    params = request.get('params', {})
                    request_id = request.get('id')

                    # Execute command
                    if command in self.handlers:
                        result = self.handlers[command](params)
                    else:
                        result = {
                            'success': False,
                            'error': f'Unknown command: {command}'
                        }

                    # Send response
                    response = {
                        'id': request_id,
                        'result': result
                    }
                    
                    print(json.dumps(response))
                    sys.stdout.flush()

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON input: {e}")
                    error_response = {
                        'id': None,
                        'error': f'Invalid JSON: {e}'
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()

                except Exception as e:
                    logger.error(f"Error processing command: {e}")
                    logger.debug(traceback.format_exc())
                    error_response = {
                        'id': request.get('id') if 'request' in locals() else None,
                        'error': str(e)
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Fatal error in command processing: {e}")
            logger.debug(traceback.format_exc())
        finally:
            logger.info("Command processing stopped")


def main():
    """Main entry point."""
    interface = MCPInterface()
    interface.process_commands()


if __name__ == '__main__':
    main()