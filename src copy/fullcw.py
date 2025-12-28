# ga-mountain-simple.py
# This integrates the GA system with the mountain environment
# WITHOUT changing the fitness function yet

import pybullet as p
import pybullet_data
import time
import numpy as np
import random
import creature
import population
import simulation
import genome
import os

# Step 1: Modify the Simulation class to use the mountain environment
class MountainSimulation(simulation.Simulation):
    """
    This is almost identical to your original Simulation class,
    but it loads the mountain environment instead of a flat plane
    """
    def run_creature(self, cr, iterations=2400):
        pid = self.physicsClientId
        p.resetSimulation(physicsClientId=pid)
        p.setPhysicsEngineParameter(enableFileCaching=0, physicsClientId=pid)
        
        # CHANGE 1: Setup mountain environment instead of flat plane
        p.setGravity(0, 0, -10, physicsClientId=pid)
        
        # Load the arena
        arena_size = 20
        self.make_arena(arena_size=arena_size)
        
        # Load the mountain
        script_dir = os.path.dirname(os.path.abspath(__file__))
        p.setAdditionalSearchPath(os.path.join(script_dir, 'shapes/'), physicsClientId=pid)
        mountain = p.loadURDF("gaussian_pyramid.urdf", [0, 0, -1], 
                             p.getQuaternionFromEuler((0, 0, 0)), 
                             useFixedBase=1, physicsClientId=pid)
        
        # CHANGE 2: Load creature at starting position (edge of arena)
        xml_file = 'temp' + str(self.sim_id) + '.urdf'
        xml_str = cr.to_xml()
        with open(xml_file, 'w') as f:
            f.write(xml_str)
        
        cid = p.loadURDF(xml_file, physicsClientId=pid)
        # Start creature at edge of arena, not flying
        p.resetBasePositionAndOrientation(cid, [8, 0, 2.5], [0, 0, 0, 1], physicsClientId=pid)
        
        # Rest is EXACTLY the same as your original code
        for step in range(iterations):
            p.stepSimulation(physicsClientId=pid)
            if step % 24 == 0:
                self.update_motors(cid=cid, cr=cr)
            pos, orn = p.getBasePositionAndOrientation(cid, physicsClientId=pid)
            cr.update_position(pos)
    
    def make_arena(self, arena_size=10, wall_height=1):
        """Copy-pasted from cw-envt.py"""
        wall_thickness = 0.5
        pid = self.physicsClientId
        
        floor_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, 
                                                       halfExtents=[arena_size/2, arena_size/2, wall_thickness],
                                                       physicsClientId=pid)
        floor_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, 
                                                 halfExtents=[arena_size/2, arena_size/2, wall_thickness], 
                                                 rgbaColor=[1, 1, 0, 1],
                                                 physicsClientId=pid)
        floor_body = p.createMultiBody(baseMass=0, 
                                      baseCollisionShapeIndex=floor_collision_shape, 
                                      baseVisualShapeIndex=floor_visual_shape, 
                                      basePosition=[0, 0, -wall_thickness],
                                      physicsClientId=pid)
        
        # Create 4 walls (copy-paste from cw-envt.py)
        wall_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, 
                                                      halfExtents=[arena_size/2, wall_thickness/2, wall_height/2],
                                                      physicsClientId=pid)
        wall_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, 
                                                halfExtents=[arena_size/2, wall_thickness/2, wall_height/2], 
                                                rgbaColor=[0.7, 0.7, 0.7, 1],
                                                physicsClientId=pid)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, 
                         baseVisualShapeIndex=wall_visual_shape, 
                         basePosition=[0, arena_size/2, wall_height/2],
                         physicsClientId=pid)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, 
                         baseVisualShapeIndex=wall_visual_shape, 
                         basePosition=[0, -arena_size/2, wall_height/2],
                         physicsClientId=pid)
        
        wall_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, 
                                                      halfExtents=[wall_thickness/2, arena_size/2, wall_height/2],
                                                      physicsClientId=pid)
        wall_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, 
                                                halfExtents=[wall_thickness/2, arena_size/2, wall_height/2], 
                                                rgbaColor=[0.7, 0.7, 0.7, 1],
                                                physicsClientId=pid)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, 
                         baseVisualShapeIndex=wall_visual_shape, 
                         basePosition=[arena_size/2, 0, wall_height/2],
                         physicsClientId=pid)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, 
                         baseVisualShapeIndex=wall_visual_shape, 
                         basePosition=[-arena_size/2, 0, wall_height/2],
                         physicsClientId=pid)


