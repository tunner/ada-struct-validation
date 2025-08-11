# Ada Structure Validation Generator

Generates Ada validation functions that check all fields using the `'Valid` attribute.

## Usage

```bash
# Interactive mode
python3 ada_validator_generator.py <file.ads>

# Direct mode  
python3 ada_validator_generator.py <file.ads> <type_name>
```

## Example

Input:
```ada
type Device is record
   Name    : String (1 .. 20);
   Sensors : Sensor_Array (1 .. 5);
   Enabled : Boolean;
end record;
```

Generated output:
```ada
function Is_Valid (Input : Device) return Boolean is
   Valid : Boolean;
begin
   Valid := Input.Name'Valid AND Input.Enabled'Valid;
   
   for i_Sensors in Input.Sensors'Range loop
      Valid := Valid AND Input.Sensors(i_Sensors).ID'Valid;
      -- ... validates all nested fields
   end loop;
   
   return Valid;
end Is_Valid;
```

## Features

- Nested records and arrays
- Ada 2005 compatible  
- String types with bounds
- Enumeration support