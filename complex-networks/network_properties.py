import sys
import numpy as np
import seaborn as sns
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection
from networkx.drawing.nx_pydot import read_dot, write_dot
from networkx.algorithms import approximation, centrality, maximal_independent_set

table1hop = [[0,  0,  0,  1,  1,  2,  2,  3,  3,  4,  4,  5,  5,  6,  6,  7,  7,  8],  
             [0,  1,  1,  2,  2,  3,  3,  4,  4,  5,  5,  6,  6,  7,  7,  8,  8,  9],  
             [0,  1,  1,  2,  2,  3,  3,  4,  4,  5,  5,  6,  6,  7,  7,  8,  8,  9],  
             [1,  2,  2,  3,  3,  4,  4,  5,  5,  6,  6,  7,  7,  8,  8,  9,  9, 10],  
             [1,  2,  2,  3,  3,  4,  4,  5,  5,  6,  6,  7,  7,  8,  8,  9,  9, 10],  
             [2,  3,  3,  4,  4,  5,  5,  6,  6,  7,  7,  8,  8,  9,  9, 10, 10, 11],  
             [2,  3,  3,  4,  4,  5,  5,  6,  6,  7,  7,  8,  8,  9,  9, 10, 10, 11],  
             [3,  4,  4,  5,  5,  6,  6,  7,  7,  8,  8,  9,  9, 10, 10, 11, 11, 12],  
             [3,  4,  4,  5,  5,  6,  6,  7,  7,  8,  8,  9,  9, 10, 10, 11, 11, 12],  
             [4,  5,  5,  6,  6,  7,  7,  8,  8,  9,  9, 10, 10, 11, 11, 12, 12, 13],  
             [4,  5,  5,  6,  6,  7,  7,  8,  8,  9,  9, 10, 10, 11, 11, 12, 12, 13],  
             [5,  6,  6,  7,  7,  8,  8,  9,  9, 10, 10, 11, 11, 12, 12, 13, 13, 14],  
             [5,  6,  6,  7,  7,  8,  8,  9,  9, 10, 10, 11, 11, 12, 12, 13, 13, 14],  
             [6,  7,  7,  8,  8,  9,  9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15],  
             [6,  7,  7,  8,  8,  9,  9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15],  
             [7,  8,  8,  9,  9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16],  
             [7,  8,  8,  9,  9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16],
             [8,  9,  9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17]]

def color(G, metric, cap, color):
    
    if isinstance(metric, dict) == False:
        for node in metric:
            if node > cap:
                G.nodes[node]["fillcolor"] = color

    # For non-binary metrics
    else:
        for node in G:
            if metric[node] == cap:
                G.nodes[node]["style"] = "filled"
                G.nodes[node]["fillcolor"] = color + "4"

            elif metric[node] >= (cap*0.75):
                G.nodes[node]["style"] = "filled"
                G.nodes[node]["fillcolor"] = color + "3"

            elif metric[node] >= (cap*0.5):
                G.nodes[node]["style"] = "filled"
                G.nodes[node]["fillcolor"] = color + "1"

def normalize(values, maxValue):

    for i,val in values.items():
        values[i] = (val/maxValue)**2

def getBetweness(G, normalized):

    betweness = nx.betweenness_centrality(G)
    if not normalized:
        return betweness

    max_betweness = betweness[ max(betweness, key=betweness.get) ]
    
    normalize(betweness, max_betweness)
    color(G, betweness, 1, "lightsteelblue")

    return betweness

def getClosenessCentrality(G, normalized):

    closeness_centrality = centrality.closeness_centrality(G);
    if not normalized:
        return closeness_centrality

    max_closeness = closeness_centrality[ max(closeness_centrality, key=closeness_centrality.get) ]
    
    normalize(closeness_centrality, max_closeness)
    print(closeness_centrality)
    color(G, closeness_centrality, 1, "olivedrab")

    return closeness_centrality

def getDominatingSet(G):
    
    G2 = nx.Graph(G)
    dominating_set = approximation.min_weighted_dominating_set(G2)
    
    for dom in dominating_set:
        G.nodes[dom]["shape"] = "box"

    return dominating_set

