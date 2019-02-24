#!/usr/bin/env python
# coding: utf-8

# # Generalizations of Max-Flow
# 
# The purpose of this assignment is to learn about the min-cost flow problem, a generalization of max-flow, and to familiarize yourself with implementing and solving linear programs.

# ## Min-Cost Flow
# 
# Recall that a flow network with demands consists of a directed graph $G = (V, E)$, where each edge $(i,j) \in E$ has a positive integer capacity $c_{ij}$ and each node $i \in V$ has an integer demand $d_i$. In a *min-cost flow* problem, each edge $(i,j) \in E$ also has a cost (or weight) $w_{ij}$. (Note that this input generalizes the input to two important problems we discussed so far: in max flow, the edge weights were not important while in shortest paths, the edge capacities were not important.) 
# 
# Given a flow network with capacities and costs, the goal is to find a *feasible* flow $f: E \rightarrow R^+$ --that is, a flow satisfying edge capacity constraints and node demands-- that minimizes the total cost of the flow. Explicitly, the problem can be formulated as a linear program.

# ### Question 1
# 
# Answer Problem 1 in HW4-theoretical.

# ### Question 2
# 
# To implement your reduction from Problem 1 in HW4-theoretical, you will work with some standard benchmark instances for min-cost flow found [here](http://elib.zib.de/pub/mp-testdata/mincost/gte/index.html). The format of the data is described in the [Info](http://elib.zib.de/pub/mp-testdata/mincost/gte/info) file. You are to read in the graph from the data file in a form that can be solved using NetworkX's `min_cost_flow` function. Note that the data sometimes lists multiple edges between the same nodes, but with different costs or capacities. In forming the graph, you need to implement your reduction from the previous question and form a `DiGraph` instance, because the `min_cost_flow` function cannot handle multi-edges, even though the package offers `MultiDiGraph` objects.

# In[1]:


import networkx as nx

def create_graph(infile):
    """Creates a directed graph as specified by the input file. Edges are annotated with 'capacity'
    and 'weight' attributes, and nodes are annotated with 'demand' attributes.
    
    Args:
        infile: the input file using the format to specify a min-cost flow problem.
        
    Returns:
        A directed graph (but not a multi-graph) with edges annotated with 'capacity' and 'weight' attributes
        and nodes annotated with 'demand' attributes.
    """
    # TODO: implement function
    file = open(infile)
    G = nx.DiGraph()
    
    for row in file:
        
        row_split = row.split(" ")
        
        if row_split[0] == 'p':
            node_num = int(row_split[2])
            node_added = node_num + 1
        
        elif row_split[0] == 'n':
            
            G.add_node(row_split[1])
            G.node[row_split[1]]['demand'] = int(row_split[2][:-1])
        
        elif row_split[0] == 'a':
            
            if (row_split[1],row_split[2]) not in G.edges():
                
                G.add_edge(row_split[1],row_split[2])
                G.edge[row_split[1]][row_split[2]]['capacity'] = int(row_split[4])
                G.edge[row_split[1]][row_split[2]]['weight'] = int(row_split[5][:-1])
                
            else:
                
                G.add_node(str(node_added))
                G.node[str(node_added)]['demand'] = 0
                
                G.add_edge(row_split[1],str(node_added))
                G.edge[row_split[1]][str(node_added)]['capacity'] = int(row_split[4])
                G.edge[row_split[1]][str(node_added)]['weight'] = 0.5 * int(row_split[5][:-1])
                
                G.add_edge(str(node_added),row_split[2])
                G.edge[str(node_added)][row_split[2]]['capacity'] = int(row_split[4])
                G.edge[str(node_added)][row_split[2]]['weight'] = 0.5 * int(row_split[5][:-1])
                
                node_added += 1
    
    for s in G.nodes():
        if 'demand' not in G.node[s]:
            G.node[s]['demand'] = 0
    
    return G


# The following will check that your code outputs the expected min cost flow values on several test instances.

# In[2]:


G_40 = create_graph('gte_bad.40')
G_6830 = create_graph('gte_bad.6830')
G_176280 = create_graph('gte_bad.176280')

print "Correct value for _40 instance:", nx.min_cost_flow_cost(G_40) == 52099553858
print "Correct value for _6830 instance:", nx.min_cost_flow_cost(G_6830) == 299390431788
print "Correct value for _176280 instance:", nx.min_cost_flow_cost(G_176280) == 510585093810


# ## Linear Programming
# 
# Instead of using special-purpose min-cost flow solvers, you will now formulate the problems as linear programs and use general-purpose LP solvers to find the solutions.

# ### Question 3
# 
# Implement the following function to formulate the flow LP and return the optimal value (i.e., minimum cost over feasible flows).

# In[3]:


import pulp

def lp_flow_value(G):
    """Computes the value of the minimum cost flow by formulating and solving
    the problem as an LP.
    
    Args:
        G: a directed graph with edges annotated with 'capacity' and 'weight'
            attrbutes, and nodes annotated with 'demand' attributes.
            
    Returns:
        The value of the minimum cost flow.
    """
    # TODO: implement function
    
    # Creates the boundless Variables as Integers
    
    flow = pulp.LpVariable.dicts("Route", G.edges(), None , None , pulp.LpInteger)

    for (i,j) in G.edges():
        flow[(i,j)].bounds(0, G.edge[i][j]['capacity'])
    
    problem = pulp.LpProblem("Minimum Cost Flow",pulp.LpMinimize)
    problem += pulp.lpSum([flow[(i,j)] * G.edge[i][j]['weight'] for (i,j) in G.edges()]), "Total Flow"
    
    for node in G.nodes():
        problem += (pulp.lpSum([flow[(i,j)] for (i,j) in G.edges() if j == node])                    - pulp.lpSum([flow[(i,j)] for (i,j) in G.edges() if i == node]))                    == G.node[node]['demand'],                 "Flow Conservation in Node %s" % node

    problem.solve()
    return pulp.value(problem.objective)


# The following will check that the LP finds the same optimal values as previously.

# In[4]:


print "Correct value for _40 instance:", lp_flow_value(G_40) == 52099553858
print "Correct value for _6830 instance:", lp_flow_value(G_6830) == 299390431788
print "Correct value for _176280 instance:", lp_flow_value(G_176280) == 510585093810

