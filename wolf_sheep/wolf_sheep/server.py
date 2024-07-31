import mesa
from .agents import TreePatch, Deer
from .model import WolfDeer

def deer_tree(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Deer:
        portrayal["Shape"] = "wolf_sheep/resources/Deer2.png"
        # https://icons8.com/icon/KF0OkFiqv6Pz/deer
        portrayal["scale"] = 1.2
        portrayal["Layer"] = 1

    elif type(agent) is TreePatch:
        if agent.fully_grown and agent.has_grown:
            portrayal["Shape"] = "wolf_sheep/resources/grown_tree.png"
            # https://icons8.com/icon/18047/oak-tree 
            portrayal["scale"] = 1 
        elif agent.fully_grown:
            portrayal["Shape"] = "wolf_sheep/resources/tree_new.png"
            # https://icons8.com/icon/18047/oak-tree 
            portrayal["scale"] = 3 
        else:
            portrayal["Shape"] = "wolf_sheep/resources/growing_tree.png"
            # https://icons8.com/icon/bocbBHYM4FYd/growing-tree
            portrayal["scale"] = 0.7
        portrayal["Layer"] = 1

    return portrayal

# Graphing for visualisations
canvas_element = mesa.visualization.CanvasGrid(deer_tree, 406, 406, 10150, 10150)
treeChart = mesa.visualization.ChartModule(
    [
        {"Label": "Deer", "Color": "#966919"},     
    ]
)
deerChart = mesa.visualization.ChartModule(
    [
        {"Label": "Fully Grown Trees", "Color": "#00AA00"},
        {"Label": "Juvenile Trees", "Color": "#FF0000"}, 
        {"Label": "Trees Total", "Color": "#000000"}, 
             
    ]
)
Treetype = mesa.visualization.BarChartModule(
    [
        {"Label": "Fully Grown Trees", "Color": "#00AA00"},
        {"Label": "Juvenile Trees", "Color": "#FF0000"}, 
        {"Label": "Trees Total", "Color": "#000000"},
    ]
    
)

TreeDeath = mesa.visualization.BarChartModule(
    [   
        {"Label": "Other Death", "Color": "#00AA00"},
        {"Label": "Antler Damage", "Color": "#FF0000"}, 
        {"Label": "Deer Grazing", "Color": "#000000"},
    ]
)

DeerDeath = mesa.visualization.BarChartModule(
    [   
        {"Label": "Population Control", "Color": "#A55453"},
        {"Label": "No Energy", "Color": "#53A59A"}, 
        {"Label": "Fawn Mortality", "Color": "#B6983D"},
        {"Label": "Deer Mortality", "Color": "#8BAB6A"},
    ]
)  


model_params = {
    # Parameters visualisation
    "title": mesa.visualization.StaticText("Parameters:"),
    "tree": mesa.visualization.Checkbox("Tree Enabled", True),
    "initial_deer": mesa.visualization.Slider("Initial Deer Population", 5, 1,25),
    "initial_patch": mesa.visualization.Slider("Initial Amount of Trees", 36550, 10000, 50000),
    "population_control":mesa.visualization.Slider("Population Control Rate", 0.0006839, 0.0000001, 1.0, 0.0000001),
    "deer_reproduce": mesa.visualization.Slider("Deer Reproduction Rate", 0.004505, 0.000001, 1.0, 0.000001),
    "deer_mortality":mesa.visualization.Slider("Deer Mortality Rate", 0.0002189, 0.0000001, 1.0, 0.0000001),
    "deer_required_energy": mesa.visualization.Slider("Deer Gain From Juvenile Trees", 1345, 1, 2500),
    "tree_regrowth_time": mesa.visualization.Slider("Tree Regrowth Time", 731, 500, 1000), 
    "tree_natural_mortality":mesa.visualization.Slider("Tree Mortality Rate", 0.00002052, 0.00000001, 1.0, 0.00000001),
}

server = mesa.visualization.ModularServer(
    WolfDeer, [canvas_element, treeChart, deerChart, Treetype, TreeDeath, DeerDeath], "Deer-Tree Grazing", model_params
)
server.port = 8521

