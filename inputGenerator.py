# Akari Input Generation .
# Authors: Steve Dimas, William Shappley, David Baloyi
# Date: 11/1/2026


import networkx as nx
import csv


#read and open the file
def input(): 
    with open('SolvableInput.csv', 'r') as f:
        reader = csv.reader(f)
        #data = list(reader)

        #get rows and columns from the first line of the csv file
        G = nx.Graph()
        graph = []
        size = next(reader)
        num_rows = int(size[0])
        num_cols = int(size[1])

        #read and create nodes 
        r = 0
        for line in reader:
            #make a row for the 2D Array to have
            graph_rows = []
            for c in range(num_cols):
                value = line[c]
                graph_rows.append(value)
                #check if the square is a blank, black square
                if value == "X":
                    Type = "black"
                    Adj = None
                #check if the value is a white space 
                elif value == ".":
                    Type = "white"
                    Adj = None
                #if neither of those we know it's a # square 
                else:
                    Type = "#black"
                    Adj = int(value)
                #now we can add the node. 
                # NOTE: we can already assume the values for the res of the variables per node before traversal 
                G.add_node((r,c), cellType = Type, MaxAdj = Adj, curAdj = 0, isLit = False, hasBulb = False)
            r += 1
            #add the row to the total graph array
            graph.append(graph_rows)

    #make edges NOTE: codes are connected to there orthgonal adjacent nodes ONLY
    for r in range(num_rows):
        for c in range(num_cols):
            #For each square up and down, check if it exists, if so add
            # down check
            if  (r+1) < num_rows:
                G.add_edge((r,c),(r+1,c))
            #up check
            if (r-1) >= 0: 
                G.add_edge((r,c),(r-1,c))
            #For each square left and right, check if it exits, if so add 
            # right check
            if  (c+1) < num_cols:
                G.add_edge((r,c),(r,c+1))
            #left check
            if (c-1) >= 0: 
                G.add_edge((r,c),(r,c-1))

    graphs = (graph, G)
    return graphs


def main():
    processedFile = input()
    return processedFile

if __name__ == "__main__":
    main()