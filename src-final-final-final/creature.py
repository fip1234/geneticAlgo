##creature.py

import genome 
from xml.dom.minidom import getDOMImplementation
from enum import Enum
import numpy as np

class MotorType(Enum):
    PULSE = 1
    SINE = 2

class Motor:
    def __init__(self, control_waveform, control_amp, control_freq):
        if control_waveform <= 0.5:
            self.motor_type = MotorType.PULSE
        else:
            self.motor_type = MotorType.SINE
        self.amp = control_amp
        self.freq = control_freq
        self.phase = 0
    

    def get_output(self):
        self.phase = (self.phase + self.freq) % (np.pi * 2)
        if self.motor_type == MotorType.PULSE:
            if self.phase < np.pi:
                output = 1
            else:
                output = -1
            
        if self.motor_type == MotorType.SINE:
            output = np.sin(self.phase)
        
        return output 

class Creature:
    def __init__(self, gene_count):
        self.spec = genome.Genome.get_gene_spec()
        self.dna = genome.Genome.get_random_genome(len(self.spec), gene_count)
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.start_position = None
        self.last_position = None
        #start
        self.max_height = None
        #end

    def get_flat_links(self):
        if self.flat_links == None:
            gdicts = genome.Genome.get_genome_dicts(self.dna, self.spec)
            self.flat_links = genome.Genome.genome_to_links(gdicts)
        return self.flat_links
    
    def get_expanded_links(self):
        self.get_flat_links()
        if self.exp_links is not None:
            return self.exp_links
        
        exp_links = [self.flat_links[0]]
        genome.Genome.expandLinks(self.flat_links[0], 
                                self.flat_links[0].name, 
                                self.flat_links, 
                                exp_links)
        self.exp_links = exp_links
        return self.exp_links

    def to_xml(self):
        self.get_expanded_links()
        domimpl = getDOMImplementation()
        adom = domimpl.createDocument(None, "start", None)
        robot_tag = adom.createElement("robot")
        for link in self.exp_links:
            robot_tag.appendChild(link.to_link_element(adom))
        first = True
        for link in self.exp_links:
            if first:# skip the root node! 
                first = False
                continue
            robot_tag.appendChild(link.to_joint_element(adom))
        robot_tag.setAttribute("name", "pepe") #  choose a name!
        return '<?xml version="1.0"?>' + robot_tag.toprettyxml()

    def get_motors(self):
        self.get_expanded_links()
        if self.motors == None:
            motors = []
            for i in range(1, len(self.exp_links)):
                l = self.exp_links[i]
                m = Motor(l.control_waveform, l.control_amp,  l.control_freq)
                motors.append(m)
            self.motors = motors 
        return self.motors 

    def update_position(self, pos):
        if self.start_position == None:
            self.start_position = pos
        else:
            self.last_position = pos
#start   
        #track max height (z coordinate)
        if self.max_height is None:
            #pos2= zcoordinate(height)
            self.max_height =pos[2]

        else:
            self.max_height =max(self.max_height, pos[2]) 
    #replace get_distance_travelled with tracking max height instead
    #return max z coord reached
    
    def get_max_height(self):
        if self.max_height ==None:
            return 0
        return self.max_height
    
    #check how close movement to centre is
    def get_horizontal_progress(self):
        if self.start_position is None or self.last_position is None:
            return 0
        
    #distance from mountain center at start
        start_dist = np.sqrt(self.start_position[0]**2 + self.start_position[1]**2)
        #distance from mountain center at end
        end_dist = np.sqrt(self.last_position[0]**2 + self.last_position[1]**2)
        
        #positive value if closer to center  
        return start_dist - end_dist
    

    #FITNESS FUNC
    #consider height and horizontal progress 
    def get_fitness(self):
        if self.last_position is None:
            return 0
        
        #get current positiom 
        x, y, z = self.last_position
        
        #distance from mountain center (0,0)
        distance_from_center = np.sqrt(x**2 + y**2)
        
        #height gained (minus starting height of 0.5 sandbox floor)
        height_reached = max(0, self.get_max_height() - 0.5)
        
        #ANTI CHEAT - max reasonable height before penalty
        max_allowed_height = 6.0
        
        if height_reached > max_allowed_height:
            #penalise excessive height
            return 0
        
        #ANTI-CHEAT: must move toward mountain to get height credit
        #pythag
        start_dist = np.sqrt(self.start_position[0]**2 + self.start_position[1]**2)
        if distance_from_center >= start_dist - 0.5: #has it moved to mountain
            #smallreward based on horizontal progress only
            fitness = (start_dist - distance_from_center) * 2 
        else:
            #within 4 units from mountain center
            if distance_from_center < 4:
                #close to mountain = big reward for height  *10
                fitness = height_reached *10 + (start_dist - distance_from_center) *3
            else:
                #far from mountain = small reward for height  *2
                fitness = height_reached *2  + (start_dist - distance_from_center) *3
        
        return max(0, fitness)
