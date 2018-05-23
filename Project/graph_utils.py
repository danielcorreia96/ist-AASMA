import networkx as nx 
from random import randint
import matplotlib.pylab as plt

colormap = []
colors = ['#8B0000','#8FBC8F','#00BFFF','#B22222','#FF69B4','#90EE90','#87CEFA', '#00FF00','#000080','#FF6347','#9ACD32']

def randColor(colormap):
    color = colors[randint(0,len(colors)-1)]
    while color in colormap:
        color = colors[randint(0,len(colors)-1)]
    return color

def draw_graph(graph):
    d = dict(nx.degree(graph))
    pos = nx.spring_layout(graph)
    plt.figure()
    nx.draw(graph, pos=pos, with_labels=graph.nodes().values(),nodelist=d.keys(), node_size=[(v+1) * 100 for v in d.values()], node_color=colormap)
    labels = nx.get_edge_attributes(graph,'weight')
    nx.draw_networkx_edge_labels(graph,pos, edge_labels=labels)

def show_graphs():
    plt.show()

def generate_weighted_random_graph(n=15, p=0.2, min_weight=1, max_weight=10):
    g = nx.gnp_random_graph(n, p, seed=randint(1,100))
    for (u,v,w) in g.edges(data=True):
        w['weight'] = randint(min_weight, max_weight)
    return g

def generate_weighted_barabasi_graph(n=20, m=3, min_weight=1, max_weight=10):
    g = nx.barabasi_albert_graph(n, m, seed=randint(1,100))
    for (u,v,w) in g.edges(data=True):
        w['weight'] = randint(min_weight, max_weight)
    return g

def set_company_nodes(graph, companies):
    # set companies to specific nodes
    cps = dict()
    for (node, c) in companies:
        cps[node] = c
    nx.set_node_attributes(graph, cps, name="company")

    # color companies in graph
    for n in graph.nodes:
        colormap.append(randColor(colormap)) if "company" in graph.node[n] else colormap.append("#%06x" % 0xDDDDDD)

