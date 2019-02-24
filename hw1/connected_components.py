#!/usr/bin/env python
# coding: utf-8

# # Connected Components
# 
# The purpose of this assignment is to familiarize yourself with the handling of graph data structures. You will implement depth-first search for identifying the connected components of an undirected graph, implementing procedure Search as a subroutine along the way.
# 
# You will use the [NetworkX](https://networkx.github.io/) Python package to represent and manipulate graphs. You should first familiarize yourself with its functionality by going through the brief [tutorial](http://networkx.github.io/documentation/networkx-1.9.1/tutorial/index.html). For this homework, you may only use the basic undirected graph methods listed [here](http://networkx.github.io/documentation/networkx-1.9.1/reference/classes.graph.html).
# 
# As a use case, we will work with a dataset recording the interactions between characters in Homer's *Iliad*.

# In[16]:


import networkx
import urllib2
homer = urllib2.urlopen('http://mirror.hmc.edu/ctan/support/graphbase/homer.dat')


# The format of the data is straightforward. After some comment lines (beginning with \*), the file lists a codename for each character (i.e., node of the graph), followed by a description. The file then lists the groups of characters that interact in each chapter, from which you will form the edges. For instance, the first line has the form:
# 
# ```1:CH,AG,ME,GS;AP,CH;HE,AC;AC,AG,CA;HE,AT;AT,AC;AT,OG;NE,AG,AC;CS,OD```
# 
# This means that CH,AG,ME,GS interacted, so there are edges for all pairs of these nodes. Groups of characters that interacted are separated by semicolons. The lines start with chapter information of the form `1:` or `&:`, which can be ignored for this problem.

# First implement a function to read in the nodes from the input file. You may implement any auxiliary functions as needed, and are encouraged to use small functions with specific purposes to keep your code readable. Any function you implement should be clearly commented.

# Next implement a function to read in the edges from the input file.

# In[17]:


def read_nodes(gfile):
    """Reads in the nodes of the graph from the input file.
    
    Args:
        gfile: A handle for the file containing the graph data, starting at the top.
        
    Returns:
        A generator of the nodes in the graph, yielding a list of the form:
            ['CH', 'AG, 'ME', ...]
    """
    
    vertices = []
    for row in gfile:
        if row[0] == '\n':
            break
        if row[0] == '*':
            continue
        else:
            vertices.append(row[0:2])
            #print(vertices)
            continue
    return vertices


# In[18]:


def read_edges(gfile):
    """Reads in the edges of the graph from the input file.
    
    Args:
        gfile: A handle for the file containing the graph data, starting at the top 
            of the edges section.
            
    Returns:
        A generator of the edges in the graph, yielding a list of pairs of the form:
            [('CH', 'AG'), ('AG', 'ME'), ...]
    """
    edges = []
    for row in gfile: # start from the edge section
        #print(len(row))
        if row[0] == '*':  # If the last row, then end
            break
        if (row[1].isdigit()):
            i = 2  # for row numbers >=10
        else:
            i = 1  # for row numbers <10 and starting with &:
        while row[i] != '\n':  # If encounter \n, then next row
            #print(i)
            i += 1  # start from the first letter of first edge in each row
            connect_node = []
            while row[i] != ';':  # group by ";"
                if row[i] == '\n':  # for the last loop, without it, string index out of range
                    break
                if row[i] == ',': 
                    i += 1
                connect_node.append(row[i:i+2])
                i += 2  # to next edge in the group
            #print(connect_node)
            for j in range(0, len(connect_node)-1):
                for k in range(j+1,len(connect_node)):
                    edges.append((connect_node[j], connect_node[k]))
    return edges
    


# The following code should now correctly create the graph.

# In[19]:


import networkx as nx
G = nx.Graph()
G.add_nodes_from(read_nodes(homer))
G.add_edges_from(read_edges(homer))


# Next implement procedure Search. The function takes in a graph and a root node, and returns a list of the nodes visited during the search. The nodes should appear in the order in which they were *first visited*. The neighbors of a node should be processed in *alphabetical order*, where numbers come before letters. This will ensure that the output of your function is uniquely defined, given any input node.

# In[20]:


def Search(graph, root):
    """Runs Search from vertex root in a graph. Neighboring nodes are processed in alphabetical order.

    Args:
        graph: the given graph, with nodes encoded as strings.
        root: the node from which to start the search.

    Returns:
        A list of nodes in the order in which they were first visited.
    """
    visited = {}
    visit_list = []
    for vertex in graph.nodes():
        visited[vertex] = 0
    def Searchchild(graph, root):
        visit_list.append(root)
        visited[root] = 1
        for edge in sorted(graph.edges(nbunch = [root, ])):
            if visited[edge[1]] == 0:
                Searchchild(graph, edge[1])
    Searchchild(graph, root)
    return visit_list


# We will check the correctness of your code by verifying that it correctly computes the DFS tree starting at Ulysses (node `OD`).

# In[21]:


ulysses = Search(G, 'OD')
print(ulysses)


# Next implement DFS to find the connected components of the character graph. When choosing roots for your components, always pick the *smallest unvisited node* according to alphabetical ordering. Combined with your Search routine, this will ensure that the output is again uniquely defined.

# In[22]:


def connected_components(graph):
    """Computes the connected components of the given graph.
    
    Args: 
        graph: the given graph, with nodes encoded as strings.
        
    Returns:
        The connected components of the graph. Components are listed in
        alphabetical order of their root nodes.
    """
    visited = {}
    component_list = []
    root = ''
    for vertex in graph.nodes():
        visited[vertex] = 0
    while(len([vertex for vertex in graph.nodes() if visited[vertex] == 0]) != 0):
        component = []
        for vertex in sorted(graph.nodes()):
            if visited[vertex] == 0:
                root = vertex
                break
        component = Search(graph,root)
        for vertex in component:
            visited[vertex] = 1
        component_list.append(component)
    return component_list


# We will check correctness of your code by verifying that your output list is identical to our solution.

# In[23]:


character_interactions = connected_components(G)
print(character_interactions)


# As a preliminary check, you should find that the following statements are all true.

# In[24]:


component_sizes = [len(c) for c in character_interactions]
print "There are 12 connected components in the Iliad:", len(component_sizes) == 12
print "The giant component has size 542:", max(component_sizes) == 542
print "There are 5 isolated characters:", len([c for c in component_sizes if c == 1]) == 5

