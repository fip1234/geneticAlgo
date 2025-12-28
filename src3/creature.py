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

#start   
    def update_position(self, pos):
        if self.start_position == None:
            self.start_position = pos
        else:
            self.last_position = pos

        #track maximum height (z coordinate)
        if self.max_height is None:
            #pos2= zcoordinate(height)
            self.max_height = pos[2]
        else:
            self.max_height = max(self.max_height, pos[2])
    #replace get_distance_travelled with tracking max height instead
    #return max z coord reached
    
    def get_max_height(self):
        if self.max_height == None:
            return 0
        return self.max_height
    


    ################################

    def get_horizontal_progress(self):
        """Calculate how much closer creature moved to mountain center (0,0)"""
        if self.start_position is None or self.last_position is None:
            return 0
        
        # Distance from mountain center at start
        start_dist = np.sqrt(self.start_position[0]**2 + self.start_position[1]**2)
        # Distance from mountain center at end
        end_dist = np.sqrt(self.last_position[0]**2 + self.last_position[1]**2)
        
        # Positive value = moved closer to mountain center
        return start_dist - end_dist
    
    def get_fitness(self):
        """
        Simple fitness: reward climbing, penalize jumping
        """
        if self.last_position is None:
            return 0
        
        # Get current position
        x, y, z = self.last_position
        
        # Distance from mountain center (0,0)
        distance_from_center = np.sqrt(x**2 + y**2)
        
        # Height gained (minus starting height of 0.5)
        height_gained = max(0, self.get_max_height() - 0.5)
        
        # ANTI-CHEAT: If too high without being near center = JUMPING, not climbing
        # Creatures start at x=6, should move toward x=0 to climb
        max_allowed_height = 3.0  # Maximum reasonable climbing height
        
        if height_gained > max_allowed_height:
            # Penalize excessive height
            return 0
        
        # ANTI-CHEAT: Must move toward mountain to get height credit
        start_dist = np.sqrt(self.start_position[0]**2 + self.start_position[1]**2)
        if distance_from_center >= start_dist - 0.5:
            # Hasn't moved toward mountain, so no height credit
            fitness = (start_dist - distance_from_center) * 2  # Small reward for moving closer
        else:
            # Has moved toward mountain, reward height based on proximity
            if distance_from_center < 4:
                # Close to mountain = big height reward
                fitness = height_gained * 10 + (start_dist - distance_from_center) * 3
            else:
                # Far from mountain = small height reward
                fitness = height_gained * 2 + (start_dist - distance_from_center) * 3
        
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