from unit2_controller import Unit2

def main():
    # Create a Unit2 object    
    unit2 = Unit2('config.yaml')
    unit2.connect()

    # Test the pump
    for name, pump in unit2.pump.items():
        pump = unit2.pump[name]
        if pump.move_liquid(name=name, millilitre=1.0, direction=1):
            print(f"moved 1 ml liquid in Pump {name} in direction 1")
        else:
            raise Exception(f"Failed to move liquid in Pump {name}")
        
        if pump.move_liquid_by_steps(name=name, steps=-48):
            print(f"moved liquid by 48 steps in Pump {name} in direction -1")
        else:
            raise Exception(f"Failed to move liquid by steps in Pump {name}")

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
        if valve.toggle() and not opened:
            print(f"toggled Valve {name}")
        else:
            raise Exception(f"Failed to toggle Valve {name}")
    
    # Close the connection
    unit2.disconnect()
    
if __name__ == "__main__":
    main()
    