#!/usr/bin/env python3
"""
Ada Validation Function Generator

This tool parses Ada specification files (.ads) and generates validation functions
for record types that check the validity of all fields using Ada's 'Valid attribute.

Author: Luca Corletto
License: MIT
"""

import re
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AdaField:
    """Represents a field in an Ada record."""
    name: str
    type_name: str
    is_array: bool = False
    array_bounds: Optional[str] = None


@dataclass
class AdaRecord:
    """Represents an Ada record type."""
    name: str
    fields: List[AdaField]


class AdaParser:
    """Parser for Ada specification files."""
    
    def __init__(self):
        self.types: Dict[str, AdaRecord] = {}
        self.enums: List[str] = []
        self.array_types: Dict[str, str] = {}  # Maps array type names to their element types
        self.subtypes: Dict[str, str] = {}     # Maps subtype names to their base types
        
    def parse_file(self, file_path: str) -> None:
        """Parse an Ada specification file."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Remove comments and normalize whitespace
        content = self._remove_comments(content)
        content = self._normalize_whitespace(content)
        
        # Parse type definitions
        self._parse_types(content)
    
    def _remove_comments(self, content: str) -> str:
        """Remove Ada comments from the content."""
        lines = content.split('\n')
        result = []
        for line in lines:
            comment_pos = line.find('--')
            if comment_pos != -1:
                line = line[:comment_pos]
            result.append(line)
        return '\n'.join(result)
    
    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace in the content."""
        # Replace multiple spaces with single space
        content = re.sub(r'\s+', ' ', content)
        # Clean up semicolons and line breaks
        content = re.sub(r'\s*;\s*', ';\n', content)
        return content
    
    def _parse_types(self, content: str) -> None:
        """Parse type definitions from the content."""
        # Find enumeration types
        enum_pattern = r'type\s+(\w+)\s+is\s*\([^)]+\)\s*;'
        for match in re.finditer(enum_pattern, content, re.IGNORECASE):
            self.enums.append(match.group(1))
        
        # Find subtype definitions
        subtype_pattern = r'subtype\s+(\w+)\s+is\s+([^;]+)\s*;'
        for match in re.finditer(subtype_pattern, content, re.IGNORECASE):
            subtype_name = match.group(1)
            base_type = match.group(2).strip()
            # Extract base type name (handle constraints like "String (1 .. 32)")
            base_match = re.match(r'(\w+)', base_type)
            if base_match:
                self.subtypes[subtype_name] = base_match.group(1)

        # Find array types
        array_pattern = r'type\s+(\w+)\s+is\s+array\s*\([^)]+\)\s+of\s+(\w+)\s*;'
        for match in re.finditer(array_pattern, content, re.IGNORECASE):
            array_type_name = match.group(1)
            element_type = match.group(2)
            self.array_types[array_type_name] = element_type
        
        # Find record types
        record_pattern = r'type\s+(\w+)\s+is\s+record\s+(.*?)\s+end\s+record\s*;'
        for match in re.finditer(record_pattern, content, re.IGNORECASE | re.DOTALL):
            type_name = match.group(1)
            record_body = match.group(2)
            fields = self._parse_record_fields(record_body)
            self.types[type_name] = AdaRecord(type_name, fields)
    
    def _parse_record_fields(self, record_body: str) -> List[AdaField]:
        """Parse fields from a record body."""
        fields = []
        
        # Split by semicolons to get individual field declarations
        field_declarations = [decl.strip() for decl in record_body.split(';') if decl.strip()]
        
        for decl in field_declarations:
            if ':' not in decl:
                continue
                
            # Parse field declaration: "field_name : type_spec"
            parts = decl.split(':', 1)
            if len(parts) != 2:
                continue
                
            field_name = parts[0].strip()
            type_spec = parts[1].strip()
            
            # Check if it's an array type
            is_array = False
            array_bounds = None
            
            # Handle array syntax: Type_Name (bounds) or String (bounds)
            array_match = re.match(r'(\w+)\s*\(([^)]+)\)', type_spec)
            if array_match:
                base_type = array_match.group(1)
                bounds = array_match.group(2)
                
                # All constrained types with bounds are arrays
                is_array = True
                array_bounds = bounds
                type_name = base_type
            else:
                type_name = type_spec
                
            # After initial parsing, check if this is an array type
            if not is_array:
                # Check if the type name itself is a direct array type
                if type_name in self.array_types:
                    is_array = True
                # Check if this type is a subtype of an array type or String
                elif type_name in self.subtypes:
                    base_subtype = self.subtypes[type_name]
                    if base_subtype in self.array_types or base_subtype == 'String':
                        # This is a subtype of an array type or String, so it should be treated as an array
                        is_array = True
            
            fields.append(AdaField(field_name, type_name, is_array, array_bounds))
        
        return fields


