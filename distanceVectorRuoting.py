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
        # Creates a connection
        self.nodes[node1].neighbour(node2, weight)
        self.nodes[node2].neighbour(node1, weight)
        # Sends the DV to the neighbours
        self.nodes[node1].sendDV()
        self.nodes[node2].sendDV()
        # Updates the edge
        present, tuple = self.usedTuple(node1, node2)
        if present:
            self.edges[tuple] = weight
        else:
            self.edges[(node1, node2)] = weight
    
    def usedTuple(self, node1: str, node2: str):
        """
        Returns the tuple used to store the edge between node1 and node2, if present
        """
        if (node1, node2) in self.edges:
            return True, (node1, node2)
        else:
            if (node2, node1) in self.edges:
                return True, (node2, node1)
            else:
                return False, None
    
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
        print("\nNETWORK - routing tables")
        for addr, node in self.nodes.items():
            print("NODE: ", addr, " - routing table")
            node.print_table()
            print("")

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
        print("NODE: ", self.addr, " - created")
    
    def neighbour(self, node: str, weight):
        """Updates a neighbour connection

        Args:
            node (str): node to discover
            weight (int): weight of the edge
        """
        if node != self.addr:
            # if the connection already exists
            if node in self.routing_table and self.routing_table[node][1] == node:
                print("EDGE: ", self.addr, " - ", node, " updating with ", weight)
                current_edgeWeight = self.routing_table[node][0]
                # I update the routes that use it
                for addr, (current_routeWeight, next_hop) in self.routing_table.items():
                    if next_hop == node:
                        self.routing_table[addr] = (current_routeWeight - current_edgeWeight + weight , node)
            else:
                print("NODE: ", self.addr, " - has a new neighbour ", node, " with weight ", weight)
            self.routing_table[node] = (weight, node)
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
        # if the node is reachable reads the DV received and updates its routing table
        if hop in self.routing_table:
            for addr, (weight, next_hop) in dv.items():
                if addr != self.addr:
                    new_distance = weight + self.routing_table[hop][0]
                    # if it's unknow we add it
                    if addr not in self.routing_table:
                        self.routing_table[addr] = (new_distance, hop)
                        updated = True
                    # if it's known we update it
                    elif new_distance < self.routing_table[addr][0]:
                            self.routing_table[addr] = (new_distance, hop)
                            updated = True
        if updated:
            self.updatedRT()
    
    def updatedRT(self):
        # prints to screen
        print(f"NODE: {self.addr} - updated its routing table")
        self.print_table()
        # communicates new DV to neighbours
        self.sendDV()
    
    def print_table(self):
        print("addr  | weight | next_hop")
        for addr, (weight, next_hop) in self.routing_table.items():
            print(addr, " -> ", weight, " via ", next_hop)

    def sendDV(self):
        """Sends its distance vector to the neighbours
        """
        current_rt = self.routing_table.copy()
        for addr, (weight, next_hop) in current_rt.items():
            # if is a neighbour
            if addr != self.addr and addr == next_hop:
                print("NODE: ", self.addr, " - sends DV to ", addr)
                self.net.transmit(self.addr, addr, self.splitHorizon(addr))

    def splitHorizon(self, addr: str):
        """Returns the routing table with split horizon applied
            (the routes traversed through the neighbour are removed: weight=inf)

        Args:
            addr (str): addr of the neighbour to which the DV is being sent

        Returns:
            dict: the routing table with split horizon applied
        """
        routing_table_mod = dict()
        for dst, (weight, next_hop) in self.routing_table.items():
            # if the route goes through the node that is receiving my Distance Vector
            if next_hop == addr:
                weight = float("inf")
            routing_table_mod[dst] = (weight, next_hop)
        return routing_table_mod


if __name__ == "__main__":
    net = Network()
    # nodes creation
    net.add_node("R1")
    net.add_node("R2")
    net.add_node("R3")
    net.add_node("R4")
    # edges creation
    net.add_edge("R1", "R2", 8)
    net.add_edge("R2", "R3", 4)
    net.add_edge("R3", "R4", 21)
    net.add_edge("R1", "R4", 3)
    net.print_tables()
    # update of an edge
    print("\n")
    net.add_edge("R3", "R4", 1) # modifies an existing edge if it exists
    net.print_tables()
