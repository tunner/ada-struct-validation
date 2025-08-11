package Input_Record is

   --  Enumerations
   type Status_Type   is (Idle, Running, Paused, Completed);
   type Sensor_Kind   is (Temperature, Pressure, Accelerometer, Gyroscope, Humidity);

   --  Helper constrained string
   subtype Small_String is String (1 .. 32);

   --  Simple date/time records (no access, no variants)
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

   --  Calibration and flags
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

   --  Arrays used for samples/thresholds
   type Sample_Array     is array (Positive range <>) of Float;
   type Thresholds_Array is array (Positive range <>) of Float;

   --  Maintenance log entries
   type Maintenance_Record is record
      When  : Timestamp;
      Notes : String (1 .. 40);
   end record;

   type Maintenance_Log is array (Positive range <>) of Maintenance_Record;

   --  Sensor-level record with nested array and sub-records
   type Sensor_Data is record
      ID          : Integer;
      Kind        : Sensor_Kind;
      Reading     : Float;
      Unit_Code   : Integer;  -- e.g. 1=°C, 2=bar, etc.
      Flags       : Sensor_Flags;
      Calibration : Calibration;
      Samples     : Sample_Array (1 .. 16);  -- last 16 raw samples
      History     : Maintenance_Log (1 .. 3); -- last 3 maintenance entries
   end record;

   type Sensor_Array is array (Positive range <>) of Sensor_Data;

   --  Channel record: contains thresholds and a small array of attached sensors
   type Channel is record
      Channel_ID : Integer;
      Enabled    : Boolean;
      Thresholds : Thresholds_Array (1 .. 3);
      Attached   : Sensor_Array (1 .. 2);  -- two sensors per channel
   end record;

   type Channel_Array is array (Positive range <>) of Channel;

   --  Firmware version
   type Version is record
      Major : Integer;
      Minor : Integer;
      Patch : Integer;
   end record;

   --  Simple power telemetry
   type Power_Info is record
      Voltage     : Float;
      Current     : Float;
      Temperature : Float;
   end record;

   --  Network configuration (kept simple and fixed-size)
   type Network_Config is record
      IPv4 : String (1 .. 15);
      Port : Integer range 0 .. 65535;
   end record;

   --  Top-level device record tying everything together
   type Device is record
      Name       : Small_String;
      State      : Status_Type;
      Version    : Version;
      Power      : Power_Info;
      Sensors    : Sensor_Array  (1 .. 6); -- pool of sensors
      Channels   : Channel_Array (1 .. 4); -- processing channels
      Network    : Network_Config;
      Error_Code : Integer;
   end record;

end Input_Record;