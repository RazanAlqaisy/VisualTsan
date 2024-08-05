import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go
import re

def parse_tsan_output(tsan_output):
    threads = {}
    current_thread = None
    race_location = None

    lines = tsan_output.split('\n')
    for line in lines:
        if 'by thread T' in line:
            current_thread = line.split()[-1].strip(':')
            threads[current_thread] = []
        elif '#' in line and current_thread:
            func = ' '.join(line.split()[2:-2])
            threads[current_thread].append(func)
        elif 'Location is global' in line:
            race_variable = line.split('\'')[1]
            race_location = line.split('at')[1].split('(')[0].strip()

    return threads, race_location, race_variable

def shorten_function_name(full_name):
    # Remove specific patterns from function names
    short_name = re.sub(r'std::thread::.*?::', '', full_name)
    short_name = re.sub(r'std::__invoke.*?::', '', short_name)
    short_name = re.sub(r'void ', '', short_name)
    short_name = re.sub(r'\(\)\s*', '', short_name)
    short_name = re.sub(r'\s*\(.*\)', '', short_name)  # Remove parameter lists
    return short_name.strip()

def create_graph(threads, race_location, race_variable):
    G = nx.DiGraph()
    root = f'Race at {race_variable} ({race_location})'
    G.add_node(root, label='Race Condition', full_label=root, style='filled', fillcolor='red')  # Root node

    for i, (thread, calls) in enumerate(threads.items()):
        previous = root
        color = ['lightblue', 'lightgreen', 'lightgray', 'lightcoral'][i % 4]
        for func in reversed(calls):
            shortened_func = shorten_function_name(func)
            node_id = f"{thread}: {shortened_func}"
            if node_id not in G:
                G.add_node(node_id, label=shortened_func, full_label=func, style='filled', fillcolor=color)
            G.add_edge(previous, node_id)
            previous = node_id

    return G

def draw_interactive_graph(G, pos):
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')

    # Add arrow heads by creating a separate trace
    arrows_x, arrows_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        arrows_x.extend([x1])
        arrows_y.extend([y1])

    arrows_trace = go.Scatter(
        x=arrows_x, y=arrows_y, mode='markers',
        marker=dict(color='#888', size=10, symbol='arrow-bar-up'),
        hoverinfo='none'
    )

    node_x, node_y, text, hover_text = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(G.nodes[node]['label'])
        hover_text.append(G.nodes[node]['full_label'])

    node_trace = go.Scatter(
        x=node_x, y=node_y, text=text, mode='markers+text',
        hoverinfo='text', hovertext=hover_text,
        marker=dict(showscale=False, colorscale='Viridis', size=10,
                    color=[G.nodes[node]['fillcolor'] for node in G.nodes()], line_width=2)
    )

    fig = go.Figure(data=[edge_trace, arrows_trace, node_trace], layout=go.Layout(
        showlegend=False, hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )

    fig.show()

def main():
    #Make sure to place your TSan output in a file named tsan_output.txt in the same directory as this script.
    with open('tsan_output.txt', 'r') as file:
        tsan_output = file.read()

    threads, race_location, race_variable = parse_tsan_output(tsan_output)
    graph = create_graph(threads, race_location, race_variable)
    pos = nx.spring_layout(graph)  # Layout for networkx drawing
    draw_interactive_graph(graph, pos)  # Plotly for interactivity

if __name__ == "__main__":
    main()
