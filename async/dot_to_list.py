import sys
import networkx as nx
from networkx.drawing.nx_pydot import write_dot
from networkx.drawing.nx_pydot import read_dot

fileName = sys.argv[1]
outputPath = sys.argv[2]

if outputPath[-1] != "/":
    outputPath += "/"

# Slicing path to get the file name
i = sys.argv[1].rfind("/") + 1
outputFile = sys.argv[1][i:]


# Building graph and converting string names like 0_2_1 to integers while keeping the topology
G = read_dot(fileName)
G = nx.convert_node_labels_to_integers(G)

# Full file path - including name ERRADO! CORRIGIR. RSTRIP NAO E SUFIXO OU PREFIXO E SIM COMB DE VAL
fileName = outputPath + outputFile.split(".")[0] + ".txt"

V = G.number_of_nodes()
E = G.number_of_edges()

# Output .dot in .txt as an edge list, with number of vertices and edges on the first line
nx.write_edgelist(G, fileName, data=False)
with open(fileName, 'r') as original: data = original.read()
with open(fileName, 'w') as modified: modified.write(str(V) + " " + str(E) + "\n" + data)
