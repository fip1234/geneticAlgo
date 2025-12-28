#mountain_sim.py
# 
import pybullet as p
import simulation
import numpy as np
import population
import genome
import creature
import random
import math
import time
import plot


#inherit from base simulation class
class MountainSim(simulation.Simulation):
    #start- added gui option 
    def __init__(self, sim_id=0, gui=False):
        if gui:
            self.physicsClientId =p.connect(p.GUI)
            #set camera so not zoomed in
            p.resetDebugVisualizerCamera(
                cameraDistance=25,
                cameraYaw=45,  
                cameraPitch=-30,
                cameraTargetPosition=[0, 0, 0],
                physicsClientId=self.physicsClientId
            )            
        else:
            self.physicsClientId =p.connect(p.DIRECT)
        self.sim_id =sim_id
    #end
    #start- added physicsClientId=pid for clarity
    def make_mountain(self,num_rocks=100, max_size=0.25, arena_size=10, mountain_height=5):
        pid = self.physicsClientId
        def gaussian(x, y, sigma=arena_size/4):
            """Return the height of the mountain at position (x, y) using a Gaussian function."""
            return mountain_height * math.exp(-((x**2 + y**2) / (2 * sigma**2)))

        for _ in range(num_rocks):
            x = random.uniform(-1 * arena_size/2, arena_size/2)
            y = random.uniform(-1 * arena_size/2, arena_size/2)
            z = gaussian(x, y)  # Height determined by the Gaussian function

            # Adjust the size of the rocks based on height. Higher rocks (closer to the peak) will be smaller.
            size_factor = 1 - (z / mountain_height)
            size = random.uniform(0.1, max_size) * size_factor

            orientation = p.getQuaternionFromEuler([random.uniform(0, 3.14), random.uniform(0, 3.14), random.uniform(0, 3.14)])
            rock_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[size, size, size], physicsClientId=pid)
            rock_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[size, size, size], rgbaColor=[0.5, 0.5, 0.5, 1], physicsClientId=pid)
            rock_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=rock_shape, baseVisualShapeIndex=rock_visual, basePosition=[x, y, z], baseOrientation=orientation, physicsClientId=pid)
    
    #start- added physicsClientId=pid for clarity
    def make_rocks(self, num_rocks=100, max_size=0.25, arena_size=10):
        pid = self.physicsClientId
        for _ in range(num_rocks):
            x = random.uniform(-1 * arena_size/2, arena_size/2)
            y = random.uniform(-1 * arena_size/2, arena_size/2)
            z = 0.5  # Adjust based on your needs
            size = random.uniform(0.1,max_size)
            orientation = p.getQuaternionFromEuler([random.uniform(0, 3.14), random.uniform(0, 3.14), random.uniform(0, 3.14)])
            rock_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[size, size, size],physicsClientId=pid)
            rock_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[size, size, size], rgbaColor=[0.5, 0.5, 0.5, 1], physicsClientId=pid)
            rock_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=rock_shape, baseVisualShapeIndex=rock_visual, basePosition=[x, y, z], baseOrientation=orientation, physicsClientId=pid)


    #start- added physicsClientId=pid for clarity
    def make_arena(self,arena_size=10, wall_height=1):
        pid = self.physicsClientId
        wall_thickness = 0.5
        floor_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, arena_size/2, wall_thickness], physicsClientId=pid)
        floor_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, arena_size/2, wall_thickness], rgbaColor=[1, 1, 0, 1],physicsClientId=pid)
        floor_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=floor_collision_shape, baseVisualShapeIndex=floor_visual_shape, basePosition=[0, 0, -wall_thickness],physicsClientId=pid)

        wall_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, wall_thickness/2, wall_height/2],physicsClientId=pid)
        wall_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, wall_thickness/2, wall_height/2], rgbaColor=[0.7, 0.7, 0.7, 1],physicsClientId=pid)  # Gray walls

        # Create four walls
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[0, arena_size/2, wall_height/2],physicsClientId=pid)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[0, -arena_size/2, wall_height/2],physicsClientId=pid)

        wall_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, halfExtents=[wall_thickness/2, arena_size/2, wall_height/2],physicsClientId=pid)
        wall_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, halfExtents=[wall_thickness/2, arena_size/2, wall_height/2], rgbaColor=[0.7, 0.7, 0.7, 1],physicsClientId=pid)  # Gray walls

        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[arena_size/2, 0, wall_height/2],physicsClientId=pid)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[-arena_size/2, 0, wall_height/2],physicsClientId=pid)


    def run_creature(self, cr, iterations=2400, show_gui_time=False):
        pid = self.physicsClientId
        p.resetSimulation(physicsClientId=pid)
        p.setPhysicsEngineParameter(enableFileCaching=0, physicsClientId=pid)

        p.setGravity(0, 0, -10, physicsClientId=pid)
        
        #mountain envioronment instead of flat plane 
        #load arena
        arena_size = 20
        self.make_arena(arena_size=arena_size)

        #load mountain
        #CHECK PATH!!!!
        mountain_position = (0, 0, -1)  # Adjust as needed
        mountain_orientation = p.getQuaternionFromEuler((0, 0, 0))
        #start
        p.setAdditionalSearchPath('src/shapes/')
        #end
        # mountain = p.loadURDF("mountain.urdf", mountain_position, mountain_orientation, useFixedBase=1)
        # mountain = p.loadURDF("mountain_with_cubes.urdf", mountain_position, mountain_orientation, useFixedBase=1)
        #start
        mountain = p.loadURDF("gaussian_pyramid.urdf", mountain_position, mountain_orientation, useFixedBase=1,physicsClientId=pid)
        #end

        #TEST 1!!!!l[8, 0, 2.5]
        # oad creature at edge of arena so doesnt fly
        xml_file = 'temp' + str(self.sim_id) + '.urdf'
        xml_str = cr.to_xml()
        with open(xml_file, 'w') as f:
            f.write(xml_str)
        
        cid = p.loadURDF(xml_file, physicsClientId=pid)

        p.resetBasePositionAndOrientation(cid, [0, 0, 2.5], [0, 0, 0, 1], physicsClientId=pid)


        for step in range(iterations):
            p.stepSimulation(physicsClientId=pid)
            if step % 24 == 0:
                self.update_motors(cid=cid, cr=cr)

            pos, orn = p.getBasePositionAndOrientation(cid, physicsClientId=pid)
            cr.update_position(pos)
            #print(pos[2])
            #print(cr.get_distance_travelled())

            if show_gui_time:
                time.sleep(1.0/240)


