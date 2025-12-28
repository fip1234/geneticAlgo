#start 
import unittest
import mountain_sim
import simulation
import creature
import population

class TestSim(unittest.TestCase):
    def testSimExists(self):
        sim = mountain_sim.MountainSim()
        self.assertIsNotNone(sim)


    def testRunExists(self):
        sim = mountain_sim.MountainSim()
        self.assertIsNotNone(sim.run_creature)
#end
#taken from test_simulation.py      
    def testRunCr(self):
        sim = mountain_sim.MountainSim()
        cr = creature.Creature(gene_count = 3)
        sim.run_creature(cr)
        # Check creature has moved
        distance = cr.get_distance_travelled()
        self.assertGreaterEqual(distance, 0)

#start    
    def testInheritsFromSim(self):
        sim = mountain_sim.MountainSim()
        self.assertIsInstance(sim, simulation.Simulation)  
#end
unittest.main()