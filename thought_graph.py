import numpy as np
import networkx as nx
import plotly.graph_objects as go
from constants import CONNECTIONS_TABLE, pick_type_icon
import streamlit as st


class ThoughtGraph(object):
    def __init__(self):
        self.thoughts = st.session_state.thoughts
        self.n = len(self.thoughts)
        self.edges = self._init_thoughts_graph()
        self.G = self._init_networkx_graph()
        self.sorted_thoughts = self._init_sort_by_influence()

    def refresh_graph(self):
        self.thoughts = st.session_state.thoughts
        self.n = len(self.thoughts)
        self.edges = self._init_thoughts_graph()
        self.G = self._init_networkx_graph()
        self.sorted_thoughts = self._init_sort_by_influence()

    def _init_thoughts_graph(self):
        thoughts = self.thoughts

        # Adjacency matrix
        edges = []

        # Create the graph
        for thought in thoughts:
            for id2 in thought[CONNECTIONS_TABLE]:
                # Edges
                edges.append((thought["id"], id2))

        return edges

    def _init_networkx_graph(self):
        G = nx.Graph()
        for thought in self.thoughts:
            G.add_node(
                thought["id"],
                type="thought",
                description=thought["summary"],
                thought_type=thought["type"],
            )
        G.add_edges_from(self.edges)
        return G

    def _init_sort_by_influence(self):
        G = self.G

        # degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        # closeness_centrality = nx.closeness_centrality(G)
        eigenvector_centrality = nx.eigenvector_centrality(G)
        # pagerank_centrality = nx.pagerank(G, alpha=0.85)
        # katz_centrality = nx.katz_centrality(G, alpha=0.1)
        # hubs, authorities = nx.hits(G)

        between_eigenvector = {
            node: betweenness_centrality[node] + eigenvector_centrality[node]
            for node in G.nodes()
        }

        # get sorted list (hi to lo) of betweenness + eigenvector
        sorted_between_eigenvector = sorted(
            between_eigenvector, key=between_eigenvector.get, reverse=True
        )
        return sorted_between_eigenvector

    def get_top_n_influential(self, n=3):
        top_n_thoughts = self.sorted_thoughts[:n]

        return [self.thoughts[i] for i in top_n_thoughts]

    def create_plot(self):
        G = self.G
        pos = nx.spring_layout(G)

        edge_x = []
        edge_y = []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        node_x = []
        node_y = []

        for node in G.nodes():
            x, y = pos[node]
            node_x += [x]
            node_y += [y]

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=[],
            mode="markers+text",
            hoverinfo="text",
            # marker=dict(
            #     showscale=True,
            #     colorscale="YlGnBu",
            #     reversescale=True,
            #     color=[],
            #     size=10,
            #     colorbar=dict(
            #         thickness=15,
            #         title="Node Connections",
            #         xanchor="left",
            #         titleside="right",
            #     ),
            # ),
        )

        node_sizes = []
        node_text = []
        node_colors = []
        node_symbols = []
        print(G.nodes())
        for node in G.nodes():
            node_sizes.append(5 * G.degree(node) + 2)
            node_text.append(f"{node} - {G.nodes[node]['description']}")
            node_colors.append("rgba(0, 0, 0, 0)")
            node_symbols.append(
                pick_type_icon(G.nodes[node]["thought_type"])
                if G.nodes[node]["type"] == "thought"
                else ""
            )

        node_trace.marker.color = node_colors
        node_trace.marker.size = node_sizes
        node_trace.text = node_symbols
        node_trace.hovertext = node_text
        node_trace.textposition = "middle center"

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title="Your Thought Graph",
                titlefont_size=16,
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False),
            ),
        )

        return fig

    # def count_paths(self, adj_list, max_path_length):
    #     pass

    # def find_max_path_pair(self, path_counts: np.ndarray):
    #     max_paths = 0
    #     max_pair = (0, 0)
    #     for i in range(path_counts.shape[0]):
    #         for j in range(path_counts.shape[1]):
    #             if path_counts[i][j] > max_paths:
    #                 max_paths = path_counts[i][j]
    #                 max_pair = (i, j)
    #     return max_pair, max_paths

    # def find_all_paths(self, adj_list, start, end):
    #     visited = [False] * len(adj_list)
    #     paths = []
    #     queue = [[start]]
    #     while queue:
    #         curr_path = queue.pop(0)
    #         node = curr_path[-1]

    #         if node == end:
    #             paths.append(curr_path)

    #         # if not visited[node]:
    #         #     visited[node] = True

    #         for neigh in adj_list[node]:
    #             if neigh == end:
    #                 paths.append(curr_path + [end])
    #             elif neigh not in curr_path:
    #                 queue.append(curr_path + [neigh])

    #     return paths
