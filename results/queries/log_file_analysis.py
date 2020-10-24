import os 
import csv 

def find_duration(indexlist, index, f):
    index = index + 1
    if 'LOG:' in f[index].split():
        indexlist.append(index)
    else:
        find_duration(indexlist, index, f)
        
location = '/Users/karinstaring/thesis/script/finally/Karin_Staring_Geomatics_Thesis/results/queries/query2/'
for filename in os.listdir(location):
    if filename == 'quer2_postgresql.log':
       f  = open(os.path.join(location, 'query2_postgresql.log'), "r").readlines()

cityobject_number = 0 
all_times = []
i = 0 

for line in f:
    split_line = line.split()
    
    if 'statement:' in split_line and 'SELECT' in split_line:
        print(split_line) 
        if 'surfaces.id' in split_line:
            if cityobject_number == 1:
                all_times.append(one_query)
                cityobject_number = 0 
            cityobject_number = cityobject_number + 1

            one_query = [] 

            
            indexlist = []
            find_duration(indexlist, i, f)
            
            first_index = indexlist[0]
            duration = f[first_index]
            one_query.append(float(duration.split('duration:')[1].split('ms')[0].replace(' ', '')))
            
        else:
            indexlist = []
            find_duration(indexlist, i, f)
            
            first_index = indexlist[0]
            duration = f[first_index]
            one_query.append(float(duration.split('duration:')[1].split('ms')[0].replace(' ', '')))
 
    i = i + 1 
all_times.append(one_query)
file_name = 'query2_postgresql.csv'
with open('/Users/karinstaring/thesis/script/finally/Karin_Staring_Geomatics_Thesis/results/queries/query2/' + str(file_name), 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for row in all_times:
        writer.writerow(row)

