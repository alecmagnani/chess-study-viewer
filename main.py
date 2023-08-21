"""
Generate a directed tree graph representing a chess study
"""
import argparse
import traceback
import chess
import chess.pgn
import chess.svg
from pyvis.network import Network
from uuid import uuid4
from pprint import pprint

OPTIONS = """
const options = {
  "nodes": {
    "borderWidth": 3,
    "borderWidthSelected": 5,
    "shape": "image",
    "size": 300,
    "font": {
      "size": 60
    }
  },
  "edges": {
    "width": 200,
    "color": "#a0c1f7",
    "font": {
        "size": 70,
        "align": "middle",
        "color": "black"
    },
    "selfReferenceSize": null,
    "selfReference": {
      "angle": 0.7853981633974483
    },
    "smooth": {
      "type": "continuous",
      "roundness": 0.75
    }
  },
  "layout": {
    "hierarchical": {
      "enabled": true,
      "levelSeparation": 2000,
      "nodeSeparation": 2000,
      "direction": "LR",
      "sortMethod": "directed",
      "shakeTowards": "roots"
    }
  },
  "physics": {
    "hierarchicalRepulsion": {
      "centralGravity": 0.0,
      "avoidOverlap": 1,
      "springLength": 200
    },
    "minVelocity": 0.75,
    "solver": "hierarchicalRepulsion"
  }
}
"""

def to_annotation(nag):
    match nag:
        case chess.pgn.NAG_GOOD_MOVE:
            return '!'
        case chess.pgn.NAG_MISTAKE:
            return '?'
        case chess.pgn.NAG_BRILLIANT_MOVE:
            return '!!'
        case chess.pgn.NAG_BLUNDER:
            return '??'
        case chess.pgn.NAG_SPECULATIVE_MOVE:
            return '!?'
        case chess.pgn.NAG_DUBIOUS_MOVE:
            return '?!'
        case _:
            return '', 

def to_color(nag):
    match nag:
        case chess.pgn.NAG_GOOD_MOVE:
            return '#5b8bb0'
        case chess.pgn.NAG_MISTAKE:
            return '#D99342'
        case chess.pgn.NAG_BRILLIANT_MOVE:
            return '#1aada6'
        case chess.pgn.NAG_BLUNDER:
            return '#ca3431'
        case chess.pgn.NAG_SPECULATIVE_MOVE:
            return '#f7c046'
        case chess.pgn.NAG_DUBIOUS_MOVE:
            return '#e58f2a'
        case _:
            return None

def build_tree(position, parent_node_id = None):
    id = uuid4().int
    label = ''

    current_pos = position
    while current_pos and len(current_pos.variations) == 1:
        label = label + ' ' + current_pos.san()
        current_pos = current_pos.next()

    if current_pos:
        svg = chess.svg.board(current_pos.board())
        with open('assets/{}.svg'.format(id), 'w') as svg_file:
            svg_file.write(svg)

        graph.add_node(id, shape='image', image='assets/{}.svg'.format(id))
        if parent_node_id:
            graph.add_edge(parent_node_id, id, label=label)


        for variation in current_pos.variations:
            build_tree(variation, id)

if __name__ == "__main__":
    graph = Network('1000px', '100%')
    #graph.show_buttons()
    graph.set_options(OPTIONS)

    parser = argparse.ArgumentParser(description="Generate an HTML page with a graph of a study.")
    parser.add_argument('pgn_file',
                        type=str,
                        help="Name of a PGN file containing a chess study.")
    args = parser.parse_args()

    with open(args.pgn_file, encoding="utf-8") as file:
        game = chess.pgn.read_game(file)
        graph.add_node('root', label='Start')
        build_tree(game.next(), 'root')
        graph.show(args.pgn_file.replace('.pgn', '.html'), notebook=False)
