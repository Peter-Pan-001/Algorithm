#!/usr/bin/env python
# coding: utf-8

# # Max Flow Applications
# 
# The purpose of this assignment is to investigate applications of finding a Max Flow. The problem asks you to design and implement an algorithm for shipping a material between nodes with different supply and demand requirements.
# 
# * Please write code *only* in the bodies of the two functions, that is, following the TODO comments.
# * Be careful not to use varibles defined outside of the functions.
# * Breaking the two above rules may lead to 0 grades.

# ## Movie distribution
# 
# First solve Problem 2 from hw3-t. 
# 
# Now suppose a movie distributor would like to ship a copy of a film from CA to every other state. There are therefore 48 units to ship out of CA, and each other state receives 1 unit. 
# 
# The dataset contiguous-usa.dat lists the adjacent states in the US. Each line lists two adjacent states; thus AK and HI are omitted, but DC is included in the data. The following code reads in the graph of US states.

# In[1]:


import networkx as nx
G = nx.Graph()

usa = open('contiguous-usa.dat')
for line in usa:
    s1, s2 = line.strip().split()
    G.add_edge(s1, s2)


# We now encode the demands into the graph.

# In[2]:


for state in G.nodes():
    if state != 'CA':
        G.node[state]['demand'] = 1
G.node['CA']['demand'] = -48


# We will assign a uniform capacity of 16 to each edge. Since CA has only three adjacent states, this is the smallest possible uniform capacity that allows one to ship all 48 units out of CA. As we have created an undirected graph, and flows have directions, we first convert the graph to a directed graph.

# In[3]:


G = nx.DiGraph(G)
uniform_capacity = 16
for (s1, s2) in G.edges():
    G.edge[s1][s2]['capacity'] = uniform_capacity


# Complete the following function to implement your algorithm to find a flow with demands. Your function should work correctly for any input, not just the movie instance considered here. As always, you are encouraged to define auxiliary functions as needed for clarity.

# In[4]:


def flow_with_demands(graph):
    """Computes a flow with demands over the given graph.
    
    Args:
        graph: A directed graph with nodes annotated with 'demand' properties and edges annotated with 'capacity' 
            properties.
        
    Returns:
        A dict of dicts containing the flow on each edge. For instance, flow[s1][s2] should provide the flow along
        edge (s1, s2).
        
    Raises:
        NetworkXUnfeasible: An error is thrown if there is no flow satisfying the demands.
    """
    # TODO: Implement the function.
    
    def reduction_to_max_flow(graph):
        graph.add_node('s')
        graph.add_node('t')
        graph.node['s']['demand'] = 0
        graph.node['t']['demand'] = 0
        for state in graph.nodes():
            if state != 's' and state != 't':
                if graph.node[state]['demand'] < 0:
                    graph.add_edge('s', state)
                    graph.edge['s'][state]['capacity'] = -graph.node[state]['demand']
                    graph.node['s']['demand'] += graph.node[state]['demand']
                elif graph.node[state]['demand'] > 0:
                    graph.add_edge(state, 't')
                    graph.edge[state]['t']['capacity'] = graph.node[state]['demand']
                    graph.node['t']['demand'] += graph.node[state]['demand']
        return graph
    
    graph = reduction_to_max_flow(graph)
    R = nx.algorithms.flow.ford_fulkerson(graph, 's', 't')
    flow_dict = R.graph['flow_dict']
    flow_value = R.graph['flow_value']
                
    if flow_value != graph.node['t']['demand']:
        raise nx.NetworkXUnfeasible("No flow satisfying the demand")
    
    for s1 in flow_dict.keys():
        for s2 in flow_dict[s1].keys():
            if s2 == 't':
                flow_dict[s1].pop('t', None)
                break
    
    for s1 in flow_dict.keys():
        if s1 == 's':
            flow_dict.pop('s', None)
        elif s1=='t':
            flow_dict.pop('t', None)
    
    graph.remove_node('s')
    graph.remove_node('t')
    
    
    return flow_dict
    


# To verify that your solution is correct, implement a function that computes the total flow into each node (which will be negative for supply nodes).

# In[5]:


def divergence(flow):
    """Computes the total flow into each node according to the given flow dict.
    
    Args:
        flow: the flow dict recording flow between nodes.
        
    Returns:
        A dict of the net flow into each node.
    """
    # TODO: Implement the function.
    
    net_flow = {}
    for s1 in flow:
        for s2 in flow[s1]:
            if s1 not in net_flow:
                net_flow[s1] = 0
            if s2 not in net_flow:
                net_flow[s2] = 0
            net_flow[s1] -= flow[s1][s2]
            net_flow[s2] += flow[s1][s2]
            
    return net_flow


# The following code performs a sanity check on your function (but does not completely confirm correctness).

# In[6]:


flow = flow_with_demands(G)
div = divergence(flow)
print "Flow satisfies all demands:", all(div[n] == G.node[n]['demand'] for n in G.nodes())

