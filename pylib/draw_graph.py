# coding=utf-8

from IPython import display
import pydot

graphs = {
    # Intro to TF notebook
    "add-op": """
        digraph g {
            x [shape=plaintext,label=""]
            y [shape=plaintext,label=""]
            z [shape=plaintext,label=""]
            x -> tf.add -> z;
            y -> tf.add;
            rankdir=LR
        }""",
    "const-op": """
        digraph g {
            z [shape=plaintext,label=""]
            tf.constant -> z;
            rankdir=LR
        }""",
    "simple-graph": """
        digraph g {
            x -> add;
            y -> add;
            sum_ [shape=plaintext,label=""];
            add -> sum_ [label="sum_"];
            rankdir=LR
        }""",
    "simple-graph-run": """
        digraph g {
            x -> add [label="2"];
            y -> add [label="3"];
            5 [shape=plaintext];
            add -> 5 ;
            rankdir=LR
        }""",
    "exercise": """
        digraph g {
            x -> add;
            y -> add;
            add -> multiply;
            y -> multiply;
            out [shape=plaintext,label=""];
            multiply -> out;
            rankdir=LR
        }""",
    # RNN notebook
    "feed-forward": """
        digraph g {
            node [style=filled, label="", shape=circle]
            a [fillcolor=gray, shape=square];
            b [fillcolor="#91bfdb"];
            b1 [fillcolor="#91bfdb"];
            c [fillcolor="#fc8d59"];
            a -> b -> b1 -> c;
            rankdir=LR
        }""",
    "recurrent": """
        digraph g {
            node [style=filled, label="", shape=circle]
            a [fillcolor=gray, shape=square];
            b [fillcolor="#91bfdb"];
            c [fillcolor="#fc8d59"];
            a -> b -> c;
            b -> b [dir=back];
            rankdir=LR
        }""",
    "unrolled": """
        digraph g {
            node [fillcolor=gray, style=filled, label="", shape=square]
            a1; a2; a3; a4;
            node [fillcolor="#91bfdb", shape=circle]
            { rank = same; b1; b2; b3; b4; }
            node [fillcolor="#fc8d59"]
            c1; c2; c3; c4;

            a1 -> b1 -> c1;
            a2 -> b2 -> c2;
            a3 -> b3 -> c3;
            a4 -> b4 -> c4;
            b1 -> b2;
            b2 -> b3
            b3 -> b4;
            rankdir=LR
        }""",
    "classification": """
        digraph g {
            node [fillcolor=gray, style=filled, label="", shape=square]
            a1; a2; a3; a4;
            node [fillcolor="#91bfdb", shape=circle]
            { rank = same; b1; b2; b3; b4; }
            node [fillcolor="#fc8d59"]
            c4;

            a1 -> b1;
            a2 -> b2;
            a3 -> b3;
            a4 -> b4 -> c4;
            b1 -> b2;
            b2 -> b3
            b3 -> b4;
            rankdir=LR
        }""",
    "generation": """
        digraph g {
            node [fillcolor=gray, style=filled, label="", shape=square]
            a1;
            node [fillcolor="#91bfdb", shape=circle]
            { rank = same; b1; b2; b3; b4; }
            node [fillcolor="#fc8d59"]
            c1; c2; c3; c4;

            a1 -> b1 -> c1;
            c1 -> b2 [style=dashed, headport=w];
            b2 -> c2;
            c2 -> b3 [style=dashed, headport=w];
            b3 -> c3;
            c3 -> b4 [style=dashed, headport=w];
            b4 -> c4;
            b1 -> b2;
            b2 -> b3
            b3 -> b4;
            rankdir=LR
        }""",
    "translation": """
        digraph g {
            node [fillcolor=gray, style=filled, label="", shape=square]
            a1; a2; a3[label="end", fillcolor=white];
            node [fillcolor="#91bfdb", shape=circle]
            { rank = same; b1; b2; b3; b4; }
            node [fillcolor="#fc8d59"]
            c3; c4;

            a1 -> b1;
            a2 -> b2;
            a3 -> b3 -> c3;
            c3 -> b4 [style=dashed, headport=w];
            b4 -> c4;
            b1 -> b2;
            b2 -> b3
            b3 -> b4;
            rankdir=LR
        }""",
    "LSTM": """
        digraph g {
            node [style=filled, shape=circle, label="", fillcolor="#91bfdb"]

            {
                node [shape=plaintext,label="",fillcolor=none]
                a1; c1;
            }

            subgraph cluster0 {
                //node [style=filled,color=white];
                color="#dddddd";
                style=filled;
                label="LSTM Cell"

                input [shape=point];

                {
                    node [label="∫", fillcolor=white]
                    input_nonlin;
                    output_nonlin;
                }

                input -> input_nonlin -> input_gate;
                input -> input_gate;

                input_gate -> state -> output_nonlin -> output_gate;
                state -> state [dir=back, label="state", headport=e, tailport=w];
                input-> output_gate;
            }

            edge [color="black:invis:black:invis:black", arrowsize=2]
            a1 -> input;
            output_gate -> c1;

            rankdir=LR
        }""",
}

def draw_graph(name):
    graph = graphs.get(name, name)
    return display.Image(pydot.graph_from_dot_data(graph).create_png())
    