class ValidationGenerator:
    """Generates Ada validation functions."""
    
    def __init__(self, parser: AdaParser):
        self.parser = parser
    
    def _generate_record_validation(self, record: AdaRecord, base_path: str, output_lines: List[str], indent_level: int = 1) -> None:
        """Recursively generate validation for a record and its nested arrays."""
        indent = "   " * indent_level
        
        for field in record.fields:
            field_path = f"{base_path}.{field.name}"
            
            if field.is_array:
                # Handle nested arrays
                loop_var = f"i_{field.name}_{indent_level}"
                output_lines.append(f"{indent}for {loop_var} in {field_path}'Range loop")
                
                # Resolve element type - handle both direct array types and subtypes of array types
                element_type = field.type_name
                if field.type_name in self.parser.array_types:
                    element_type = self.parser.array_types[field.type_name]
                elif field.type_name == 'String':
                    # String arrays have Character elements
                    element_type = 'Character'
                elif field.type_name in self.parser.subtypes:
                    # Check if this subtype resolves to String or an array type
                    base_subtype = self.parser.subtypes[field.type_name]
                    if base_subtype == 'String':
                        element_type = 'Character'
                    elif base_subtype in self.parser.array_types:
                        element_type = self.parser.array_types[base_subtype]
                
                # Check if array element is a record type
                if element_type in self.parser.types:
                    # Recursively generate validation for nested record
                    nested_record = self.parser.types[element_type]
                    self._generate_record_validation(nested_record, f"{field_path}({loop_var})", output_lines, indent_level + 1)
                else:
                    # Simple type in array
                    output_lines.append(f"{indent}   Valid := Valid AND {field_path}({loop_var})'Valid;")
                
                output_lines.append(f"{indent}end loop;")
                output_lines.append("")
            else:
                # Simple field - check if it's a nested record
                if field.type_name in self.parser.types:
                    # Nested record - recursively validate its fields
                    nested_record = self.parser.types[field.type_name]
                    self._generate_record_validation(nested_record, field_path, output_lines, indent_level)
                else:
                    # Simple field
                    output_lines.append(f"{indent}Valid := Valid AND {field_path}'Valid;")

    def generate_validation_function(self, type_name: str) -> str:
        """Generate a validation function for the given type."""
        if type_name not in self.parser.types:
            raise ValueError(f"Type '{type_name}' not found in parsed types")
        
        record = self.parser.types[type_name]
        
        # Generate function signature
        function_code = f"function Is_Valid (Input : {type_name}) return Boolean is\n"
        function_code += "   Valid : Boolean;\n"
        function_code += "begin\n"
        function_code += "   Valid := True;\n\n"
        
        # Use recursive validation generation
        all_code = []
        self._generate_record_validation(record, "Input", all_code, 1)
        
        # Join all the generated code
        if all_code:
            function_code += "\n".join(all_code)
        
        function_code += "\n   return Valid;\n"
        function_code += f"end Is_Valid;\n"
        
        return function_code
    
    def generate_adb_file(self, type_name: str, package_name: str) -> str:
        """Generate a complete .adb file with the validation function."""
        function_body = self.generate_validation_function(type_name)
        
        adb_content = f"-- Generated validation function for {type_name}\n"
        adb_content += f"-- This file contains a validation function template\n\n"
        adb_content += f"-- Add this function to your package body:\n\n"
        adb_content += function_body
        
        return adb_content


def main():
    """Main entry point for the tool."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python ada_validator_generator.py <ada_spec_file> [type_name]")
        sys.exit(1)
    
    ada_file = sys.argv[1]
    specified_type = sys.argv[2] if len(sys.argv) == 3 else None
    
    if not Path(ada_file).exists():
        print(f"Error: File '{ada_file}' not found")
        sys.exit(1)
    
    # Parse the Ada file
    parser = AdaParser()
    try:
        parser.parse_file(ada_file)
    except Exception as e:
        print(f"Error parsing Ada file: {e}")
        sys.exit(1)
    
    # Show available types
    if not parser.types:
        print("No record types found in the file")
        sys.exit(1)
    
    print("Found the following record types:")
    for i, type_name in enumerate(parser.types.keys(), 1):
        print(f"  {i}. {type_name}")
    
    # Select type to validate
    if specified_type:
        if specified_type not in parser.types:
            print(f"Error: Type '{specified_type}' not found in the file")
            print("Available types:")
            for type_name in parser.types.keys():
                print(f"  - {type_name}")
            sys.exit(1)
        choice = specified_type
    else:
        # Ask user to select type interactively
        while True:
            try:
                choice = input("\nEnter the name of the type to validate: ").strip()
                if choice in parser.types:
                    break
                print(f"Type '{choice}' not found. Please choose from the list above.")
            except KeyboardInterrupt:
                print("\nAborted.")
                sys.exit(0)
    
    # Generate validation function
    generator = ValidationGenerator(parser)
    
    try:
        # Extract package name from file
        package_name = Path(ada_file).stem
        adb_content = generator.generate_adb_file(choice, package_name)
        
        # Write to output file
        output_file = f"{choice.lower()}_validation.adb"
        with open(output_file, 'w') as f:
            f.write(adb_content)
        
        print(f"\nValidation function generated successfully!")
        print(f"Output written to: {output_file}")
        
    except Exception as e:
        print(f"Error generating validation function: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()