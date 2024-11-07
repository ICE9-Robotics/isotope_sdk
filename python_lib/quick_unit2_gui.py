import tkinter as tk
import yaml
from unit2_controller import Unit2

class BreakoutBoardController(tk.Tk):
    def __init__(self, config_file):
        super().__init__()
        self.title("Breakout Board Controller")
        self.geometry('325x400')
        
        self.unit2 = Unit2(config_file)
        self.unit2.connect()
        
        self.create_widgets()
        self.load_config(config_file)
        
    def create_widgets(self):
        tk.Label(self, text="Breakout Board Controller",font=('Arial', 20)).pack()
        tk.Label(self, text="Check the setup in the config file first!").pack()
        tk.Label(self, text="").pack()  # spacing
        
        # Valves
        tk.Label(self, text="Valves",font=('Arial', 18)).pack()
        self.valve_var = tk.StringVar(self)
        self.valve_var.set("valve number")
        self.valve_option = tk.OptionMenu(self, self.valve_var, [])
        self.valve_option.pack()
        tk.Button(self, text="Open valve", command=self.open_valve).pack()
        tk.Button(self, text="Close valve", command=self.close_valve).pack()
        
        tk.Label(self, text="").pack()  # spacing
        
        # Pumps
        tk.Label(self, text="Pumps",font=('Arial', 18)).pack()
        self.pumps_var = tk.StringVar(self)
        self.pumps_var.set("pump number")
        self.pumps_option = tk.OptionMenu(self, self.pumps_var, [])
        self.pumps_option.pack()
        tk.Label(self, text="Number of Steps").pack()
        self.entry_steps = tk.Entry(self)
        self.entry_steps.pack()
        tk.Button(self, text="Run Pump", command=self.run_pump).pack()
        
        tk.Label(self, text="").pack()  # spacing

        tk.Button(self, text="Disconnect board", command=self.disconnect).pack()
    
    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            pump_options = [i['name'] for i in config["pump"]["devices"]]
            valve_options = [i['name'] for i in config["valve"]["devices"]]
        
        self.valve_option['menu'].delete(0, 'end')
        for option in valve_options:
            self.valve_option['menu'].add_command(label=option, command=tk._setit(self.valve_var, option))
        
        self.pumps_option['menu'].delete(0, 'end')
        for option in pump_options:
            self.pumps_option['menu'].add_command(label=option, command=tk._setit(self.pumps_var, option))
    
    def open_valve(self):
        name = int(self.valve_var.get())
        valve = self.unit2.valve[name]
        if valve.open() and valve.is_open():
            print(f"opened Valve {name}")
        else:
            raise Exception(f"Failed to open Valve {name}")
    
    def close_valve(self):
        name = int(self.valve_var.get())
        valve = self.unit2.valve[name]
        if valve.close() and not valve.is_open():
            print(f"closed Valve {name}")
        else:
            raise Exception(f"Failed to close Valve {name}")
    
    def run_pump(self):
        name = int(self.pumps_var.get())
        steps = self.entry_steps.get()
        self.unit2.pump[name].move_liquid_by_steps(steps)
        print(f"pump {name} moving {steps} steps!")
    
    def disconnect(self):
        self.unit2.disconnect()
        self.destroy()
        print("disconnected and exiting")

if __name__ == "__main__":
    app = BreakoutBoardController('config.yaml')
    app.mainloop()
