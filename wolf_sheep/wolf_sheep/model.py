"""
Deer-Tree Grazing Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

import mesa
import decimal

from .agents import TreePatch, Deer
from .scheduler import RandomActivationByTypeFiltered

class WolfDeer(mesa.Model): #Name retained as WolfDeer due to server connection
    """
    Deer-Tree Grazing Model
    """
    #initialization
    height = 406
    width = 406
    initial_deer = 5
    initial_patch = 36550
    deer_reproduce = 0.004505
    deer_mortality = 0.0002189
    fawn_mortality = 0.0009576
    population_control = 0.0006839
    tree_natural_mortality = 0.00002052
    tree = False
    tree_regrowth_time = 731
    verbose = False                                            
    
    #Food and energy allocations
    deer_required_energy = 1345                                 
    deer_food_pool = initial_deer * deer_required_energy        
    tree_total_health = initial_deer * deer_required_energy     
    
    #Tree death type counters
    tree_natural_death_count = 0
    tree_antler_death_count = 0
    tree_eaten_death_count = 0
    
    #Deer death type counters
    deer_population_control_death_count = 0
    deer_energy_death_count = 0
    fawn_mortality_death_count = 0
    deer_mortality_death_count = 0

    description = (
        "A model for simulating deer and tree grazing  modelling."
    )

    def __init__(
        self,
        width=406,
        height=406,
        initial_deer=5,
        deer_reproduce=0.004505,
        deer_mortality=0.0002189,
        fawn_mortality = 0.0009576,
        population_control=0.0006839,
        tree_natural_mortality=0.00002052,
        tree=False,
        tree_regrowth_time=731,
        deer_required_energy=1345,
        initial_patch=36550,
        deer_food_pool = initial_deer * deer_required_energy,
        tree_total_health = initial_deer * deer_required_energy
    ):
        """
        Create a new Deer-Tree Grazing model with the given parameters.

        Args:
            initial_deer: Number of deer to start with
            initial_patch: Number of trees to start with
            deer_reproduce: Possiblity per time step for reprodcuction
            deer_mortality:Possiblity per time step for deer death due to deer mortality
            fawn_mortality: Possiblity per time step for fawn death due to fawn mortality
            population_control: Possiblity per time step for deer death due to population control
            tree_natural_mortality: Possiblity per time step for tree death due to tree mortality
            tree: Check for if active object is of type Tree
            tree_regrowth_time: Maximum time taken for a tree to reach fully grown
            deer_required_energy: Average deer food requirement per time step
            deer_food_pool: Deer daily collective food pool based on deer food requirements
            tree_total_health: Tree daily collective health pool based on deer food requirements
            
            
        """
        super().__init__()
        self.width = width
        self.height = height
        self.initial_deer = initial_deer
        self.deer_reproduce = deer_reproduce
        self.deer_mortality = deer_mortality
        self.fawn_mortality = fawn_mortality
        self.population_control = population_control
        self.tree_natural_mortality = tree_natural_mortality
        self.tree = tree
        self.tree_regrowth_time = tree_regrowth_time
        self.deer_required_energy = deer_required_energy
        self.initial_patch = initial_patch
        self.deer_food_pool = deer_food_pool
        self.tree_total_health = tree_total_health
        
        #Collection of data for tracking and visualisations
        self.schedule = RandomActivationByTypeFiltered(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        self.datacollector = mesa.DataCollector(
            {
                "Deer": lambda m: m.schedule.get_type_count(Deer),
                "Fully Grown Trees": lambda m: m.schedule.get_type_count(
                    TreePatch, lambda x: x.fully_grown
                ),
                "Juvenile Trees": lambda m: m.schedule.get_type_count(
                    TreePatch, lambda x: not x.fully_grown
                ),
                "Trees Total": lambda m: m.schedule.get_type_count(
                    TreePatch, lambda x: x.fully_grown) + m.schedule.get_type_count(
                    TreePatch, lambda x: not x.fully_grown),
                "Other Death": lambda m: m.tree_natural_death_count,
                "Antler Damage": lambda m: m.tree_antler_death_count,
                "Deer Grazing": lambda m: m.tree_eaten_death_count,
                
                "Population Control": lambda m: m.deer_population_control_death_count,
                "No Energy": lambda m: m.deer_energy_death_count,
                "Fawn Mortality": lambda m: m.fawn_mortality_death_count,
                "Deer Mortality": lambda m: m.deer_mortality_death_count,
                
            }
        )

        # Initialization of tree patches
        if self.tree:
            
            #Allocation of grown vs juvenile trees
            noGrown = 11550
            noJuven = 25000
            for i in range(noGrown):
                
                fully_grown = True
               
                #Assigned tree health and regrowth time
                countdown = self.tree_regrowth_time
                health = round(decimal.Decimal((decimal.Decimal(18.267) * decimal.Decimal(1.0063198**(731)))) *10 , 0)
               
                placed = False
                
                #Find a suitable spot to place the tree
                while placed == False:
                    x = self.random.randrange(self.width)
                    y = self.random.randrange(self.height)
                    while self.grid[x][y] != []:
                        x = self.random.randrange(self.width)
                        y = self.random.randrange(self.height)
                        
                    blocks = self.grid.get_neighborhood((x, y), True)

                    placed = True  
                    for i in blocks:
                        if i != (x, y) or i != (x-1, y+1) or i != (x+1, y-1):
                            if not self.grid.is_cell_empty(i):
                                placed = False

                patch = TreePatch(self.next_id(), (x, y), self, True, fully_grown, False, False, countdown, health)
            
                self.grid.place_agent(patch, (x, y))
                self.schedule.add(patch)
             
            #Steps are largely repeated for each Juvenile except for countdown and grown variables   
            for i in range(noJuven):
                fully_grown = False
                  
                #Assigned tree health and regrowth time       
                countdown = self.random.randrange(365, self.tree_regrowth_time)
                daysAlive = 731 - countdown
                health = round(decimal.Decimal((decimal.Decimal(18.267) * decimal.Decimal(1.0063198**(daysAlive)))) *10, 0)
                
                treepos = []    
                
                for x in self.agents:
                    if isinstance(x, TreePatch):
                        if x.fully_grown:
                            treepos.append(x.pos)
                
                placed = False
                
                while placed == False:
                    x = self.random.randrange(self.width)
                    y = self.random.randrange(self.height)
                    while self.grid[x][y] != []:
                        x = self.random.randrange(self.width)
                        y = self.random.randrange(self.height)
                        
                    blocks = self.grid.get_neighborhood((x, y), True)

                    placed = True  
                    for i in blocks:
                        if i != (x, y) or i != (x-1, y+1) or i != (x+1, y-1):
                            if i in treepos:
                                placed = False

                patch = TreePatch(self.next_id(), (x, y), self, True, fully_grown, False, False, countdown, health)
                
                self.grid.place_agent(patch, (x, y))
                self.schedule.add(patch)
        
        
        # Create deer and place randomly amongst the grid
        for i in range(self.initial_deer):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2*self.deer_required_energy)
            deer = Deer(self.next_id(), (x, y), self, True, False, False, energy)
            self.grid.place_agent(deer, (x, y))
            self.schedule.add(deer)   

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        
        #Summary created for the run to collect results
        
        if (self.schedule.steps) == 0:
            f = open("Results.txt", "w")
            f.write(
                "Initial number deer: " + str(self.schedule.get_type_count(Deer)) + "\n" + 
                "Initial number grown tree: " + str(self.schedule.get_type_count(TreePatch, lambda x: x.fully_grown))  + "\n" + 
                "Initial number juvenile tree: " + str(self.schedule.get_type_count(TreePatch, lambda x: not x.fully_grown)) + "\n" +
                "Initial population control: " + str(self.population_control) + "\n" +
                "Initial deer food req: " + str(self.deer_required_energy) + "\n" +
                "Dimensions: " + str(self.height)+"x"+str(self.width) + "\n" + "\n"
            )
        
        if (self.schedule.steps) == 730:     
            f = open("Results.txt", "a")
            f.write( "Final number deer: " + str(self.schedule.get_type_count(Deer)) + "\n" +
                    "Final number grown tree: " + str(self.schedule.get_type_count(TreePatch, lambda x: x.fully_grown)) + "\n" +
                    "Final number juvenile tree: " + str(self.schedule.get_type_count(TreePatch, lambda x: not x.fully_grown)) + "\n" +
                    "\n" +
                    "Tree Natural Death: " + str(self.tree_natural_death_count) + "\n" +
                    "Tree Antler Death: " + str(self.tree_antler_death_count) + "\n" +
                    "Tree Eaten Death: " + str(self.tree_eaten_death_count) + "\n" +
                    "\n" +
                    "Population Control Deaths: " + str(self.deer_population_control_death_count) + "\n" +
                    "Deer Energy Death: " + str(self.deer_energy_death_count) + "\n" +
                    "Fawn Mortality Death: " + str(self.fawn_mortality_death_count) + "\n" +
                    "Deer Mortality Death: " + str(self.deer_mortality_death_count)             
            )
            f.close()
            exit()
        
        #Ensure food pool is a regularly updated value based on current amount of deers
        self.deer_food_pool =  self.schedule.get_type_count(Deer) * self.deer_required_energy
        
        
        #Begin process of trees being eaten by collecting list eligible trees
        treelist = []    
        
        for x in self.agents:
            if isinstance(x, TreePatch):
                if not x.fully_grown:
                    treelist.append(x)
        
        self.tree_total_health = self.schedule.get_type_count(Deer) * self.deer_required_energy
        
        #Trees that can die due to being frayed by antlers
        treelist2 = []
        for x in self.agents:
            if isinstance(x, TreePatch):
                if not x.fully_grown or x.has_grown:
                    if x.health > 0:
                        treelist2.append(x)

        #Deer food gain from additional sources removed from tree health 
        other_food_percent = self.random.randrange(9, 11)/100 
        other_food_source = self.tree_total_health * other_food_percent
        self.tree_total_health -= decimal.Decimal(other_food_source)
        
        #While energy pool still available, select random trees to lose health due to being eaten
        while self.tree_total_health > 0 and treelist != []:
            eaten = self.random.randrange(self.deer_required_energy)
            self.random.shuffle(treelist)
            #Tree death due to being eaten
            if eaten > treelist[0].health:
                    self.tree_total_health -= treelist[0].health
                    treelist[0].health = 0
                    self.tree_eaten_death_count += 1  
                    treelist.remove(treelist[0])
            else:
                treelist[0].health -= eaten
                self.tree_total_health -= eaten

        #No more available food if there is no trees left 
        if treelist == []:
            self.deer_required_energy = 0
            self.deer_food_pool = 0
        else:
            #Trees can only die due to being frayed during certain times of the year
            if (self.schedule.steps >= 59 and self.schedule.steps <= 242) or (self.schedule.steps >= 425 and self.schedule.steps <= 608): 
                #Tree death due to being frayed
                antler_deaths = int(round(((3.3 * self.schedule.get_type_count(Deer, lambda x: not x.fawn)) * (0.15 + 0.0222 * self.schedule.get_type_count(Deer, lambda x: not x.fawn))), 0))
                self.tree_antler_death_count += antler_deaths
                self.random.shuffle(treelist2)
                if len(treelist2)>0:  
                    for i in range(antler_deaths):
                        treelist2[i].health = 0         
                        treelist2.remove(treelist2[0])

        #Model scheduler 
        self.schedule.step()
        self.datacollector.collect(self)
        if self.verbose:
            print(
                [
                    self.schedule.time,
                    self.schedule.get_type_count(Deer),
                    self.schedule.get_type_count(TreePatch, lambda x: x.fully_grown),
                    self.schedule.get_type_count(TreePatch, lambda x: not x.fully_grown),
                ]
            )
        
    #Run the model
    def run_model(self, step_count=731):
        if self.verbose:
            print("Initial number deer: ", self.schedule.get_type_count(Deer))
            print(
                "Initial number grown tree: ",
                self.schedule.get_type_count(TreePatch, lambda x: x.fully_grown))
            print(  
                "Initial number juvenile tree: ",
                self.schedule.get_type_count(TreePatch, lambda x: not x.fully_grown))

        for i in range(step_count):
            print(i)
            self.step()

        if self.verbose:
            print("")
            print("Final number deer: ", self.schedule.get_type_count(Deer))
            print(
                "Final number grown tree: ",
                self.schedule.get_type_count(TreePatch, lambda x: x.fully_grown))
            print(
                "Final number juvenile tree: ",
                self.schedule.get_type_count(TreePatch, lambda x: not x.fully_grown))