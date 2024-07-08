import networkx as nx
from matplotlib import pyplot as plt
from datetime import datetime
import itertools

G = nx.read_weighted_edgelist('L4.edgelist', create_using=nx.Graph(), nodetype=int)

colors = ['#e620ae'] * 3 + ['#20aee5'] * 3 + ['#4be620'] * 3
pos = {0:[0, 2], 1:[0, 1], 2:[0, 0], 3:[1, 2], 4:[1, 1], 5:[1, 0], 6:[2, 2], 7:[2, 1], 8:[2, 0]}
node_sizes = {node: 4000 for node in G.nodes()}
node_sizes[3] = 1600
node_sizes[4] = 1600
node_sizes[5] = 1600
ORIGIN_GROUP = [[0, 1, 2], [6, 7, 8]]
visited_nodes = set()
for origin_group_u, origin_group_v in itertools.combinations(ORIGIN_GROUP, 2):
    for origin_u, origin_v in itertools.product(origin_group_u, origin_group_v):
        _, path = nx.single_source_dijkstra(G, source=origin_u, target=origin_v)
        visited_nodes.update(path)
unvisited_nodes = set(G.nodes()) - visited_nodes
G.remove_nodes_from(unvisited_nodes)
colors = ['#e620ae'] * 3 + ['#20aee5'] * 1 + ['#4be620'] * 3
node_sizes = {node: 4000 for node in G.nodes()}
node_sizes[3] = 1600

label = {(u, v): int(data['weight']) for u, v, data in G.edges(data=True)}
plt.figure(figsize=(6, 6))
nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=list(node_sizes.values()))
nx.draw_networkx_labels(G, pos, font_color='white', font_size=24)
nx.draw_networkx_edges(G, pos, width=3, edge_color='#20aee5')
nx.draw_networkx_edge_labels(G, pos, font_size=24, font_color='#20aee5', edge_labels=label)
plt.rcParams["savefig.dpi"] = 200
plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
plt.savefig(f"figure{datetime.now().strftime('%y%m%d%H%M%S')}.png", format="png")