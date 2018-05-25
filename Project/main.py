import networkx as nx
import matplotlib.pylab as plt
from random import *
import graph_utils
from company import *
from truck import *
from client import *
     
company_names = ["A", "B", "C", "D","E","F","G","H","I","J","K"]
def generate_companies(graph, n_companies=5):
    # create companies
    companies = sample(list(graph.nodes()), k=n_companies)
    companies = [(x, Company(x, 10000, company_names[i], graph,
            uni_cost=1, truck_threshold=100, profit_margin=1.5, tax=0.05
            )) for i,x in enumerate(companies)]
    print(companies)
    graph_utils.set_company_nodes(graph, companies)
    return companies

def generate_trucks(graph, companies, n_trucks=7):
    for c in companies:
        c[1].setTrucks([Truck(i, c[1], graph) for i in range(n_trucks)])

def do_edge_explosion(t,graph):
    try:
        e = choice(list(graph.edges()))
    except Exception as e:
        print(f"\tall edges removed t= {t}\t")
        exit()
    graph.remove_edge(e[0],e[1])
    print(f"\tedge removed:\t {e[0]} -- {e[1]} (t={t})")

def do_game_over(companies, company, graph,t):
    print(f"GAME OVER FOR {company[1]} at t={t} -- offers={company[1].completedOffers}")
    companies.remove(company)
    del graph.node[company[0]]['company']
    graph_utils.colormap[company[0]]= "#%06x" % 0xDDDDDD


def main():
    g = graph_utils.generate_weighted_random_graph(n=15, p=0.2, min_weight=1, max_weight=10)
    # g = graph_utils.generate_weighted_barabasi_graph()

    companies = generate_companies(g, n_companies=5)
    generate_trucks(g, companies, n_trucks=7)
    clients = [Client(n, [c[1] for c in companies], min_offer_val=20, max_offer_val=100) for n in g.nodes if "company" not in g.node[n]]

    # graph_utils.draw_graph(g)

    p_remove = 0.0002 # por random

    for i in range(10000):
        if not len(companies):
            print("NO MORE COMPANIES")
            break

        if len(companies) == 1:
            print(f"WINNER: {c} -- t={i} -- offers={companies[0][1].completedOffers}")
            return

        if (randint(1,99)/100) < p_remove:
            do_edge_explosion(i,g)

        for cli in clients:
            cli.go(i)

        for c in companies:
            if c[1].money <= 0:
                do_game_over(companies, c, g,i)
                for cli in clients:
                    cli.setCompanies(companies)
                continue

            # c[1].money -= c[1].money*0.001 # impostos por existencia
            c[1].go(g, i)

            # if not i % 100:
            #     print(c[1])

    for c in companies:
        print(f"SURVIVOR: {c} -- t={i} -- offers={c[1].completedOffers}")

    # graph_utils.draw_graph(g)
    # graph_utils.show_graphs()

if __name__ == '__main__':
    main()
