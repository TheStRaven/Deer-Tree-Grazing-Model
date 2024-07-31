import mesa
import random
import decimal

from .random_walk import RandomWalker

class Deer(RandomWalker):
    """
    A deer that walks around, reproduces (asexually) and eats juvenile trees.

    The init is the same as the RandomWalker.
    """
    energy = None

    def __init__(self, unique_id, pos, model, moore, fawn, reproducible, energy=None): 
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy                #current energy
        self.fawn = fawn                    #if they are a fawn set True
        self.reproducible = reproducible    #if meet the requirements to have a chance to reproduce set true
    
    def step(self):
        """
        A model step. Move, then eat tree and reproduce if requirements met.
        """
        coordinates = []
        for x in range(self.model.width):
            for y in range(self.model.height):
                coordinates.append((x, y))
    
        living = True
                 
        self.random_move(coordinates)       #Random move out of all possible movements
        self.energy -= int(1345/4)          #Lose energy for their movement   
        
        
        
        #reproduction requirements
        self.reproducible = False
        if (self.model.schedule.steps >= 90 and self.model.schedule.steps <= 180) or (self.model.schedule.steps >= 456 and self.model.schedule.steps <= 546):
            self.reproducible = True
        
        
        treelist = []    
        
        for x in self.model.agents:
            if isinstance(x, TreePatch):
                if not x.fully_grown and x.health > 0:
                    treelist.append(x)
               
        #Calculate food taken out of food pool and assigned to any deer
        if self.model.deer_food_pool > 0 and treelist != []:          
            tenper = int(self.model.deer_required_energy * 0.1)
            gain = self.model.random.randrange(self.model.deer_required_energy - tenper, self.model.deer_required_energy + tenper)
            
            # Deer cant have over 50% excess energy (1.5*1345)
            if self.energy >= 1345:         
                gain = 0
                
            if gain >= self.model.deer_food_pool:
                self.energy += self.model.deer_food_pool
                self.model.deer_food_pool = 0
            else:
                self.model.deer_food_pool -= gain
                self.energy += gain
   
        
        # Death if energy = 0
        if self.energy < 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            living = False
            self.model.deer_energy_death_count +=1
         
         
        #Have a chance at reproduction if requirements met
        if self.reproducible:
            if living and self.random.random() < self.model.deer_reproduce:
                if([self.pos] != [None]):
                    neighbor_cells = self.model.grid.get_neighborhood(self.pos, True)
                    emptycells = []
                    
                    for i in neighbor_cells:
                        if self.model.grid[i[0]][i[1]] == []:
                            emptycells.append(i)

                    if emptycells != []:
                        place = random.choice(emptycells)
                        fawnEnergy = self.energy / 2
                        fawn = Deer(self.model.next_id(), place, self.model, self.moore, True, False, fawnEnergy)
                        self.model.grid.place_agent(fawn, place)
                        self.model.schedule.add(fawn)   
                        
                #75% chance a deer producing a second deer if already giving birth
                if self.random.random() < 0.75:
                    if([self.pos] != [None]):
                        neighbor_cells = self.model.grid.get_neighborhood(self.pos, True)
                        emptycells = []
                        for i in neighbor_cells:
                            if self.model.grid[i[0]][i[1]] == []:
                                emptycells.append(i)

                        if emptycells != []:
                            place = random.choice(emptycells)
                            fawnEnergy = self.energy / 2
                            fawn = Deer(self.model.next_id(), place, self.model, self.moore, True, False, fawnEnergy)
                            self.model.grid.place_agent(fawn, place)
                            self.model.schedule.add(fawn)
       
        #Chance of dying due to deer mortality rate
        if (not self.fawn and living and self.random.random() < self.model.deer_mortality):
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                living = False
                self.model.deer_mortality_death_count +=1
                
        #Chance of dying due to fawn mortality rate
        if (self.fawn and living and self.random.random() < self.model.fawn_mortality):
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                living = False
                self.model.fawn_mortality_death_count +=1

        #Chance of dying due to population control
        if living and self.random.random() < self.model.population_control:
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                living = False
                self.model.deer_population_control_death_count +=1


class TreePatch(mesa.Agent):
    """
    A juvenile tree that grows at a fixed rate and it is eaten by deer
    """

    def __init__(self, unique_id, pos, model, moore, fully_grown, has_grown, frayable, countdown, health):
        """
        Creates a new tree     
        """
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown      #Fully grown tree
        self.has_grown = has_grown          #Has achieved fully grown status during duration of run
        self.frayable = frayable            #Has the possibility of being frayed
        self.countdown = countdown          #Countdown until fully grown if juvenile
        self.health = health                #Overall health of the tree
        self.pos = pos                      
        self.moore = moore                  

    """
    A model step. Grow, be eaten and/or die.
    """
    def step(self):
        
        #Juvenile trees will become grown if countdown is 0, otherwise remain Juvenile and die if health reaches 0
        if not self.fully_grown:
            if self.countdown <= 0:
                self.fully_grown = True
                self.has_grown = True
                self.countdown = self.model.tree_regrowth_time  
        #Pass will allow the tree to gain no health and will thus die at the end of the step
            elif self.health == 0:
               pass                         
            else:
                self.countdown -= 1
                dayAlive = 731-self.countdown
                self.health += round(decimal.Decimal((decimal.Decimal(18.267) * decimal.Decimal(1.0063198**(dayAlive))) - (decimal.Decimal(18.267) * decimal.Decimal(1.0063198**(dayAlive-1)))) * 10, 0)

        # Tree Death due to being eaten or being frayed(difference tracked within model.py) 
        if (self.health <= 0):
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
                        
        # Tree Natural Death due to mortality
        elif (self.random.random() < self.model.tree_natural_mortality):
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.tree_natural_death_count += 1
        


