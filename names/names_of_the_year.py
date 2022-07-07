# Top Baby Names
# Aditi Nukala
# Makeup Assignment
# Determing top names for a given year
#part 1


def main():
# getting file name from user input
    filename = input("Enter filename:")
    year = int(input("Enter year:"))
# running top names method
    print_top_names_for_year(filename,year)
    
def print_top_names_for_year(filename, year, num=10):
# opening file for reading
    infile = open (filename, 'r')
# creating empty list to get popularity of names
    names = []
# formatting lines for reading
    infile.readline()
# providing offset for indexing purposes
    index = year - 1879
# creating tuple and appending tuple list
    for line in infile:
        line = line.strip()
        line = line.split(",")
        name_tuple = (int(line[index]), line[0])
        names.append(name_tuple)
# sorting names by count
    names = sorted (names, reverse=True)
# creating list of top 10
    top10 = names[0:num]
# making list for top 10 formatted properly
    for i in top10:
        print(i[1],i[0])
    

main()	
