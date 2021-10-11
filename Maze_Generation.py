import random
import math
from queue import PriorityQueue
import heapq
import pygame

# RGB colors
BLACK = (0,0,0)
WHITISH = (250,235,215)
RANDOM = (121,213,43)
PURP = (75,0,130)
RED = (220,20,60)
GREEN = (0,255,0)

W, H = 1000, 1000 # Window size
WINDOW = pygame.display.set_mode((W, H)) # Main window
pygame.display.set_icon(pygame.image.load('Images/maze-icon-12.jpg'))

final_path = []

# Class to create vertices
class Vertex: 
    def __init__(self, n):
        self.name = n

# Class to create graphs using said vertices
class Graph: 
    vertices = {}
    edges = []
    edge_indices = {}
    dedges = []

    # Add vertices to the graph
    def add_vertex(self, vertex): 
        if isinstance(vertex, Vertex) and vertex.name not in self.vertices:
            
            self.vertices[vertex.name] = vertex
            for row in self.edges:
                row.append(math.inf)
            self.edges.append([math.inf]*(len(self.edges)+1))
            self.edge_indices[vertex.name] = len(self.edge_indices)
            return True
        else:
            return False

    # Add edges to the graph
    def add_edge(self, u, v, weight): 
        if u in self.vertices and v in self.vertices:
            self.edges[self.edge_indices[u]][self.edge_indices[v]] = weight
            self.edges[self.edge_indices[v]][self.edge_indices[u]] = weight
            return True
        else: 
            return False

    # Print out the graph
    def print_graph(self): 
        for v, i in sorted(self.edge_indices.items()):
            print(str(v)+' ', end='')
            for j in range(len(self.edges)):
                print(self.edges[i][j], end='')
            print(' ')

# Priority queue that stores edges for Prim's algorithm
class PriorityQueue: 
    def __init__(self):
        self.data = []
        self.index = 0
    
    # Add items to the priority queue
    def push(self, u, v, prio): 
        heapq.heappush(self.data, (prio, self.index, u, v))
        self.index += 1

    # Extract items from the priority queue
    def pop(self): 
        return heapq.heappop(self.data)

class Queue:
    def __init__(self):
        self.data = []

    def enqueue(self, node):
        self.data.append(node)
    
    def dequeue(self):
        return self.data.pop(0)

# Generate graph that will serve as the base for our maze (grid)
def grid_gen(): 
    n = random.randint(10, 50)           # Set size of the grid
    plus = n+n
    times = n*n
    for i in range(1,times+1):
        g.add_vertex(Vertex(i))
    for j in range(1, times+1):
        x = random.randint(1,10)         # Pick a random horizontal edgeweight
        g.add_edge(j, plus+1-j, x)
        if j%n==0:
            plus += n+n
        x = random.randint(1,10)         # Pick a random vertical edgeweight
        g.add_edge(j, j+1, x)

    print("Original: ",g.edges)

# Add the adjacent edges to the Priority Queue
def addEdges(nodeIndex, visited, pq): 
    visited[nodeIndex] = True
    edges = g.edges[nodeIndex]
    for i, edge in enumerate(edges):
        if edge is not math.inf and i+1 not in visited:
            pq.push(g.edges.index(edges)+1, i+1, edge)

# Utilize Prim's algorithm to find a minimum spanning tree of the generated grid-like UAG, then convert it to an adjacency matrix
def prim(s = 0): 
    n = len(g.vertices)
    visited = [False for number in range(n)]
    pq = PriorityQueue()
    m = n-1
    edgeCount = 0
    mstEdges = [None for number in range(m)]   
    addEdges(s, visited, pq)

    while len(pq.data) != 0 and edgeCount != m:
        edge = pq.pop()
        nodeIndex = edge[3]-1

        if visited[nodeIndex]:
            continue
        
        edge = edge[:1] + edge[2:]
        mstEdges[edgeCount] = edge
        edgeCount += 1
        addEdges(nodeIndex, visited, pq)

    g.edges = [[math.inf for number in range(n)] for no in range(n)]

    for i in mstEdges:
        g.edges[i[1]-1][i[2]-1] = i[0]
        g.edges[i[2]-1][i[1]-1] = i[0]

    return g.edges

