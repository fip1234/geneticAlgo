# view_elite.py
import mountain_sim
import creature
import genome

# Load and show a specific elite
filename = 'elite_99.csv'  # Change to any elite file

print(f"Loading {filename}...")
dna = genome.Genome.from_csv(filename)

cr = creature.Creature(1)
cr.update_dna(dna)

print(f"Creature has {len(cr.get_expanded_links())} links")

# Show in GUI
sim = mountain_sim.MountainSim(gui=True)
print("Running simulation...")
sim.run_creature(cr, 2400, show_gui_time=True)

height = cr.get_max_height()
print(f"Max height reached: {height}")

import time
while True:
    time.sleep(1)