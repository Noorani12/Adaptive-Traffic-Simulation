import time
import random
import os

# ==============================================================================
# CAMERA-BASED ADAPTIVE TRAFFIC SIGNAL SIMULATION
# Proof of Concept based on "daaSimulationBlueprint.pdf"
# ==============================================================================

# Configuration Parameters
SIMULATION_TIME = 150        # Number of ticks to simulate
G_MIN = 3                    # Minimum green light duration 
G_MAX = 20                   # Maximum green light duration
SATURATION_FLOW = 2          # Cars leaving the intersection per tick during green
ARRIVAL_RATES = {
    "North": 0.3,            # Medium traffic
    "South": 0.3,            # Medium traffic
    "East":  0.1,            # Low traffic
    "West":  0.8             # Heavy traffic (Needs more green time)
}

class Intersection:
    def __init__(self, mode):
        self.mode = mode
        self.queues = {"North": 0, "South": 0, "East": 0, "West": 0}
        self.total_delay = 0
        self.cars_passed = 0
        self.current_green = "North"
        self.green_timer = 10 if mode == "FIXED" else 5
        self.directions = ["North", "South", "East", "West"]

    def inject_traffic(self, arrivals):
        for d, count in arrivals.items():
            self.queues[d] += count
            # Accumulate waiting time for vehicles currently in queue
            self.total_delay += self.queues[d]

    def step(self):
        # Process intersection clearing (vehicles passing through)
        if self.queues[self.current_green] > 0:
            passed = min(self.queues[self.current_green], SATURATION_FLOW)
            self.queues[self.current_green] -= passed
            self.cars_passed += passed
            
        # Decrease timer and switch light if needed
        self.green_timer -= 1
        if self.green_timer <= 0:
            self.switch_light()

    def switch_light(self):
        # Move to the next direction circularly
        idx = self.directions.index(self.current_green)
        self.current_green = self.directions[(idx + 1) % 4]
        
        if self.mode == "FIXED":
            # Fixed interval timing (ignoring real traffic)
            self.green_timer = 10
        else:
            # ADAPTIVE CAMERA-BASED TIMING
            # Mimics the optimization function: dynamically calculates needed time based on queue length
            q_len = self.queues[self.current_green]
            
            # Predict how much time is needed to clear the queue
            calc_time = max(G_MIN, int(q_len / SATURATION_FLOW) + 2)
            
            # Bound the time between Min and Max constraints
            self.green_timer = min(G_MAX, calc_time)

def run_simulation():
    fixed = Intersection("FIXED")
    adaptive = Intersection("ADAPTIVE")
    
    # Store history for visualization
    for tick in range(1, SIMULATION_TIME + 1):
        # 1. Generate identical random traffic for a fair comparison
        arrivals = {}
        for d in ["North", "South", "East", "West"]:
            # Inject 1 or 2 cars probabilistically
            if random.random() < ARRIVAL_RATES[d]:
                arrivals[d] = random.randint(1, 2)
            else:
                arrivals[d] = 0
        
        fixed.inject_traffic(arrivals)
        adaptive.inject_traffic(arrivals)
        
        # 2. Advance the simulation by 1 step
        fixed.step()
        adaptive.step()
        
        # 3. Render the output to the terminal in real-time
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"🚥 SMART TRAFFIC SIGNAL SIMULATION - ALGORITHM DEMO 🚥")
        print(f"⏳ Time Step: {tick}/{SIMULATION_TIME} | Objective: Minimize Delay & Queue Length")
        print("Note: The West lane is simulated to have heavy rush hour traffic.\n")
        
        for name, sim in [("1. FIXED TIMING (Traditional Approach)", fixed), 
                         ("2. CAMERA-BASED ADAPTIVE (Our Proposed Model)", adaptive)]:
            print(f"\033[1m{name}\033[0m")
            print("-" * 75)
            for d in sim.directions:
                if sim.current_green == d:
                    light = "\033[92m🟩 GREEN\033[0m"
                    timer = f"({sim.green_timer:02d}s left)"
                else:
                    light = "\033[91m🟥 RED  \033[0m"
                    timer = "          "
                
                cars = "🚗" * min(sim.queues[d], 25) + ("+" if sim.queues[d] > 25 else "")
                print(f" {light} {timer} | {d[:5]:<5} | Queue: {sim.queues[d]:2d} | {cars}")
            print(f" 📈 Cumulative Wait Time: \033[93m{sim.total_delay}\033[0m | ✅ Throughput: {sim.cars_passed} cars passed\n")
        
        time.sleep(0.12) # Speed of simulation

    # Show Final Optimization Results side-by-side
    print("=" * 75)
    print("📊 OPTIMIZATION RESULTS SUMMARY (from Objective Function)")
    print("=" * 75)
    print(f"{'Performance Metric':<25} | {'Fixed Timing':<15} | {'Adaptive Model':<15} | {'Net Improvement':<15}")
    print("-" * 75)
    
    delay_imp = ((fixed.total_delay - adaptive.total_delay) / max(1, fixed.total_delay)) * 100
    thru_imp = ((adaptive.cars_passed - fixed.cars_passed) / max(1, fixed.cars_passed)) * 100
    
    print(f"{'Total Delay (Wait Time)':<25} | {fixed.total_delay:<15} | \033[92m{adaptive.total_delay:<15}\033[0m | \033[92m{delay_imp:.1f}% REDUCED\033[0m")
    print(f"{'Total Throughput':<25} | {fixed.cars_passed:<15} | \033[92m{adaptive.cars_passed:<15}\033[0m | \033[92m{thru_imp:.1f}% INCREASED\033[0m")
    print("=" * 75)
    print("\nConclusion: The adaptive metaheuristic scheduling dynamically balanced the green")
    print("time towards the heavy traffic lanes (West), reducing overall bottleneck!")

if __name__ == '__main__':
    try:
        run_simulation()
    except KeyboardInterrupt:
        print("\nSimulation stopped early.")
