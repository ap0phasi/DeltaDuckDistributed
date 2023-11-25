import re
from collections import defaultdict

def parse_queries(query_text):
    # Check if the query text contains any decorators
    if '-- id:' in query_text:
        # Regular expression to match the decorators and the query
        pattern = r"--\s*id:\s*(\d+)(?:\s*--\s*depends_on:\s*([0-9, ]+))?\s*(.*?);(?=\s*--\s*id|\s*$)"
        queries = re.findall(pattern, query_text, re.DOTALL)

        # Convert the query data into a structured dictionary
        query_dict = {}
        for query_id, dependencies, query in queries:
            query_dict[int(query_id)] = {
                "query": query.strip(),
                "depends_on": [int(dep.strip()) for dep in dependencies.split(',')] if dependencies else []
            }
        return query_dict
    else:
        # If no decorators are found, treat the entire text as a single query
        return {1: {"query": query_text.strip(), "depends_on": []}}

def build_dependency_graph(query_dict):
    graph = defaultdict(list)
    for query_id, query_info in query_dict.items():
        for dep in query_info["depends_on"]:
            graph[dep].append(query_id)
    return graph

def create_request_packets(query_dict, graph):
    packets = []
    independent_queries = []
    dependent_queries = []

    # Separate independent and dependent queries
    for query_id, query_info in query_dict.items():
        if not query_info["depends_on"]:
            independent_queries.append(query_info["query"])
        else:
            dependent_queries.append((query_id, query_info))

    # First packet contains all independent queries
    if independent_queries:
        packets.append(independent_queries)

    # Process dependent queries
    visited = set()
    
    def visit(node):
        if node not in visited:
            visited.add(node)
            for neighbour in graph[node]:
                visit(neighbour)
            # Add each dependent query as a separate packet
            packets.append([query_dict[node]["query"]])

    for node, _ in dependent_queries:
        visit(node)

    return packets

def parse_and_create_packets(query_text):
    query_dict = parse_queries(query_text)
    if len(query_dict) == 1 and not query_dict[1]["depends_on"]:
        return [[query_dict[1]["query"]]]  # Single query in a single packet
    else:
        dependency_graph = build_dependency_graph(query_dict)
        packets = create_request_packets(query_dict, dependency_graph)
        return packets

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

    packets = parse_and_create_packets(query_text)
    for i, packet in enumerate(packets, 1):
        print(f"Packet {i}:\n{packet}\n")
        
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
    packets = parse_and_create_packets(query_text)
    for i, packet in enumerate(packets, 1):
        print(f"Packet {i}:\n{packet}\n")