#run Genetic Algorithm
if __name__ == "__main__":
    pop = population.Population(pop_size=10, gene_count=3)
    sim = MountainSim()

    best_creature = None
    best_fitness = 0

    #start
    generation_list = []
    best_fitness_list = []
    mean_fitness_list = []
    #end

#from test_ga_no_thread.py
    for iteration in range(5):
        #run each creature in sim
        for cr in pop.creatures:
            sim.run_creature(cr, 2400) 

        #sim.eval_population(pop, 2400)
        #calculate fitnesses using distance travelled - CHANGE
        fits = [cr.get_max_height() 
                for cr in pop.creatures]
        links = [len(cr.get_expanded_links()) 
                for cr in pop.creatures]

        #start
        generation_list.append(iteration)
        best_fitness_list.append(np.max(fits))
        mean_fitness_list.append(np.mean(fits))
        #end

        print(iteration, "fittest:", np.round(np.max(fits), 3), 
                "mean:", np.round(np.mean(fits), 3), "mean links", np.round(np.mean(links)), "max links", np.round(np.max(links)))       
        
        fit_map = population.Population.get_fitness_map(fits)
        new_creatures = []

        for i in range(len(pop.creatures)):
            p1_ind = population.Population.select_parent(fit_map)
            p2_ind = population.Population.select_parent(fit_map)
            p1 = pop.creatures[p1_ind]
            p2 = pop.creatures[p2_ind]
            # now we have the parents!
            dna = genome.Genome.crossover(p1.dna, p2.dna)
            dna = genome.Genome.point_mutate(dna, rate=0.1, amount=0.25)
            dna = genome.Genome.shrink_mutate(dna, rate=0.25)
            dna = genome.Genome.grow_mutate(dna, rate=0.1)
            cr = creature.Creature(1)
            cr.update_dna(dna)
            new_creatures.append(cr)

        # elitism
        max_fit = np.max(fits)
        for cr in pop.creatures:
            if cr.get_max_height() == max_fit:
                new_cr = creature.Creature(1)
                new_cr.update_dna(cr.dna)
                new_creatures[0] = new_cr
                filename = "elite_"+str(iteration)+".csv"
                genome.Genome.to_csv(cr.dna, filename)
                #start
                print("saved elite to", filename)
        
                # save best creature overall
                if max_fit > best_fitness:
                    best_fitness = max_fit
                    best_creature = creature.Creature(1)
                    best_creature.update_dna(cr.dna)
                break
        pop.creatures = new_creatures

# MOVE PLOTTING HERE - AFTER THE LOOP (NOT INSIDE)
print("evolution complete! :)")  
print("best fitness:", best_fitness)

# USE plot (not plot_results) since you imported plot
plot.plot_fitness(generation_list, best_fitness_list, mean_fitness_list,
                    filename='src/fitness_evolution.png')
plot.save_table(generation_list, best_fitness_list, mean_fitness_list,
                filename='src/results.csv')

# Show best in GUI
print("\nShowing best creature in GUI...")
gui_sim = MountainSim(gui=True)
gui_sim.run_creature(best_creature, 2400, show_gui_time=True)
print("Demo complete!")
while True:
    time.sleep(1)
#end