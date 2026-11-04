import csv
import networkx as nx
import optimizedAkarialgorithm

inputGrapharray = optimizedAkarialgorithm.main()
with open("output.txt",'w') as out:
    for row in inputGrapharray:
        stringLine = ''.join(row) + '\n'
        out.write(stringLine)