def getSubgraphCentrality(G, normalized):
    
    G2 = nx.Graph(G)
    subgraph_centr = centrality.subgraph_centrality(G2)
    if not normalized:
        return subgraph_centrality

    max_subcentr = subgraph_centr[ max(subgraph_centr, key=subgraph_centr.get) ]
    
    normalize(subgraph_centr, max_subcentr)
    color(G, subgraph_centr, 1, "mediumorchid")

    return subgraph_centr

def buildWires(G,labels,n):

    # Drawing edges of costy neighbors
    points = []
    edges = []
    idx = 0
    for i, (u,v) in enumerate(G.edges):
        
        # Get coordinates from each vertex in the final grid (placement)
        x1,y1 = map(int, np.where(labels==u))
        x2,y2 = map(int, np.where(labels==v))

        distManhattanI = abs(x2 - x1)
        distManhattanJ = abs(y2 - y1)
        
        hopCost = table1hop[distManhattanI][distManhattanJ]

        if hopCost > 0:
            # Each vertex is now considered a point
            points.append((x1,y1))
            points.append((x2,y2))
            
            # Index of connected points
            edges.append( (idx, idx +1) )
            idx += 2
    
    # Adjusting lines to start and end at the center of the cells
    for i,val in enumerate(points):
        (a,b) = val
        a += 0.5;
        b += 0.5;
        points[i] = (b,a)

    if len(edges) > 0: 
        points = np.asarray(points)
        edges = np.asarray(edges)
        # Adding wires to the plot
        lc = LineCollection(points[edges], colors="red")
        plt.gca().add_collection(lc)
        #for i in range(len(points)):
        #    (x,y) = points[i]
        #    plt.plot(a,b)
        

def placementHeatmap(G, fileName, strategy, prop, binaryProp = set()):

    n,data = 0, []
    with open("placements/" + strategy + "/" + fileName + "_p.txt", "r") as file:
        for line in file.readlines():
            n += 1
            for num in line.split():
                data.append(int(num))

    labels = np.asarray(data).reshape(n,n)
    
    # +1 offset is used to create a unique color (0) for 255
    for i, num in enumerate(data):
        data[i] = prop[num]+1 if num!=255 else 0
    
    # HEATMAPs
    placement = np.asarray(data).reshape(n,n)
    
    ax = sns.heatmap(placement, cmap="YlGnBu", annot=labels, fmt="d")
    
    # Inverting color map for betweness
    #cmap = sns.cm.rocket_r
    #ax = sns.heatmap(placement, cmap=cmap, annot=labels, fmt="d")
    
    buildWires(G,labels,n)
    
    if len(binaryProp) > 0:
        for i in range(n):
            for j in range(n):
                if labels[i][j] in binaryProp:
                    # Patch object implements x left(0) -> right(n-1) and y top(0) -> down(n-1), hence (j,i)
                    ax.add_patch(Rectangle((j,i), 1,1, fill=False, edgecolor="red", lw=3))
    
    plt.savefig(fileName + "-" + strategy)
    plt.close()

def remove_attributes(G):
    for node in G:
        G.nodes[node].pop("label", None)
        G.nodes[node].pop("opcode", None)

    for (u,v, attributes) in G.edges(data=True):
        attributes.clear()


# -------------------- ENTRY POINT -------------------- #


# Building graph and removing attributes
fileName = sys.argv[1]
strategy = sys.argv[2]
G = read_dot(fileName);
G = nx.DiGraph( nx.convert_node_labels_to_integers(G) )
remove_attributes(G)

#Slicing string to get rid of file path
i = sys.argv[1].rfind("/") + 1
fileName = sys.argv[1][i:]
fileName = fileName.split(".")[0]

# Directed graph metrics
bc = getBetweness(G, True)
#cc = getClosenessCentrality(G, True)

## Undirected graph metrics
#subgc = getSubgraphCentrality(G, True)
#print(subgc)
domset = getDominatingSet(G)
print(domset)
print(maximal_independent_set(nx.Graph(G)))
placementHeatmap(G,fileName,strategy, bc)
#write_dot(G, fileName + ".dot")
