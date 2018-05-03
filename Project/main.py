import networkx as nx
import matplotlib.pylab as plt
from random import randint, sample
from company import *
from truck import *
from item import *
     


def set_company_nodes(graph):
    company_names = ["A", "B", "C", "D","E"]
    companies = sample(list(graph.nodes()), k=len(company_names))
    companies = [(x, Company(x, 1000, company_names[i], g)) for i,x in enumerate(companies)]
    cps = dict()
    for (node, c) in companies:
        cps[node] = c
    nx.set_node_attributes(graph, cps, name="company")
    return graph


def randColor():
    return "#%06x" % randint(0x111111,0xCCCCCC)

def draw_graph(graph):
    colormap = []
    for n in graph.nodes:
        colormap.append(randColor()) if "company" in graph.node[n] else colormap.append("#%06x" % 0xDDDDDD)
            
    d = dict(nx.degree(graph))
    pos = nx.spring_layout(graph) 
    plt.figure()
    nx.draw(graph, pos=pos, with_labels=graph.nodes().values(),nodelist=d.keys(), node_size=[(v+1) * 100 for v in d.values()], node_color=colormap)
    labels = nx.get_edge_attributes(graph,'weight')
    nx.draw_networkx_edge_labels(graph,pos, edge_labels=labels)
    plt.show()  

def randomOffers():
    return [Item(randint(20,50), clients[randint(0,len(clients)-1)]) for _ in range(randint(0,10))]

g = nx.gnp_random_graph(15, 0.20, seed=1)
for (u,v,w) in g.edges(data=True):
    w['weight'] = randint(1,10)
g = set_company_nodes(g)


draw_graph(g)

companies = [g.nodes[n]["company"] for n in g.nodes if "company" in g.node[n]]
clients = [n for n in g.nodes if "company" not in g.node[n]]

for c in companies:
    c.setTrucks([Truck(i, c, g) for i in range(7)])

for _ in range(10):
    # explosoes random
    
    for c in companies:
        c.go(g,randomOffers())
