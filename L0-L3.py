import networkx as nx
from matplotlib import pyplot as plt
import itertools
from datetime import datetime


# 各母点からの最短距離を計算
def dijkstra_dists(G, origins):
    dists = {}
    for origin in origins:
        dists[origin], _ = nx.single_source_dijkstra(G, source=origin)
    return dists


# ノードがどの母点から近いかを求める
def find_closest_origin(dists, node):
    closest_dist = float('inf')

    # 最短距離を持つ始点を保持する変数
    closest_origin = None
    # ノードに最も近い母点を見つける
    for origin in dists:
        # 'node' キーに対応する値を取得する
        dist_to_node = dists[origin][node]

        # 現時点での最短距離よりも小さい場合、更新する
        if dist_to_node < closest_dist:
            closest_dist = dist_to_node
            closest_origin = origin
    return closest_origin, closest_dist


# ノードとエッジを分類
def check_class(G, dists):
    node_class_dict = {}    # ノードがどの母点に属しているかを記録する辞書
    edge_class_dict = {}    # エッジがどの母点に属しているかを記録する辞書
    
    for u, v, data in G.edges(data=True):
        dist = data['weight']
        
        # エッジの両端のノードがどの母点から近いかを求める
        origin_u, origin_u_dist = find_closest_origin(dists, u)
        origin_v, origin_v_dist = find_closest_origin(dists, v)
        
        if origin_u == origin_v:    # エッジの両端点が同じ母点に属している場合
            node_class_dict[u] = origin_u
            node_class_dict[v] = origin_v
            edge_class_dict[(u, v)] = ((origin_u, origin_u), None)
            
        elif origin_u_dist + dist == origin_v_dist: # エッジの両端点が違う母点だが、母点origin_uにエッジが属している場合
            node_class_dict[u] = origin_u
            node_class_dict[v] = origin_v
            edge_class_dict[(u, v)] = ((origin_u, origin_u), None)
        
        elif origin_u_dist == origin_v_dist + dist: # エッジの両端点が違う母点だが、母点origin_vにエッジが属している場合
            node_class_dict[v] = origin_v
            node_class_dict[v] = origin_u
            edge_class_dict[(u, v)] = ((origin_v, origin_v), None)

        else:   # エッジの途中で境界が変わる場合
            node_class_dict[u] = origin_u
            node_class_dict[v] = origin_v
            border_dist = (origin_u_dist + dist + origin_v_dist) / 2        # 母点間の距離の半分
            edge_class_dict[(u, v)] = ((origin_u, origin_v), (border_dist - origin_u_dist, border_dist - origin_v_dist))
    return node_class_dict, edge_class_dict


# レベル1 ノード間経路に関係の無いノードを削除
def delete_branch_nodes(G, origins):
    visited_nodes = set()
    
    # 母点ノード間経路ノード以外のノードの導出
    for origin_u, origin_v in itertools.combinations(origins, 2):   # 2つの母点を選択
        paths = nx.all_simple_paths(G, source=origin_u, target=origin_v)
        for path in paths:
            visited_nodes.update(path)
    unvisited_nodes = set(G.nodes()) - visited_nodes
    
    G.remove_nodes_from(unvisited_nodes)    # 未訪問のノードを削除


# レベル2 ノードをまたがない母点ノード間最短距離経路以外のノードを削除
def delete_not_shortest_path_without_origin(G, origins):
    visited_nodes = set()
    
    for origin_u, origin_v in itertools.combinations(origins, 2):   # 2つの母点を選択
        _G = G.copy()
        origin_others = set(origins) - set([origin_u, origin_v])    # origin_u, origin_v以外の母点ノードを取得
        _G.remove_nodes_from(origin_others)     # origin_u, origin_v以外の母点ノードは通らないので削除
        _, path = nx.single_source_dijkstra(_G, source=origin_u, target=origin_v)
        visited_nodes.update(path)
    unvisited_nodes = set(G.nodes()) - visited_nodes

    G.remove_nodes_from(unvisited_nodes)    # 未訪問のノードを削除


# レベル3 母点ノード間最短距離経路以外のノードを削除
def delete_not_shortest_path(G, origins):
    visited_nodes = set()
    
    for origin_u, origin_v in itertools.combinations(origins, 2):   # 2つの母点を選択
        _, path = nx.single_source_dijkstra(G, source=origin_u, target=origin_v)
        visited_nodes.update(path)
    unvisited_nodes = set(G.nodes()) - visited_nodes

    G.remove_nodes_from(unvisited_nodes)    # 未訪問のノードを削除
    

# グラフを描画
def draw(G, pos, origin_point_dict, node_class_dict, edge_class_dict):
    node_color_dict = {node: origin_point_dict[node_class_dict[node]] for node in G.nodes()}
    
    DEFAULT_NODE_SIZE = 1600
    node_sizes = {node: DEFAULT_NODE_SIZE for node in G.nodes()}
    for origin_point in origin_point_dict.keys():
        node_sizes[origin_point] = DEFAULT_NODE_SIZE * 2.5
        
    DEFAULT_COLOR = '#20aee5'
    edge_color_dict = {}
    edge_label_dict = {}
    for (u, v) in G.edges():
        (origin_u, _), dists = edge_class_dict[(u, v)]
        if dists == None:
            edge_color_dict[(u, v)] = origin_point_dict[origin_u]
            edge_label_dict[(u, v)] = G.edges[u, v]['weight']
            # edge_color_dict[(u, v)] = DEFAULT_COLOR
        else :
            edge_color_dict[(u, v)] = DEFAULT_COLOR
            edge_label_dict[(u, v)] = f"{dists[0]}, {dists[1]}"
            # edge_label_dict[(u, v)] = G.edges[u, v]['weight']
    
    # node_color_dict = {node: DEFAULT_COLOR for node in G.nodes()}
    # node_color_dict.update(ORIGIN_COLOR_DICT)
    
    plt.figure(figsize=(6, 6))
    nx.draw_networkx_nodes(G, pos, node_size=list(node_sizes.values()), node_color=node_color_dict.values())
    nx.draw_networkx_labels(G, pos, font_color='white', font_size=24)
    nx.draw_networkx_edges(G, pos, width=3, edge_color=edge_color_dict.values())
    nx.draw_networkx_edge_labels(G, pos, font_size=24, font_color='#20aee5', edge_labels=edge_label_dict)
    plt.rcParams["savefig.dpi"] = 200
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
    plt.savefig(f"figure{datetime.now().strftime('%y%m%d%H%M%S')}.png", format="png")
    

G = nx.read_weighted_edgelist('L0-L3.edgelist', create_using=nx.Graph(), nodetype=int)

ORIGIN_COLOR_DICT = {0: '#e620ae', 4: '#4be620', 7: '#e5cc20'}
POSITION_DICT = {0:[0, 0], 1:[2, 0], 2:[5, 0], 3:[0, 3], 4:[2, 3], 5:[5, 2], 6:[0, 5], 7: [5, 5]}

dists = dijkstra_dists(G, ORIGIN_COLOR_DICT.keys())
node_class_dict, edge_class_dict = check_class(G, dists)
delete_branch_nodes(G, ORIGIN_COLOR_DICT.keys())
delete_not_shortest_path_without_origin(G, ORIGIN_COLOR_DICT.keys())
delete_not_shortest_path(G, ORIGIN_COLOR_DICT.keys())
draw(G, POSITION_DICT, ORIGIN_COLOR_DICT, node_class_dict, edge_class_dict)