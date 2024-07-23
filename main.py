import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go

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

def create_graph(threads, race_location, race_variable):
    G = nx.DiGraph()
    root = f'Race at {race_variable} ({race_location})'
    G.add_node(root, label=root, style='filled', fillcolor='red')
    color_map = ['lightblue', 'lightgreen', 'lightgray', 'lightcoral']  # Extend as needed

    for i, (thread, calls) in enumerate(threads.items()):
        previous = root
        color = color_map[i % len(color_map)]
        for func in reversed(calls):
            node_id = f"{thread}: {func}"
            if node_id not in G:
                G.add_node(node_id, label=func, style='filled', fillcolor=color)
            G.add_edge(previous, node_id)
            previous = node_id

    return G

def draw_interactive_graph(G, pos):
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')

    node_x = []
    node_y = []
    text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(G.nodes[node]['label'])

    node_trace = go.Scatter(x=node_x, y=node_y, text=text, mode='markers+text', hoverinfo='text', marker=dict(showscale=False, colorscale='Viridis', size=10, color=[G.nodes[node]['fillcolor'] for node in G.nodes()], line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(showlegend=False, hovermode='closest', margin=dict(b=20, l=5, r=5, t=40), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    fig.show()

def main():
    tsan_output = """
    WARNING: ThreadSanitizer: data race (pid=8255)
    Read of size 4 at 0x563c4e70e154 by thread T2:
        #0 thread_function() /mnt/c/Users/sebak/Desktop/hell/untitled2/main.cpp:11 (untitled2+0x2459)
        #1 void std::__invoke_impl<void, void (*)()>(std::__invoke_other, void (*&&)()) /usr/include/c++/11/bits/invoke.h:61 (untitled2+0x4a7c)
        #2 std::__invoke_result<void (*)()>::type std::__invoke<void (*)()>(void (*&&)()) /usr/include/c++/11/bits/invoke.h:96 (untitled2+0x49d1)
        #3 void std::thread::_Invoker<std::tuple<void (*)()> >::_M_invoke<0ul>(std::_Index_tuple<0ul>) /usr/include/c++/11/bits/std_thread.h:259 (untitled2+0x4926)
        #4 std::thread::_Invoker<std::tuple<void (*)()> >::operator()() /usr/include/c++/11/bits/std_thread.h:266 (untitled2+0x48c8)
        #5 std::thread::_State_impl<std::thread::_Invoker<std::tuple<void (*)())> >::_M_run() /usr/include/c++/11/bits/std_thread.h:211 (untitled2+0x487a)
        #6 <null> <null> (libstdc++.so.6+0xdc252)

    Previous write of size 4 at 0x563c4e70e154 by thread T1:
        #0 thread_function() /mnt/c/Users/sebak/Desktop/hell/untitled2/main.cpp:11 (untitled2+0x2471)
        #1 void std::__invoke_impl<void, void (*)()>(std::__invoke_other, void (*&&)()) /usr/include/c++/11/bits/invoke.h:61 (untitled2+0x4a7c)
        #2 std::__invoke_result<void (*)()>::type std::__invoke<void (*)()>(void (*&&)()) /usr/include/c++/11/bits/invoke.h:96 (untitled2+0x49d1)
        #3 void std::thread::_Invoker<std::tuple<void (*)()> >::_M_invoke<0ul>(std::_Index_tuple<0ul>) /usr/include/c++/11/bits/std_thread.h:259 (untitled2+0x4926)
        #4 std::thread::_Invoker<std::tuple<void (*)()> >::operator()() /usr/include/c++/11/bits/std_thread.h:266 (untitled2+0x48c8)
        #5 std::thread::_State_impl<std::thread::_Invoker<std::tuple<void (*)())> >::_M_run() /usr/include/c++/11/bits/std_thread.h:211 (untitled2+0x487a)
        #6 <null> <null> (libstdc++.so.6+0xdc252)

    Location is global 'shared_variable' of size 4 at 0x563c4e70e154 (untitled2+0x000000008154)

    Thread T2 (tid=8258, running) created by main thread at:
        #0 pthread_create ../../../../src/libsanitizer/tsan/tsan_interceptors_posix.cpp:969 (libtsan.so.0+0x605b8)
        #1 std::thread::_M_start_thread(std::unique_ptr<std::thread::_State, std::default_delete<std::thread::_State>) >, void (*)()) <null> (libstdc++.so.6+0xdc328)
        #2 main /mnt/c/Users/sebak/Desktop/hell/untitled2/main.cpp:20 (untitled2+0x24e3)

    Thread T1 (tid=8257, running) created by main thread at:
        #0 pthread_create ../../../../src/libsanitizer/tsan/tsan_interceptors_posix.cpp:969 (libtsan.so.0+0x605b8)
        #1 std::thread::_M_start_thread(std::unique_ptr<std::thread::_State, std::default_delete<std::thread::_State>) >, void (*)()) <null> (libstdc++.so.6+0xdc328)
        #2 main /mnt/c/Users/sebak/Desktop/hell/untitled2/main.cpp:20 (untitled2+0x24e3)

    SUMMARY: ThreadSanitizer: data race /mnt/c/Users/sebak/Desktop/hell/untitled2/main.cpp:11 in thread_function()
    """

    threads, race_location, race_variable = parse_tsan_output(tsan_output)
    graph = create_graph(threads, race_location, race_variable)
    pos = nx.spring_layout(graph)  # Layout for networkx drawing
    draw_interactive_graph(graph, pos)  # Plotly for interactivity

if __name__ == "__main__":
    main()
