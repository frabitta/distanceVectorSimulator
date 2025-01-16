class Network:
    """
    Network of nodes
    """
    def __init__(self):
        """Creates a new network
        """
        self.nodes: dict[str, Node] = {}                # addr: Node
        self.edges: dict[tuple[str, str], int] = {}     # (node1, node2): weight

    def add_node(self, addr: str):
        """Add a new node to the network

        Args:
            addr (str): addr of the node
        """
        self.nodes[addr] = Node(addr, self)
    
    def add_edge(self, node1: str, node2: str, weight: int):
        """Add an edge between two nodes

        Args:
            node1 (str): addr of the first node
            node2 (str): addr of the second node
            weight (int): weight of the edge
        """
        self.nodes[node1].neightbour(node2, weight)
        self.nodes[node2].neightbour(node1, weight)
        self.nodes[node1].sendDV()
        self.nodes[node2].sendDV()
        present, tuple = self.usedTuple(node1, node2)
        if present:
            self.edges[tuple] = weight
        else:
            self.edges[(node1, node2)] = weight
    
    def usedTuple(self, node1: str, node2: str):
        """
        Returns the tuple used to store the edge between node1 and node2, if present"""
        if (node1, node2) in self.edges:
            return True, (node1, node2)
        else:
            if (node2, node1) in self.edges:
                return True, (node2, node1)
            else:
                return False, None

    def remove_node(self, addr: str):
        """Remove a node from the network

        Args:
            addr (str): addr of the node to remove
        """
        if addr in self.nodes:
            del self.nodes[addr]
            # removes edges from/to that node if they exist
            for (node1, node2) in list(self.edges.keys()):
                if node1 == addr or node2 == addr:
                    self.remove_edge(node1, node2)
    
    def remove_edge(self, node1: str, node2: str):
        """Remove an edge between two nodes

        Args:
            node1 (str): addr of the first node
            node2 (str): addr of the second node
        """
        present, tuple = self.usedTuple(node1, node2)
        if present:
            # deletes edge and informs the two nodes that the connection doesn't exist anymore
            del self.edges[tuple]
            # we check if the nodes exist because they could have been removed by remove_node
            if node1 in self.nodes:
                self.nodes[node1].neightbour(node2,float('inf'))
            if node2 in self.nodes:
                self.nodes[node2].neightbour(node1,float('inf'))
    
    def transmit(self, src: str, dst: str, dv: dict[str, tuple[int, str]]):
        """Transmit a distance vector to a node

        Args:
            dst (str): addr of the destination node
            dv (dict[str, tuple[int, str]]): distance vector to transmit
        """
        self.nodes[dst].receiveDV(src, dv)
    
    def print_tables(self):
        """Prints the routing tables of all nodes
        """
        for addr, node in self.nodes.items():
            print("Routing table for node ", addr)
            node.print_table()
            print("\n")

class Node:
    """
    Node of the network
    """
    def __init__(self, addr: str, network: Network):
        """Creates a new node

        Args:
            addr (str): addr of the node
        """
        self.addr = addr
        self.routing_table: dict[str, tuple[int, str]] = {} # destination: (distance, next hop)
        self.net = network
        self.routing_table[self.addr] = (0, self.addr)
        # self.neightbours = []
        print("Created node ", self.addr)
    
    def neightbour(self, node: str, weight):
        """Updates a neightbour connection

        Args:
            node (str): node to discover
            weight (int): weight of the edge
        """
        if node != self.addr:
            print("Node ", self.addr, " has a new neighbour ", node, " with weight ", weight)
            # self.neightbours.append(node)
            if node not in self.routing_table:
                self.routing_table[node] = (weight, node)
            else:
                self.routing_table[node] = (weight, node)
                # if a connection is disabled we inform the other nodes and delete it  
                if weight == float('inf'):
                    # we delete all the routes that go through that node
                    for addr, (weight, next_hop) in self.routing_table.items():
                        if next_hop == node:
                            del self.routing_table[addr]
                    """
                    self.neightbours.remove(node)
                    """
            """
            I send the DV via the newtwork because we need to have the connection established
            otherwise we find synchronization issues
            """
            # self.updatedRT()
    
    def receiveDV(self, hop, dv: dict[str, tuple[int, str]]):
        """Receives the distance vector from the neighbours
        """
        updated = False
        # print("Node ", self.addr, " received a DV:\n", dv)
        # reads the DV received and updates its routing table
        if hop in self.routing_table:
            for addr, (weight, next_hop) in dv.items():
                # if the node is reachable
                """ """
                if addr != self.addr:
                    new_distance = weight + self.routing_table[hop][0]
                    # if is unknow we add it
                    if addr not in self.routing_table:
                        self.routing_table[addr] = (new_distance, hop)
                        updated = True
                    # if is known we update it
                    else:
                        if new_distance < self.routing_table[addr][0]:
                            self.routing_table[addr] = (new_distance, hop)
                            updated = True

            if updated:
                self.updatedRT()
    
    def updatedRT(self):
        # prints to screen
        print(f"Node {self.addr} updated its routing table")
        self.print_table()
        # communicates new DV to neighbours
        self.sendDV()
    
    def print_table(self):
        print("addr -> weight via next_hop")
        for addr, (weight, next_hop) in self.routing_table.items():
            print(addr, " -> ", weight, " via ", next_hop)

    def sendDV(self):
        """Sends its distance vector to the neighbours
        """
        current_rt = self.routing_table.copy()
        for addr, (weight, next_hop) in current_rt.items():
            # if is a neightbour
            if addr != self.addr and addr == next_hop:
                print("Node ", self.addr, " sends DV to ", addr)
                self.net.transmit(self.addr, addr, self.routing_table)

if __name__ == "__main__":
    net = Network()
    
    net.add_node("A")
    net.add_node("B")
    net.add_node("C")
    net.add_node("D")

    net.add_edge("A", "B", 7)
    net.add_edge("B", "C", 5)
    net.add_edge("C", "D", 20)
    net.add_edge("A", "D", 2)
    
    net.print_tables()
    print("\n\n\n\n")
    # edge cost change test
    net.add_edge("C", "D", 1) # modifies an existing edge if it exists
    net.print_tables()
    
    print("\n\n\n\n")
    net.remove_edge("C", "D")
    net.print_tables()