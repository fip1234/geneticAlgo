#start. view_elite.py
#quickly view specific elite creature from csv
import mountain_sim
import creature
import genome

#load 99
filename = 'elite_99.csv'

dna = genome.Genome.from_csv(filename)

#create new creature and updates its dna
cr = creature.Creature(1)
cr.update_dna(dna)

print("creature has", len(cr.get_expanded_links()), "links")

#show in GUI how many body parts it has
sim = mountain_sim.MountainSim(gui=True)
print("Running simulation...")
sim.run_creature(cr, 2400, show_gui_time=True)

height = cr.get_max_height()
print("Max height reached:", height)

import time
while True:
    time.sleep(1)

    #end