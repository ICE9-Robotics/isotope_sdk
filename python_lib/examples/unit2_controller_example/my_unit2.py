from unit2_controller import Unit2

def main():
    # Create a Unit2 object    
    unit2 = Unit2('config.yaml')
    unit2.connect()

    # Test the pump
    for name in unit2.pump.get_names():
        if unit2.pump.move_liquid(name=name, millilitre=1.0, direction=1):
            print(f"moved 1 ml liquid in Pump {name} in direction 1")
        else:
            raise Exception(f"Failed to move liquid in Pump {name}")
        if unit2.pump.move_liquid_by_steps(name=name, steps=-48):
            print(f"moved liquid by 48 steps in Pump {name} in direction -1")
        else:
            raise Exception(f"Failed to move liquid by steps in Pump {name}")
        
        # You may also refer to the pump object directly
        pump = unit2.pump[name]
        if pump.move_liquid(name=name, millilitre=1.0, direction=1):
            print(f"moved 1 ml liquid in Pump {name} in direction 1")
        else:
            raise Exception(f"Failed to move liquid in Pump {name}")

    # Test the valve
    for name in unit2.valve.get_names():
        if unit2.valve.open(name=name) and unit2.valve.is_open(name=name):
            print(f"opened Valve {name}")
        else:
            raise Exception(f"Failed to open Valve {name}")
        
        if unit2.valve.close(name=name) and not unit2.valve.is_open(name=name):
            print(f"closed Valve {name}")
        else:
            raise Exception(f"Failed to close Valve {name}")
        
        opened = unit2.valve.open(name=name)
        if unit2.valve.toggle(name=name) and not opened:
            print(f"toggled Valve {name}")
        else:
            raise Exception("Failed to toggle Valve {name}")
        
        # You may also refer to the valve object directly
        valve = unit2.valve[name]
        if valve.open() and valve.is_open():
            print(f"opened Valve {name}")
        else:
            raise Exception(f"Failed to open Valve {name}")
    
    # Close the connection
    unit2.disconnect()
    
if __name__ == "__main__":
    main()
    