# Generate 2 dicts of rectangle-objects as tuples in order to store all nodes and edges
def nodes_grid(rect_width: int, line_width: int, offset: int):
    nodes = {} 
    edges = {} # {(parent_node, child_node) -> (left, top, rect_width, rect_width)}
    top = int(line_width/2+offset)
    left = int(line_width/2+offset)
    inc = int(rect_width*2)
    for j in g.vertices:
        nodes[j] = (left, top, rect_width, rect_width)
        top += inc
        if(j%math.sqrt(len(g.vertices))==0):
            left+=rect_width*2
            top -= inc
            inc *= -1
    for m, node in enumerate(g.edges):
        for k, edge in enumerate(node):
            if(edge<math.inf):
                left = (nodes[m+1][0]+nodes[k+1][0])/2
                top = (nodes[m+1][1]+nodes[k+1][1])/2
                if (left, top, rect_width, rect_width) not in edges.values():
                    edges[(m+1,k+1)] = (left, top, rect_width, rect_width)
        
    return nodes, edges

# Draw the maze
def draw():
    node_count = len(g.vertices)
    line_width = math.floor(1000/math.sqrt(node_count))                    # Pick a line-width relative to the size of the maze
    mid_width = W-line_width                                               # Width of the inside of the maze-border
    rect_width = math.floor(mid_width/(2*math.sqrt(node_count)-1))         # Width of the rectangles that make up the nodes in the maze
    total_width = (math.sqrt(node_count)*2-1)*rect_width
    offset = (mid_width-total_width)/2
    nodes, edges = nodes_grid(rect_width, line_width, offset)
    end_node = node_count
    if(node_count%2==0):
        end_node = node_count+1-math.sqrt(node_count)
    for key, node in nodes.items():
        if(key == end_node):
            pygame.draw.rect(WINDOW, RED, node)
        elif(key == 1):
            pygame.draw.rect(WINDOW, GREEN, node)
        else:
            pygame.draw.rect(WINDOW, WHITISH, node)
    for key, edge in edges.items():
        pygame.draw.rect(WINDOW, WHITISH, edge)
    rect = pygame.Rect(0, 0, W, H)
    for step in final_path:
        if(step != 1 and step != end_node):
            pygame.draw.rect(WINDOW, PURP, nodes[step])
        if(step != final_path[-1]):
            try: pygame.draw.rect(WINDOW, PURP, edges[(step, final_path[final_path.index(step)+1])])
            except: pygame.draw.rect(WINDOW, PURP, edges[(final_path[final_path.index(step)+1], step)])
    pygame.draw.rect(WINDOW, BLACK, rect, line_width)
    return end_node

def find_path(s, e, path):
    if(e == s):
        return
    for key, value in path.items():
        if e in value:
            final_path.append(key)
            find_path(s, key, path)

def solve(s):
    q = Queue()
    q.enqueue(s)

    visited = [False for n in range(len(g.vertices))]
    visited[s-1] = True
    path = {}

    while len(q.data)!=0:
        node = q.dequeue()
        nb = []
        for i, next_node in enumerate(g.edges[node-1]):
            if(next_node < math.inf and not visited[i]):
                nb.append(i+1)
        path[node] = nb
        for nextt in nb:
            if visited[nextt-1] == False:
                q.enqueue(nextt)
                visited[nextt-1] = True
    return path

def bfs(e): # Find the shortest (and only) path in the maze
    s = 1
    path = solve(s)
    find_path(s, e, path)
    final_path.reverse()
    final_path.append(e)

# Display the pygame window and set basic parameters
def display(graph): 
    pygame.display.set_caption("Maze generation")
    count = 0
    while True:
        WINDOW.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        end_node = draw()
        if(count < 1):
            bfs(end_node)
        count += 1
        pygame.display.flip()

# Generate a new maze
def new_maze(): 
    g.vertices = {}
    g.edge_indices = {}
    g.edges = []
    g.dedges = []

    grid_gen()
    mst = prim()
    print("MST:", mst)
    display(g)

if __name__ == "__main__":
    g = Graph()
    new_maze()
    
