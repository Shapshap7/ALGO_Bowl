#INPUT:David
#Input: File with .,1,2,3,4,X
#Output: A NetworkX grid with states of each cell contained within each node
#Note:
    # Difficulty is defined as the number of groups that find the best solution
    # The more number of groups that find your best solution the less points you get
    # The less number of groups that get that solution the more points you get.
# Ideas:

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
    """

#ALGORITHM:Steve,Wiliam,David
#Input: NetworkX Grid
#Output: new NetworkX grid with L inserted where . should have been
    # Ideas:
def alg():
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
    # Ideas: