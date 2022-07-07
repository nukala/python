import plainchart

def main():
    counts_by_name = make_name_dict()
    counts = get_counts_for_name(counts_by_name)
    
    # Uncomment for Part 4
    # totals_by_year = get_totals_by_year()
    # pct_counts = percentages(counts,totals_by_year)

    # Uncomment for Parts 3 and 4
    # make_graph(counts)

def make_name_dict():
    return

def get_counts_for_name(counts_by_name):
    return

def make_graph(values):
    # Print the X axis
    print_x_axis()
    

def get_totals_by_year():
    return 

def percentages(counts,totals_by_year):
    return 

# Prints the X axis for the chart
def print_x_axis():
    line = ""
    for y in range(1880,2017,10):
        line = line + "|" + str(y) + " " * 5 
    print(line)

main()

