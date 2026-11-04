import csv
import networkx as nx
import optimizedAkarialgorithm

inputGrapharray = optimizedAkarialgorithm.main()
with open("output.csv",'w',newline="") as out:
    for row in inputGrapharray:
        stringCsv = ''.join(row)
        write = csv.writer(out)
        write.writerow(stringCsv)

