import networkx as nx
import matplotlib.pylab as plt
from random import randint, sample
import graph_utils
from company import *
from truck import *
from item import *
     
company_names = ["A", "B", "C", "D","E","F","G","H","I","J","K"]
def generate_companies(graph, n_companies=5):
    # create companies
    companies = sample(list(graph.nodes()), k=n_companies)
    companies = [(x, Company(x, 1000, company_names[i], graph)) for i,x in enumerate(companies)]
    print(companies)
    graph_utils.set_company_nodes(graph, companies)
    return companies

def generate_trucks(graph, companies, n_trucks=7):
    for c in companies:
        c[1].setTrucks([Truck(i, c[1], graph) for i in range(n_trucks)])

def generate_offers(clients, min_offers=0, max_offers=10, min_val=20, max_val=40):
    return [Item(randint(min_val,max_val), clients[randint(0,len(clients)-1)]) for _ in range(randint(min_offers,max_offers))]

def do_edge_explosion(t,graph):
    try:
        e = random.choice(list(graph.edges()))
    except Exception as e:
        print(f"\tall edges removed t= {t}\t")
        exit()
    graph.remove_edge(e[0],e[1])
    print(f"\tedge removed:\t {e[0]} -- {e[1]} (t={t})")

def do_game_over(companies, company, graph,t):
    print(f"GAME OVER FOR {company[1]} at t={t}")
    companies.remove(company)
    del graph.node[company[0]]['company']
    graph_utils.colormap[company[0]]= "#%06x" % 0xDDDDDD


def main():
    g = graph_utils.generate_weighted_random_graph()
    # g = graph_utils.generate_weighted_barabasi_graph()

    companies = generate_companies(g, n_companies=5)
    generate_trucks(g, companies, n_trucks=7)
    clients = [n for n in g.nodes if "company" not in g.node[n]]

    # graph_utils.draw_graph(g)

    p_remove = 0.0002 # por random

    for i in range(10000):
        if random.random() < p_remove:
            do_edge_explosion(i,g)

        for c in companies:
            if c[1].money <= 0:
                do_game_over(companies, c, g,i)
                continue

            offers = generate_offers(clients)
            c[1].money -= (c[1].money*0.05 + len(offers))
            c[1].go(g,offers)

    for c in companies:
        print(f"SURVIVOR: {c} -- t={i}")

    # graph_utils.draw_graph(g)
    # graph_utils.show_graphs()

if __name__ == '__main__':
    main()
