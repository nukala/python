import plainchart

def main():
    counts_by_name = make_name_dict()
    counts = get_counts_for_name(counts_by_name)
    
    # Uncomment for Part 4
    totals_by_year = get_totals_by_year()
    pct_counts = percentages(counts,totals_by_year)

    # Uncomment for Parts 3 and 4
    make_graph(pct_counts)

def make_name_dict():
    infile = open ("countsByName.test.csv", "r")
    names = {}
    line = infile.readline()
    for line in infile:
        line = line.split(",")
        name = line[0]
        count = []
        for i in range(1,len(line)):
            count.append(int(line[i]))
        names[name] = count
    infile.close()
    return names

def get_counts_for_name(counts_by_name):
    while True:
        name = input("What's your name?")
        if name in counts_by_name:
            counts = counts_by_name[name]
            print("Found", name)
            print("Maximum Count =", max(counts))
            return counts
        else:
            continue

def make_graph(values):
    chart = plainchart.PlainChart(values, 7)
    print(chart.render())
    # Print the X axis
    print_x_axis()
    
def get_totals_by_year():
    infile = open("totalsByYear.csv", "r")
    totals = {}
    # throw away the first line
    line = infile.readline()
    for line in infile:
        parts = line.split(",")
        year = parts[0]
        population = parts[1]
        totals[year] = population

    infile.close()
    return totals


def percentages(counts,totals_by_year):
    pcts = []
    for year in totals_by_year:
        population = int(totals_by_year[year])
        i = int(year) - 1880
        pcts.append(counts[i] / int(population))

    return pcts

# Prints the X axis for the chart
def print_x_axis():
    line = ""
    for y in range(1880,2017,10):
        line = line + "|" + str(y) + " " * 5 
    print(line)

main()

# create aa dictionary, key is name, value is the list of all the coutns for every year

