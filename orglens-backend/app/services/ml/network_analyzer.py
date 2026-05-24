import networkx as nx
from typing import Optional
from loguru import logger
import numpy as np


class NetworkAnalyzer:
    """
    Build and analyze communication networks.
    Creates graphs showing who talks to whom, influence flows, decision patterns.
    """

    def __init__(self):
        self.logger = logger

    def build_communication_network(
        self,
        messages: list[dict],
        employees: dict,  
    ) -> dict:
        """
        Build a directed graph of communication patterns.

        messages format: [{sender_id, recipient_ids, content, timestamp, influence_score}]
        Returns: {nodes: [...], edges: [...], metrics: {...}}
        """
        graph = nx.DiGraph()

        for emp_id, emp_obj in employees.items():
            graph.add_node(
                emp_id,
                name=emp_obj.name,
                title=emp_obj.title,
                department=emp_obj.department,
                level=emp_obj.level,
            )

        edge_weights = {}  

        for msg in messages:
            sender_id = msg.get("sender_id")
            recipient_ids = msg.get("recipient_ids", [])
            influence_score = msg.get("influence_score", 0.5)

            if not sender_id or not recipient_ids:
                continue

            for recipient_id in recipient_ids:
                key = (sender_id, recipient_id)
                if key not in edge_weights:
                    edge_weights[key] = []
                edge_weights[key].append(influence_score)

        for (sender, recipient), scores in edge_weights.items():
            weight = np.mean(scores)
            graph.add_edge(
                sender,
                recipient,
                weight=weight,
                message_count=len(scores),
                avg_influence=weight,
            )

        nodes = self._extract_nodes(graph, employees)
        edges = self._extract_edges(graph)
        clusters = self._detect_clusters(graph)
        centrality = self._calculate_centrality_metrics(graph)

        return {
            "nodes": nodes,
            "edges": edges,
            "clusters": clusters,
            "centrality_metrics": centrality,
            "graph": graph,
        }

    def identify_gatekeepers(self, graph: nx.DiGraph) -> list[dict]:
        """
        Identify gatekeepers: people who control information flow.
        Uses betweenness centrality and clustering coefficient.
        """
        gatekeepers = []

        betweenness = nx.betweenness_centrality(graph, weight="weight")

        clustering = nx.clustering(graph, weight="weight")

        in_degree = dict(graph.in_degree(weight="weight"))
        out_degree = dict(graph.out_degree(weight="weight"))

        for node_id in graph.nodes():
            betweenness_score = betweenness.get(node_id, 0) * 10
            clustering_score = clustering.get(node_id, 0)
            in_deg = in_degree.get(node_id, 0)
            out_deg = out_degree.get(node_id, 0)

            gatekeeper_score = betweenness_score * (1 - clustering_score)

            if gatekeeper_score > 1.0:  
                gatekeepers.append({
                    "node_id": node_id,
                    "gatekeeper_score": gatekeeper_score,
                    "betweenness": betweenness_score,
                    "clustering": clustering_score,
                    "in_degree": in_deg,
                    "out_degree": out_deg,
                })

        return sorted(gatekeepers, key=lambda x: x["gatekeeper_score"], reverse=True)

    def identify_isolated_experts(self, graph: nx.DiGraph) -> list[dict]:
        """
        Identify isolated experts: people with high in-degree but low clustering.
        These are people whose opinion is sought, but they don't network broadly.
        """
        isolated = []

        in_degree = dict(graph.in_degree(weight="weight"))
        clustering = nx.clustering(graph, weight="weight")
        out_degree = dict(graph.out_degree(weight="weight"))

        for node_id in graph.nodes():
            in_deg = in_degree.get(node_id, 0)
            out_deg = out_degree.get(node_id, 0)
            clustering_score = clustering.get(node_id, 0)

            if in_deg > 2.0 and out_deg < 1.0 and clustering_score < 0.3:
                isolated.append({
                    "node_id": node_id,
                    "in_degree": in_deg,
                    "out_degree": out_deg,
                    "clustering": clustering_score,
                    "isolation_score": in_deg / max(out_deg + 0.1, 1.0),
                })

        return sorted(isolated, key=lambda x: x["isolation_score"], reverse=True)

    def detect_alliances(self, graph: nx.DiGraph, threshold: float = 0.7) -> list[dict]:
        """
        Detect groups of people who communicate tightly (alliances).
        Uses community detection.
        """
        from networkx.algorithms import community

        undirected = graph.to_undirected()

        try:
            communities = list(community.greedy_modularity_communities(undirected, weight="weight"))
        except Exception:
            return []

        alliances = []
        for idx, comm in enumerate(communities):
            if len(comm) < 2:
                continue

            subgraph = graph.subgraph(comm)
            internal_edges = subgraph.number_of_edges()
            possible_edges = len(comm) * (len(comm) - 1)

            if possible_edges > 0:
                cohesion = internal_edges / possible_edges
            else:
                cohesion = 0

            alliances.append({
                "alliance_id": idx,
                "members": list(comm),
                "size": len(comm),
                "cohesion": cohesion,
            })

        return sorted(alliances, key=lambda x: x["cohesion"], reverse=True)


    def _extract_nodes(self, graph: nx.DiGraph, employees: dict) -> list[dict]:
        """Extract nodes from graph with metrics"""
        in_degree = dict(graph.in_degree(weight="weight"))
        out_degree = dict(graph.out_degree(weight="weight"))
        pagerank = nx.pagerank(graph, weight="weight", alpha=0.85)

        nodes = []
        for node_id in graph.nodes():
            emp = employees.get(node_id)
            nodes.append({
                "id": str(node_id),
                "name": graph.nodes[node_id].get("name", "Unknown"),
                "title": graph.nodes[node_id].get("title"),
                "department": graph.nodes[node_id].get("department"),
                "level": graph.nodes[node_id].get("level"),
                "in_degree": in_degree.get(node_id, 0),
                "out_degree": out_degree.get(node_id, 0),
                "pagerank": pagerank.get(node_id, 0) * 100, 
            })

        return nodes

    def _extract_edges(self, graph: nx.DiGraph) -> list[dict]:
        """Extract edges from graph"""
        edges = []
        for source, target, data in graph.edges(data=True):
            edges.append({
                "from": str(source),
                "to": str(target),
                "weight": data.get("weight", 0),
                "message_count": data.get("message_count", 0),
                "type": "communication",
            })

        return edges

    def _detect_clusters(self, graph: nx.DiGraph) -> list[dict]:
        """Detect clusters/communities"""
        from networkx.algorithms import community

        undirected = graph.to_undirected()

        try:
            communities = list(community.greedy_modularity_communities(undirected, weight="weight"))
        except Exception:
            return []

        clusters = []
        for idx, comm in enumerate(communities):
            clusters.append({
                "cluster_id": idx,
                "name": f"Cluster {idx}",
                "members": [str(m) for m in comm],
                "size": len(comm),
            })

        return clusters

    def _calculate_centrality_metrics(self, graph: nx.DiGraph) -> dict:
        """Calculate various centrality metrics"""
        return {
            "degree_centrality": dict(nx.degree_centrality(graph)),
            "betweenness_centrality": dict(nx.betweenness_centrality(graph, weight="weight")),
            "closeness_centrality": dict(nx.closeness_centrality(graph, distance="weight")),
            "pagerank": dict(nx.pagerank(graph, weight="weight")),
        }
