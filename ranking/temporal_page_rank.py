import networkx as nx
from progress.bar import Bar

def calculate_tpr(own_public_key, blocks):
    """
    Creates a graph of the interactions and calculates pagerank.
    :return: PageRank from one node
    """

    nodes = set()
    G = nx.DiGraph()

    for block in Bar('Creating graph').iter(blocks):
        pubkey_requester = block.public_key
        pubkey_responder = block.link_public_key

        sequence_number_requester = block.sequence_number
        sequence_number_responder = block.link_sequence_number

        G.add_edge((pubkey_requester, sequence_number_requester), (pubkey_requester, sequence_number_requester + 1),
                   contribution=block.contribution)
        G.add_edge((pubkey_requester, sequence_number_requester), (pubkey_responder, sequence_number_responder + 1),
                   contribution=block.contribution - block.net_contribution)

        G.add_edge((pubkey_responder, sequence_number_responder), (pubkey_responder, sequence_number_responder + 1),
                   contribution=block.contribution - block.net_contribution)
        G.add_edge((pubkey_responder, sequence_number_responder), (pubkey_requester, sequence_number_requester + 1),
                   contribution=block.contribution)

        nodes.add(pubkey_requester)
        nodes.add(pubkey_responder)

    personal_nodes = [node1 for node1 in G.nodes() if node1[0] == own_public_key]
    number_of_nodes = len(personal_nodes)
    if number_of_nodes == 0:
        return {}
    personalisation = {node_name: 1.0 / number_of_nodes if node_name in personal_nodes else 0
                       for node_name in G.nodes()}

    try:
        result = nx.pagerank_scipy(G, personalization=personalisation, weight='contribution')
    except nx.NetworkXException:
        self._logger.info("Empty Temporal PageRank, returning empty scores")
        return {}

    sums = {}

    for interaction in result.keys():
        sums[interaction[0]] = sums.get(interaction[0], 0) + result[interaction]

    return sums

