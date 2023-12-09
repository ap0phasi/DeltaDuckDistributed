import re
from collections import defaultdict

def parse_queries(query_text):
    # Updated pattern to correctly capture node information
    pattern = r"--\s*id:\s*(\d+)(?:\s*--\s*depends_on:\s*([0-9, ]+))?(?:\s*--\s*node:\s*([^\s;]+))?\s*([^;]*?);(?=\s*--\s*id|\s*$)"
    queries = re.findall(pattern, query_text, re.DOTALL)

    query_dict = {}
    for query_id, dependencies, node, query in queries:
        query_dict[int(query_id)] = {
            "query": query.strip(),
            "depends_on": [int(dep.strip()) for dep in dependencies.split(',')] if dependencies else [],
            "node": node.strip() if node else None  # Include node information
        }
    return query_dict if queries else {1: {"query": query_text.strip(), "depends_on": [], "node": None}}


def build_dependency_graph(query_dict):
    graph = defaultdict(list)
    for query_id, query_info in query_dict.items():
        for dep in query_info["depends_on"]:
            graph[dep].append(query_id)
    return graph

def create_request_packets(query_dict, graph):
    packets = []
    nodes = []  # List to store node information for each packet

    independent_queries = []
    independent_nodes = []  # Nodes for independent queries
    dependent_queries = []

    # Process each query
    for query_id, query_info in query_dict.items():
        if not query_info["depends_on"]:
            independent_queries.append(query_info["query"])
            independent_nodes.append(query_info["node"])
        else:
            dependent_queries.append((query_id, query_info))

    # Handle independent queries
    if independent_queries:
        packets.append(independent_queries)
        nodes.append(independent_nodes)

    # Function to visit nodes in the dependency graph
    visited = set()
    def visit(node):
        if node not in visited:
            visited.add(node)
            for neighbour in graph[node]:
                visit(neighbour)
            packets.append([query_dict[node]["query"]])
            nodes.append([query_dict[node]["node"]])  # Add corresponding node

    # Visit each dependent query node
    for node, _ in dependent_queries:
        visit(node)

    return packets, nodes


def parse_and_create_packets(query_text):
    query_dict = parse_queries(query_text)
    if len(query_dict) == 1 and not query_dict[1]["depends_on"]:
        return [[query_dict[1]["query"]]], [[query_dict[1]["node"]]]
    else:
        dependency_graph = build_dependency_graph(query_dict)
        packets, nodes = create_request_packets(query_dict, dependency_graph)
        return packets, nodes

if __name__ == "__main__":
    # Example query text
    query_text = """
    -- id: 1
    SELECT * FROM customers
    WHERE customer_id > 100;

    -- id: 2
    SELECT name, email FROM users
    WHERE signup_date > '2021-01-01';

    -- id: 3
    -- depends_on: 1,2
    SELECT c.name, u.email
    FROM customers c
    JOIN users u ON c.user_id = u.id
    WHERE c.status = 'active';
    """

    packets, nodes = parse_and_create_packets(query_text)
    for i, (packet, node) in enumerate(zip(packets, nodes), 1):
        print(f"Packet {i}:\n{packet}\nNode: {node}\n")
        
    query_text = """
    -- id: 1
    CREATE TABLE postgres.temp1 AS SELECT * FROM =(^)climate;

    -- id: 2
    CREATE TABLE postgres.temp2 AS SELECT * FROM =(^)climate;

    -- id: 3
    -- depends_on: 1,2
    SELECT * FROM postgres.temp1
    UNION ALL
    SELECT * FROM postgres.temp2;
    """
    packets, nodes = parse_and_create_packets(query_text)
    for i, (packet, node) in enumerate(zip(packets, nodes), 1):
        print(f"Packet {i}:\n{packet}\nNode: {node}\n")
        
    query_text = """
    -- id: 1
    -- node: e6e1903a5e9f
    CREATE TABLE eph2 AS SELECT * FROM eph1;

    -- id: 2
    CREATE TABLE postgres.para1 AS SELECT * FROM =(^)climate;

    -- id: 3
    -- depends_on: 1,2
    -- node: e6e1903a5e9f
    CREATE TABLE eph3 AS
    SELECT * FROM eph2
    UNION ALL
    SELECT * FROM postgres.para1;
    """
    
    packets, nodes = parse_and_create_packets(query_text)
    for i, (packet, node) in enumerate(zip(packets, nodes), 1):
        print(f"Packet {i}:\n{packet}\nNode: {node}\n")
    for packet, node in zip(packets, nodes):
        tasks = []
        for query, query_node in zip(packet, node):
            print(f"{query}\n Node: {query_node}\n")
            
        
        
