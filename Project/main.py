import networkx as nx
import matplotlib.pylab as plt
from random import randint, sample
from company import *
from truck import *
from item import *
     
colors = ['#8B0000','#8FBC8F','#00BFFF','#B22222','#FF69B4','#90EE90','#87CEFA', '#00FF00','#000080','#FF6347','#9ACD32']#,'#7FFF00','#FF7F50','#6495ED','#FFF8DC','#DC143C','#00FFFF','#00008B','#008B8B','#B8860B','#A9A9A9','#006400','#BDB76B','#8B008B']

def set_company_nodes(graph):
    company_names = ["A", "B", "C", "D","E"]
    companies = sample(list(graph.nodes()), k=len(company_names))
    companies = [(x, Company(x, 1000, company_names[i], g)) for i,x in enumerate(companies)]
    print(companies)
    cps = dict()
    for (node, c) in companies:
        cps[node] = c
    nx.set_node_attributes(graph, cps, name="company")
    return graph


def randColor(colormap):
    color = colors[randint(0,len(colors)-1)]
    while color in colormap:
        color = colors[randint(0,len(colors)-1)]
    return color

def draw_graph(graph):
    colormap = []

    for n in graph.nodes:
        colormap.append(randColor(colormap)) if "company" in graph.node[n] else colormap.append("#%06x" % 0xDDDDDD)
            
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

for i in range(10000):
    # print("==============================================\n")
    # explosoes random
    
    for c in companies:
        if c.money <= 0:
            print(f"GAME OVER FOR {c} at t={i}")
            companies.remove(c)
            continue
        c.money -= 1
        c.go(g,randomOffers())


draw_graph(g)
