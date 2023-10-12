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
    "borderWidth": 5,
    "borderWidthSelected": 7,
    "size": 25,
    "font": {
      "size": 16,
      "strokeWidth": 7
    }
  },
  "edges": {
    "width": 12,
    "color": "#282a35",
    "selfReference": {
      "size": 1,
      "angle": 0.7853981633974483
    },
    "smooth": {
      "enabled": true,
      "type": "cubicBezier",
      "roundness": 0.55
    }
  },
  "layout": {
    "hierarchical": {
      "enabled": true,
      "levelSeparation": 150,
      "nodeSeparation": 180,
      "direction": "UD",
      "sortMethod": "directed",
      "shakeTowards": "leaves"
    }
  },
  "physics": {
    "hierarchicalRepulsion": {
      "centralGravity": 0.3,
      "avoidOverlap": 0.99,
      "springLength": 100,
      "nodeDistance": 180
    },
    "minVelocity": 0.75,
    "solver": "hierarchicalRepulsion"
  }
}
"""

def to_annotation(nags):
    if len(nags) == 0:
        return ''
    nag = list(nags)[0]

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

def to_color(nags):
    if len(nags) == 0:
        return ''
    nag = list(nags)[0]

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

def to_move_string(position):
    return '{}{}'.format(position.san(), to_annotation(position.nags))

def to_node_label(positions):
    label = ''
    first_pos = positions[0]

    if first_pos.turn():
        label += str(first_pos.board().fullmove_number - 1)
        label += '...'

    for position in positions:
        if not position.turn():
            label += '{}. '.format(str(position.board().fullmove_number))
        label += '{} '.format(to_move_string(position))

    return label

def to_node_title(positions):
    title = ''
    first_pos = positions[0]

    if first_pos.turn():
        title += str(first_pos.board().fullmove_number - 1)
        title += '...'

    for position in positions:
        if not position.turn():
            title += '{}. '.format(str(position.board().fullmove_number))
        title += '{} '.format(to_move_string(position))
        if position.turn():
            title += '\n'
        if position.comment:
            title +=  '\t' + position.comment + '\n\n'

    return title


def build_tree(position, parent_node_id):
    id = uuid4().int
    positions = [position]

    while len(position.variations) == 1:
        position = position.next()
        positions.append(position)

    node_label = to_node_label(positions)
    node_title = to_node_title(positions)

    graph.add_node(id, 
                   label=node_label,
                   title=node_title, 
                   value=len(positions))

    if parent_node_id:
        graph.add_edge(parent_node_id, id)

    for variation in position.variations:
        build_tree(variation, id)

if __name__ == "__main__":
    #graph = Network('300px', '30%', bgcolor='#a3c99e')
    #graph.show_buttons()

    graph = Network('1000px', '100%', bgcolor='#a3c99e', filter_menu=True)
    graph.set_options(OPTIONS)

    parser = argparse.ArgumentParser(description="Generate an HTML page with a graph of a study.")
    parser.add_argument('pgn_file',
                        type=str,
                        help="Name of a PGN file containing a chess study.")
    args = parser.parse_args()

    with open(args.pgn_file, encoding="utf-8") as file:
        game = chess.pgn.read_game(file)
        graph.add_node('Start', label='')
        build_tree(game.next(), 'Start')
        graph.show(args.pgn_file.replace('.pgn', '.html'), notebook=False)
