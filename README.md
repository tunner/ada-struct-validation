# Ada Structure Validation Generator

Generates Ada validation functions that check all fields using the `'Valid` attribute.

## Usage

```bash
# Interactive mode
python3 ada_validator_generator.py <file.ads>

# Direct mode  
python3 ada_validator_generator.py <file.ads> <type_name>

# Custom input variable name
python3 ada_validator_generator.py <file.ads> <type_name> --input My_Device
python3 ada_validator_generator.py <file.ads> <type_name> -i Device_A
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
   Valid := True;
   
   for i_Name_1 in Input.Name'Range loop
      Valid := Valid AND Input.Name(i_Name_1)'Valid;
   end loop;
   
   for i_Sensors_1 in Input.Sensors'Range loop
      Valid := Valid AND Input.Sensors(i_Sensors_1).ID'Valid;
      -- ... validates all nested fields and arrays
   end loop;
   
   return Valid;
end Is_Valid;
```

With custom input name (`--input My_Device`):
```ada
function Is_Valid (My_Device : Device) return Boolean is
   Valid : Boolean;
begin
   Valid := True;
   
   for i_Name_1 in My_Device.Name'Range loop
      Valid := Valid AND My_Device.Name(i_Name_1)'Valid;
   end loop;
   
   return Valid;
end Is_Valid;
```

## Features

- Nested records and arrays
- Character-by-character string validation
- Array subtypes and direct array types
- Customizable input parameter names
- Ada 2005 compatible  
- Enumeration support