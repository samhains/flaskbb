import csv

with open('ilxor.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile)
    print(csvreader)
    for row in csvreader:
        print(row)