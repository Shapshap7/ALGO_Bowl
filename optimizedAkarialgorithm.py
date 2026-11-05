#INPUT:William
#Input: File with .,1,2,3,4,X
#Output: A NetworkX grid with states of each cell contained within each node
#Note:
    # Difficulty is defined as the number of groups that find the best solution
    # The more number of groups that find your best solution the less points you get
    # The less number of groups that get that solution the more points you get.
# Ideas:

import networkx as nx
import inputGenerator

def input():
    """
    Size =  line1.split
row = Size[0]
col = Size[1]
for lines in file:
   line.split
 for each in line:
 if each == X:
    Type = black:
     MaxLight = None
 elif each == . :
    Type = white
      MaxLight = None 
 else:
     type = black 
       MaxLight = int(each)
    g.addnode((r,c), cell_type = Type, MaxAdj = MaxLight, CurLight = 0, isLit = false, hasLightBulb = false)
    r++;
    """

#ALGORITHM:Steve,Wiliam,David
#Input: NetworkX Grid
#Output: new NetworkX grid with L inserted where . should have been
    # Ideas:


    # key: (r,c) 
    # recFunction (r-1,c) hey call node key (r-1,c) recFunction ((r-1)-1,c): base case: if graph has node, else return.
    # SecBasecase: if node["is an X or blockNum"], thirdBaseCase: if node["isbulb"] == true, remove
def helperRec(row,col,dRow,dCol,maxRow,maxCol,NXGraph):
    # Base Case1
    if(row < 0 or col < 0):
        return False
    if(row>=maxRow or col>=maxCol):
        return False
    # Base case 2
    if(NXGraph.nodes[(row,col)]["cellType"] != "white"):
        return False
    # bas3e case 3
    if(NXGraph.nodes[(row,col)]["hasBulb"] == True):
        return True

    # recursive()
    result = helperRec(row+dRow,col+dCol,dRow,dCol,maxRow,maxCol,NXGraph)

    return result




def alg(graphs):
    # g = [['B','B','X','.'],
    #      ['.','B','B','.'],
    #      ['B','0','X','.'],
    #      ['B','.','.','.']]

    graph2D = graphs[0]
    graphNX = graphs[1]
    maxSizerow = len(graph2D)
    maxSizecol = len(graph2D[0])

    for node in graphNX.nodes: 
        # checkes the current node and sees if it can place a bulb there
        if (graphNX.nodes[node]["cellType"] == "white" and 
            graphNX.nodes[node]["isLit"] == False and 
            graphNX.nodes[node]["hasBulb"] == False):

            for neighbor in graphNX.neighbors(node):
                if (graphNX.nodes[neighbor]["cellType"] == "#black"):
                    if (graphNX.nodes[neighbor]["MaxAdj"] > graphNX.nodes[neighbor]["curAdj"]):
                        graphNX.nodes[neighbor]["curAdj"] += 1 
                        graphNX.nodes[node]["hasBulb"] = True
                        row = node[0]
                        col = node[1]
                        graph2D[row][col] = "L"
                    
                    if (graphNX.nodes[neighbor]["MaxAdj"] == 0):
                        graphNX.nodes[node]["hasBulb"] = False
                        row = node[0]
                        col = node[1]
                        graph2D[row][col] = "."
                        break
                    
                    

    '''
    To find a violation:
        We'll loop over every square number block and check its adjacent neighboring nodes.
        We'll make sure that the number of bulbs neighboring the number block is less than or equal
        to the MaxAdj number. If this is false, for example we have too many bulbs adjacent to the number
        block we will remove curAdj - MaxAdj bulbs from the neighbors and set them hasBulb = False. Update 
        curAdj as well.
    '''
    currViolations = 0
    for nodeKey in graphNX.nodes:
        currNode = graphNX.nodes[nodeKey]
        
        if (currNode["cellType"] == "#black" and currNode["MaxAdj"] is not None):
            actual_bulbs = sum(1 for neighbor in graphNX.neighbors(nodeKey) if graphNX.nodes[neighbor]["hasBulb"])
            #check curAdj >= MaxAdj
            if(actual_bulbs != currNode["MaxAdj"]):
                #We have a violation
                currViolations += 1
        if (currNode["hasBulb"] == True):
            currNoderow = nodeKey[0]
            currNodecol = nodeKey[1]
            # Go all the way North
            if (helperRec(currNoderow-1, currNodecol, -1, 0, maxSizerow, maxSizecol, graphNX) or
                helperRec(currNoderow+1, currNodecol, 1, 0, maxSizerow, maxSizecol, graphNX) or
                helperRec(currNoderow, currNodecol-1, 0, -1, maxSizerow, maxSizecol, graphNX) or
                helperRec(currNoderow, currNodecol+1, 0, 1, maxSizerow, maxSizecol, graphNX)):
                currViolations += 1

    illuminated_cells = set()

    # Step 1: Cast rays from all bulbs
    for nodeKey in graphNX.nodes:
        if graphNX.nodes[nodeKey].get("hasBulb") == True:
            r, c = nodeKey
            illuminated_cells.add((r, c))  # The bulb's own cell is illuminated

            # Cast light rays in all 4 directions
            for dRow, dCol in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
                curr_r, curr_c = r + dRow, c + dCol

                # Travel in a straight line until hitting a wall/number or grid edge
                while 0 <= curr_r < maxSizerow and 0 <= curr_c < maxSizecol:
                    target_node = graphNX.nodes[(curr_r, curr_c)]
                    
                    # STOP only if hitting a black wall or number block
                    if target_node.get("cellType") != "white":
                        break

                    # Add cell to illuminated set (includes empty white cells and other bulbs)
                    illuminated_cells.add((curr_r, curr_c))
                    curr_r += dRow
                    curr_c += dCol

    # Step 2: Count how many white cells remain unlit
    # Step 2: Count how many white cells remain unlit
    unlitCells = 0

    for nodeKey in graphNX.nodes:
        node = graphNX.nodes[nodeKey]

        if node.get("cellType") == "white":
            if nodeKey not in illuminated_cells:
                unlitCells += 1

    print("Violations:", currViolations)
    print("Unlit cells:", unlitCells)

    return (currViolations,graph2D)
    """if square empty:
    check adjacents for # squares
    for each number square adjacent:
                count all lights next to it:
                # Instead maybe use a state
                IF "# = light_count" break and dont place light, ELSE check next # square 
    if all "#=light_count" checks return false, place a light there
    class square {
    int final light_count = 3;
    int light_adjacent = 0;
    """

    #Make sure to list sections of the Algorithm:
    #1. Choose a traversal method for the grid
    #2. Every step you make determine Rule 1 and 2
        # Rule 1, no light can touch another light
        # Rule 2, if you are on or near a number block you must have n number of lights next to 
        # Number block such that n = {0,1,2,3,4}
       

#OUTPUT:Steve
#Input: 2D grid with L inserted where .'s were
#Output: .csv with original file with updated L cells.
    # Ideas: For the output we are going to create a .csv file as the optimal solution 
    # where our NetworkX graph will 

def main():
    graph1 = inputGenerator.main()
    returnedGraph = alg(graph1)   
    return returnedGraph

if __name__ == "__main__":
    main()