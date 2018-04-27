import networkx as nx
import matplotlib.pylab as plt
import random

class CompanyNode:
    def __init__(self, money, name):
        self.money = money
        self.name = name
        self.trucks = []

    def __repr__(self):
        return f"Company {self.name} with {self.money} euros"
        
def set_company_nodes(graph):
    company_names = ["A", "B", "C", "D","E"]
    companies = random.sample(list(graph.nodes()), k=len(company_names))
    companies = [(x, CompanyNode(1000, company_names[i])) for i,x in enumerate(companies)]
    cps = dict()
    for (node, c) in companies:
        cps[node] = c
    nx.set_node_attributes(graph, cps, name="company")
    return graph

def draw_graph(graph):
    colormap = []
    for n in graph.nodes:
        colormap.append("red") if "company" in graph.node[n] else colormap.append("blue")
            
    d = dict(nx.degree(graph))
    pos = nx.spring_layout(graph) 
    plt.figure()
    nx.draw(graph, pos=pos, with_labels=graph.nodes().values(),nodelist=d.keys(), node_size=[(v+1) * 100 for v in d.values()], node_color=colormap)
    labels = nx.get_edge_attributes(graph,'weight')
    nx.draw_networkx_edge_labels(graph,pos, edge_labels=labels)
    plt.show()  

g = nx.gnp_random_graph(15, 0.20, seed=1)
for (u,v,w) in g.edges(data=True):
    w['weight'] = random.randint(1,10)
g = set_company_nodes(g)
draw_graph(g)