# Step 2: Run the GA loop (copy-pasted from test_ga_no_threads.py)
if __name__ == "__main__":
    pop = population.Population(pop_size=10, gene_count=3)
    sim = MountainSimulation()  # Use our new mountain simulation!
    
    for iteration in range(100):  # Run fewer generations for testing
        # Run each creature in the mountain environment
        for cr in pop.creatures:
            sim.run_creature(cr, 2400)
        
        # Calculate fitness (still using distance travelled - NOT optimal for mountains yet!)
        fits = [cr.get_distance_travelled() for cr in pop.creatures]
        links = [len(cr.get_expanded_links()) for cr in pop.creatures]
        
    ################################
        #counld change this line
        print(f"Generation {iteration}: fittest={np.round(np.max(fits), 3)}, "
              f"mean={np.round(np.mean(fits), 3)}, mean_links={np.round(np.mean(links))}")
    #################################  
        # Selection and reproduction (exactly the same as before)
        fit_map = population.Population.get_fitness_map(fits)
        new_creatures = []
        
        for i in range(len(pop.creatures)):
            p1_ind = population.Population.select_parent(fit_map)
            p2_ind = population.Population.select_parent(fit_map)
            p1 = pop.creatures[p1_ind]
            p2 = pop.creatures[p2_ind]
            
            dna = genome.Genome.crossover(p1.dna, p2.dna)
            dna = genome.Genome.point_mutate(dna, rate=0.1, amount=0.25)
            dna = genome.Genome.shrink_mutate(dna, rate=0.25)
            dna = genome.Genome.grow_mutate(dna, rate=0.1)
            
            cr = creature.Creature(1)
            cr.update_dna(dna)
            new_creatures.append(cr)
        
        # Elitism: keep the best creature
        max_fit = np.max(fits)
        for cr in pop.creatures:
            if cr.get_distance_travelled() == max_fit:
                new_cr = creature.Creature(1)
                new_cr.update_dna(cr.dna)
                new_creatures[0] = new_cr
                filename = f"elite_{iteration}.csv"
                genome.Genome.to_csv(cr.dna, filename)
                break
        
        pop.creatures = new_creatures
    
    print("Evolution complete!")


    ########################################
    def evaluate_creature(self, cr, iterations=2400):
        # Reset simulation to clear any previous creatures
        p.resetSimulation(physicsClientId=self.physicsClientId)
        p.setPhysicsEngineParameter(enableFileCaching=0, physicsClientId=self.physicsClientId)
        
        # Rebuild the environment (mountain + arena)
        p.setGravity(0, 0, -10, physicsClientId=self.physicsClientId)
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=self.physicsClientId)
        self.make_arena()
        self.load_mountain()
        
        # Save creature DNA to URDF file and load it
        urdf_name = 'test.urdf'
        with open(urdf_name, 'w') as f:
            f.write(cr.to_xml())
        
        # Spawn creature to the side of mountain, at base level
        # [7, 0, 1.5] = 7 units to right, ground level
        creature_id = p.loadURDF(urdf_name, [5, 0, 0.5], physicsClientId=self.physicsClientId)
        
        # Track heights in second half of simulation (after settling)
        heights = []
        
        # Run simulation
        for step in range(iterations):
            p.stepSimulation(physicsClientId=self.physicsClientId)
            
            # Update motors every 24 steps (10 times per second)
            if step % 24 == 0:
                self.update_motors(creature_id, cr)
            
            # Get current position and update tracking
            pos, orn = p.getBasePositionAndOrientation(creature_id, physicsClientId=self.physicsClientId)
            cr.update_position(pos)
            
            # Only track height after first half (step 1200 onwards = last 5 seconds)
            # This ignores initial falling/jumping chaos and rewards sustained position
            if step > iterations // 2:
                heights.append(pos[2])
        
        # Fitness = average sustained height (rewards staying high, not brief peaks)
        average_height = np.mean(heights) if len(heights) > 0 else 0
        return average_height