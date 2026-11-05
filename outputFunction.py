import csv
import networkx as nx
import optimizedAkarialgorithm

inputGrapharray = optimizedAkarialgorithm.main()
violations = str(inputGrapharray[0])
graph = inputGrapharray[1]
with open("output.txt", 'w') as out:
    out.write(violations + '\n')
    for row in graph:
        stringLine = ''.join(row) + '\n'
        out.write(stringLine)
