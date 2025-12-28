import creature 
import numpy as np

class Population:
    def __init__(self, pop_size, gene_count):
        self.creatures = [creature.Creature(
                          gene_count=gene_count) 
                          for i in range(pop_size)]

    @staticmethod
    def get_fitness_map(fits):
        fitmap = []
        total = 0
        for f in fits:
            total = total + f
            fitmap.append(total)
        return fitmap
    
    @staticmethod
    def select_parent(fitmap):
        r = np.random.rand() # 0-1
        r = r * fitmap[-1]
        for i in range(len(fitmap)):
            if r <= fitmap[i]:
                return i

###################################
class FixedPopulation(Population):
    """Population where only motor controls evolve"""
    
    def __init__(self, pop_size):
        self.creatures = [creature.FixedCreature() 
                         for i in range(pop_size)]
    
    def evolve(self, mutation_rate=0.1):
        """Evolve only motor parameters"""
        fits = [c.get_fitness() for c in self.creatures]
        fitmap = Population.get_fitness_map(fits)
        
        new_creatures = []
        for i in range(len(self.creatures)):
            # Select two parents
            p1_ind = Population.select_parent(fitmap)
            p2_ind = Population.select_parent(fitmap)
            
            # Crossover motor genes only
            dna1 = self.creatures[p1_ind].dna
            dna2 = self.creatures[p2_ind].dna
            
            new_dna = []
            for gene1, gene2 in zip(dna1, dna2):
                new_gene = gene1.copy()
                # Crossover only motor control genes
                for i in [14, 15, 16]:
                    if np.random.random() < 0.5:
                        new_gene[i] = gene2[i]
                new_dna.append(new_gene)
            
            # Mutate motor genes only
            new_dna = creature.FixedCreature.mutate_motor_only(
                new_dna, mutation_rate)
            
            new_creature = creature.FixedCreature()
            new_creature.update_dna(new_dna)
            new_creatures.append(new_creature)
        
        self.creatures = new_creatures


############################