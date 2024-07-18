# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!  WARNING  AVERTISSEMENT  警告  предупреждение  !!
# !!       Potential DAMAGE to your equipment      !!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Before running this script, make sure you confirm the default current
# value of the pumps is correctly set to the operating current of the pumps 
# in the configuration file.
# Otherwise, the motor and the PCB may be damaged.


import os
import time
from unit2_controller import Unit2

def get_script_path():
    return os.path.dirname(__file__)

def main():
    config_file = os.path.join(get_script_path(), 'config_single_board.yaml')
    # Create a Unit2 object
    unit2 = Unit2(config_file)
    unit2.connect()

    # Start all pumps
    for name, pump in unit2.pump.items():
        if pump.move_liquid(millilitre=10, direction=1):
            print(f"Pump {name} is now moving liquid by 10 ml in direction 1")
        else:
            raise Exception(f"Failed to move liquid in Pump {name}")
        
    # Wait until all pumps are done
    completed = {name: False for name in unit2.pump.keys()}
    while not all(completed.values()):
        for name, pump in unit2.pump.items():
            if completed[name]:
                continue
            if pump.is_done():
                completed[name] = True
                # Unless stall torque is required, turn off the pump to avoid overheating, recommended!
                pump.power_off()
                print(f"Pump {name} is done.")
    
    time.sleep(1)
    # Move one specific pump by steps
    name = "pump1"
    if unit2.pump[name].move_liquid_by_steps(steps=-48):
        print(f"Pump {name} is now moving 48 steps in direction -1")
    else:
        raise Exception(f"Failed to move liquid by steps in Pump {name}")
    unit2.pump["pump1"].wait_until_done()
    unit2.pump["pump1"].power_off()
    print(f"Pump {name} is done.")

    # Test the valve
    for name, valve in unit2.valve.items():
        if valve.open() and valve.is_open():
            print(f"opened Valve {name}")
        else:
            raise Exception(f"Failed to open Valve {name}")
        
        if valve.close() and not valve.is_open():
            print(f"closed Valve {name}")
        else:
            raise Exception(f"Failed to close Valve {name}")
        
        opened = valve.open()
        if valve.toggle() and valve.is_open() != opened:
            print(f"toggled Valve {name}")
        else:
            raise Exception(f"Failed to toggle Valve {name}")
    
    # Close the connection
    unit2.disconnect()
    
if __name__ == "__main__":
    main()
    