import sys
import networkx as nx
from networkx.drawing.nx_pydot import write_dot


K,N = map(int, sys.argv[1:3])
name = "K" + str(K) + "N" + str(N)

G = nx.DiGraph()
v = N

# These will become MUL
temp_subi = [] 

# Building leafs and SUBi
for i in range(N):
    for j in range(K):
        G.add_edge(i, v)
        G.nodes[v]["label"] = "MULT" + str(v)
        temp_subi.append(v)
        v = v+1

# Starting node
v = K*N + N

# Stride to get kth variable from each cluster
stride = lambda n,k: n*K + N + k
###############
# N Reduction #
###############

slt_tree = [] # for later use
for k in range(K):
    
    add_tree = []
    propagate = not(N%2==0)
    end = N-1 if propagate else N
    
    # First add layer
    for i in range(0,end,2):
        
        a = stride(i,k)
        b = stride(i+1,k)
        
        G.add_edges_from( [(a,v), (b,v)] )
        G.nodes[v]["label"] = "ADD" + str(v)
        add_tree.append(v)

        v = v+1

    if propagate:
        a = stride(end,k)
        
        G.add_edge(a, v)
        G.nodes[v]["label"] = "REG" + str(v)
        add_tree.append(v)
        
        v = v+1

    # ADD tree
    nodes = len(add_tree)
    while nodes > 1:
        
        temp = []
        propagate = not(nodes%2==0)
        end = nodes-1 if propagate else nodes

        for add in range(0, end, 2):

            a = add_tree[add]
            b = add_tree[add+1]

            G.add_edges_from( [(a,v), (b,v)] )
            G.nodes[v]["label"] = "ADD" + str(v)
            temp.append(v)
            
            v = v+1

        if propagate:
            a = add_tree[-1] # getting odd node 
            
            G.add_edge(a, v)
            G.nodes[v]["label"] = "REG" + str(v)
            temp.append(v)
            
            v = v+1

        add_tree = temp
        nodes = len(temp) # implicit // 2 + int(propagate)
        
        # Keeping track of nodes indexes in the last layer
        if nodes == 1:
            slt_tree.append(add_tree[0])

###############
# K Reduction #
###############

isREG = {}
mux_tree = []

# Building first SLT layer
size = len(slt_tree)
end = size if size%2==0 else size-1
slt_temp = []
has_mux = {}
for slt in range(0,end, 2):

    a = slt_tree[slt]
    b = slt_tree[slt+1]
    
    # Converging
    G.add_edges_from( [(a,v), (b,v)] )
    slt_temp.append(v)
    G.nodes[v]["label"] = "SLT" + str(v)
    
    # Connecting SLT to respective MUX
    v = v+1
    G.add_edge(v-1,v)
    G.nodes[v]["label"] = "MUX" + str(v)
    mux_tree.append(v)
    
    v = v+1
    

# Propagate Odd Add as REG
if size%2!=0:
    G.add_edge(slt_tree[-1], v)
    slt_temp.append(v)
    G.nodes[v]["label"] = "REG" + str(v)
    isREG[v] = True

    v = v+1

slt_tree = slt_temp
nodes = len(slt_tree)
while nodes > 1:

    end = nodes if nodes%2==0 else nodes-1

    slt_temp = []
    slt_buffer = []
    mux_buffer = [] # We can't update the MUX right away in ODD cases
    for n in range(0,end, 2):
        
        a = slt_tree[n]
        b = slt_tree[n+1]

        G.add_edges_from([(a,v), (b,v)])
        G.nodes[v]["label"] = "SLT" + str(v)
        slt_temp.append(v)
        v = v+1

    if nodes%2!=0:
            
        G.add_edge(slt_tree[-1], v)
        G.nodes[v]["label"] = "REG" + str(v)
        slt_buffer.append(v)
        isREG[v] = True
        v = v+1

        # If there are odd nodes and K isn't odd, you still need the MUX
        if K%2==0:
            G.add_edge(mux_tree[-1],v)
            G.nodes[v]["label"] = "REG" + str(v)
            mux_tree.pop()
            mux_buffer.append(v)
            v = v+1

    slt_tree = slt_temp + slt_buffer

    # MUX convergence
    mux_end = len(mux_tree)
    if mux_end >= 2:
        
        mux_end = mux_end if mux_end%2==0 else mux_end-1
        mux_temp = []
        i = 0
        
        for m in range(0,mux_end, 2):
            G.add_edge(mux_tree[m],v)
            G.add_edge(mux_tree[m+1],v)

            
            # If is in bounds converge!
            if not(slt_tree[i] in isREG):
                G.add_edge(slt_tree[i], v)
                i = i+1

            G.nodes[v]["label"] = "MUX" + str(v)
            mux_temp.append(v)
            v = v+1
        
        if len(mux_tree)%2!=0:
           G.add_edge(mux_tree[-1], v)
           G.add_edge(slt_tree[i], v)

           # Quickfix, need to figure out why later..
           if K==7:
               G.nodes[v]["label"] = "MUX"+str(v)
           else:
               G.nodes[v]["label"] = "MUX"+str(v)

           mux_temp.append(v)
           v = v+1
        mux_tree = mux_buffer + mux_temp


    
    nodes = len(slt_tree)

# Output
for mux in mux_tree:
    G.add_edge(mux, v)
if K==5:
    G.add_edge(slt_tree[-1], v)
    G.nodes[v]["label"] = "MUX"
    G.add_edge(v, v+1)
    v = v+1
G.nodes[v]["label"] = "K"
v = v+1

# Connecting SUBi to MUL
new_subi = []
idx = 0
for i in range(N):
    for j in range(K):
        G.remove_edge(i,temp_subi[idx]) # Remove AB
        G.add_edge(i,v) # Create AC
        new_subi.append(v)
        G.nodes[v]["label"] = "SUB"
        G.add_edge(v, temp_subi[idx]) # Create CB

        v = v+1
        idx = idx+1

# Node expansion
idx = 0
for i in range(N):
    
    end = K if K%2==0 else K-1

    for j in range(0,end,2):
        
        a = new_subi[idx]
        b = new_subi[idx+1]

        # Removing direct connection from variable to subi in pairs
        G.remove_edges_from( [(i,a), (i,b)] )

        # Expanding variable
        G.add_edge(i,v)
        G.nodes[v]["label"] = "REG"

        # Connect expansion to previous subi pair
        G.add_edges_from( [(v,a), (v,b)] )

        v = v+1
        idx = idx+2

    if K%2!=0:
        
        propagate = new_subi[idx]
        G.remove_edge(i, propagate)

        G.add_edge(i,v)
        G.nodes[v]["label"] = "REG"

        G.add_edge(v, propagate)

        v = v+1
        idx = idx+1



write_dot(G, name + ".dot")

# Writing output for Annealing
V = G.number_of_nodes()
E = G.number_of_edges()
nx.write_edgelist(G, name + ".in", data=False)
with open(name + ".in", 'r') as original: data = original.read()
with open(name + ".in", 'w') as modified: modified.write(str(V) + " " + str(E) + "\n\n" + data)
