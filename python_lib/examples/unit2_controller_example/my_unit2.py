from unit2_controller import Unit2

def main():
    # Create a Unit2 object    
    unit2 = Unit2('config.yaml')

    # Test the pump
    for id in unit2.pump.get_device_ids():
        if unit2.pump.move_liquid(device_id=id, millilitre=1.0, direction=1):
            print(f"moved 1 ml liquid in Pump {id} in direction 1")
        else:
            raise Exception(f"Failed to move liquid in Pump {id}")
        if unit2.pump.move_liquid_by_steps(device_id=id, steps=-48):
            print(f"moved liquid by 48 steps in Pump {id} in direction -1")
        else:
            raise Exception(f"Failed to move liquid by steps in Pump {id}")

    # Test the valve
    for id in unit2.valve.get_device_ids():
        if unit2.valve.open(device_id=id) and unit2.valve.is_open(device_id=id):
            print(f"opened Valve {id}")
        else:
            raise Exception(f"Failed to open Valve {id}")
        
        if unit2.valve.close(device_id=id) and not unit2.valve.is_open(device_id=id):
            print(f"closed Valve {id}")
        else:
            raise Exception(f"Failed to close Valve {id}")
        
        opened = unit2.valve.open(device_id=id)
        if unit2.valve.toggle(device_id=id) and not opened:
            print(f"toggled Valve {id}")
        else:
            raise Exception("Failed to toggle Valve {id}")
    
    # Close the connection
    unit2.disconnect()
    
if __name__ == "__main__":
    main()
    