#ed
    def update_dna(self, dna):
        self.dna = dna
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.start_position = None
        self.last_position = None
        self.max_height = None

#START
#FIXED CREATURE- only motor evolves

class FixedCreature(Creature):
#START    
    FIXED_STRUCTURE = [
        #gene 0: body- fixed
        [0.5, 0.5, 0.15, 0.0, 0.4, 0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5],
        
        #gene 1:thigh 1
        [0.5, 3.0, 0.10, 0.0, 0.3, 0.5, 0.0, 0.5, 0.0, 1.0, 0.0, 0.15, 0.0, 0.15, 0.5, 0.8, 0.5],
        #gene 2:shin 1
        [0.5, 3.5, 0.08, 0.0, 0.2, 0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.6, 0.0, 0.0, 0.5, 0.8, 0.5],
        
        #gene 3:thigh 2
        [0.5, 3.0, 0.10, 0.0, 0.3, 0.5, 0.0, 0.5, 1.57, 1.0, 0.0, 0.15, 0.0, 0.15, 0.5, 0.8, 0.5],
        #gene 4:shin 2
        [0.5, 3.5, 0.08, 0.0, 0.2, 0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.6, 0.0, 0.0, 0.5, 0.8, 0.5],
        
        #gene 5:thigh 3
        [0.5, 3.0, 0.10, 0.0, 0.3, 0.5, 0.0, 0.5, 3.14, 1.0, 0.0, -0.15, 0.0, 0.15, 0.5, 0.8, 0.5],
        #gene 6:shin 3
        [0.5, 3.5, 0.08, 0.0, 0.2, 0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.6, 0.0, 0.0, 0.5, 0.8, 0.5],
        
        #gene 7:thigh 4
        [0.5, 3.0, 0.10, 0.0, 0.3, 0.5, 0.0, 0.5, 4.71, 1.0, 0.0, -0.15, 0.0, 0.15, 0.5, 0.8, 0.5],
        #gene 8:shin 4
        [0.5, 3.5, 0.08, 0.0, 0.2, 0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.6, 0.0, 0.0, 0.5, 0.8, 0.5],
    ]
    #end
    
    def __init__(self, gene_count=None):
        #creature with fixed morphology but random motor genes
        self.spec = genome.Genome.get_gene_spec()
#start       
        #start with fixed structure using above  
        self.dna = [np.array(gene) for gene in self.FIXED_STRUCTURE]
        
        #randomize motor control genes (14,15,16) only
        for gene in self.dna:
            #control-waveform
            gene[14] = np.random.random()
            #control-amp
            gene[15] = np.random.random()
            #control-freq
            gene[16] = np.random.random()
#end
        
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.start_position = None
        self.last_position = None
        self.max_height = None

#start
    @staticmethod
    def mutate_motor_only(genome, mutation_rate=0.1 ):
        new_dna=[]
        for gene in genome:
            #dont modify og gene
            new_gene =gene.copy()
            #mutating only motor parts
            for i in [14, 15, 16]:
                if np.random.random() <mutation_rate:
                    #if mutation- assign randome vale to i
                    new_gene[i] = np.random.random()
            new_dna.append(new_gene)
        return new_dna

#END