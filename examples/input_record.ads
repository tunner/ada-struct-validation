with Interfaces;

package Input_Record is

   -- Enumerations
   type Status_Type   is (Idle, Running, Paused, Completed);
   type Sensor_Kind   is (Temperature, Pressure, Accelerometer, Gyroscope, Humidity);

   subtype Small_String is String (1 .. 32);

   -- Date/Time types
   type Date is record
      Year  : Integer range 1900 .. 2100;
      Month : Integer range 1 .. 12;
      Day   : Integer range 1 .. 31;
   end record;

   type Time_Of_Day is record
      Hour   : Integer range 0 .. 23;
      Minute : Integer range 0 .. 59;
      Second : Integer range 0 .. 59;
   end record;

   type Timestamp is record
      D : Date;
      T : Time_Of_Day;
   end record;

   -- Calibration and flags
   type Calibration is record
      Offset : Float;
      Scale  : Float;
      Valid  : Boolean;
   end record;

   type Sensor_Flags is record
      Active        : Boolean;
      Faulted       : Boolean;
      Needs_Service : Boolean;
   end record;

   -- Arrays
   type Sample_Array     is array (Positive range <>) of Float;
   type Thresholds_Array is array (Positive range <>) of Float;

   -- Maintenance log
   type Maintenance_Record is record
      TimeStamp  : Timestamp;
      Notes : String (1 .. 40);
   end record;
   type Maintenance_Log is array (Positive range <>) of Maintenance_Record;

   -- Subtype of primitive and array
   subtype Byte is Interfaces.Unsigned_8;
   type Byte_Array is array (Positive range <>) of Byte;

   -- Sensor-level record
   type Sensor_Data is record
      ID          : Integer;
      Kind        : Sensor_Kind;
      Reading     : Float;
      Unit_Code   : Integer;
      Flags       : Sensor_Flags;
      Calibration : Calibration;
      Samples     : Sample_Array (1 .. 16);
      History     : Maintenance_Log (1 .. 3);
      Raw_Bytes   : Byte_Array (1 .. 8); -- New byte array field
   end record;

   type Sensor_Array is array (Positive range <>) of Sensor_Data;

   -- Channel record
   type Channel is record
      Channel_ID : Integer;
      Enabled    : Boolean;
      Thresholds : Thresholds_Array (1 .. 3);
      Attached   : Sensor_Array (1 .. 2);
   end record;
   type Channel_Array is array (Positive range <>) of Channel;

   -- Version, power, and network
   type Version is record
      Major : Integer;
      Minor : Integer;
      Patch : Integer;
   end record;

   type Power_Info is record
      Voltage     : Float;
      Current     : Float;
      Temperature : Float;
   end record;

   type Network_Config is record
      IPv4 : String (1 .. 15);
      Port : Integer range 0 .. 65535;
   end record;

   -- Top-level device record
   type Device is record
      Name       : Small_String;
      State      : Status_Type;
      Version    : Version;
      Power      : Power_Info;
      Sensors    : Sensor_Array  (1 .. 6);
      Channels   : Channel_Array (1 .. 4);
      Network    : Network_Config;
      Error_Code : Integer;
   end record;

end Input_Record;