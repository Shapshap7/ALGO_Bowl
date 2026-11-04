import csv
import networkx as nx
import optimizedAkarialgorithm

inputGrapharray = optimizedAkarialgorithm.main()
with open("mini4x4.csv",'w',newline="") as out:
    for row in inputGrapharray:
        stringCsv = ''.join(row)
        write = csv.writer(out)
        write.writerow(stringCsv)

