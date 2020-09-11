from networkx.drawing.nx_pydot import write_dot;
import networkx as nx
import sys

n = int(sys.argv[1])
gridSize = 2*n*n
hop = 2*n

G = nx.DiGraph()
idx = 0
for i in range(0, gridSize, 2):

    # Connecting MULi to respective SUMi
    G.add_edge(i, i+1)
    # Propagating SUMi to it's bottom neighbor 
    if i+1+hop < gridSize:
        G.add_edge(i+1, i+1+hop)
    # Propagating from MULi to MULi+1
    if i%hop != hop-2:
        G.add_edge(i, i+2)

    G.nodes[i]["label"] = "mult"+str(idx)
    G.nodes[i+1]["label"] = "sum"+str(idx)
    idx+=1



# Getting graph specs
V = G.number_of_nodes()
E = G.number_of_edges()
operands = V//2
inputs = [ str(i) for i in range(0, gridSize, hop) ]
outputs = [ str(i) for i in range(gridSize-hop, gridSize, 2) ]

# Making your life easier with a simple output format
name = str(n) + "x" + str(n) + "-systolic_array"
inputs = " ".join(inputs)
outputs = " ".join(outputs)

write_dot(G, name + ".dot")
nx.write_edgelist(G, name + ".txt", data=False)
with open(name + ".txt", 'r') as original: data = original.read()
with open(name + ".txt", 'w') as modified: modified.write( str(V) + " " + str(E) + "\n"
                                                         + str(operands) + "\n\n" 
                                                         + data + "\n" 
                                                         + inputs + "\n"
                                                         + outputs + "\n")
