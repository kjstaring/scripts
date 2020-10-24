import json
import os

def compare_PostgreSQL(file_name): 
    #1. Open original CityJSON file 
    StringOriginal = str('/Users/karinstaring/GeomaticsThesis/datasets/old/' + file_name + '.json')
    original = open(StringOriginal, encoding='utf-8-sig')
    #2. Original CityJSON file size 
    size_original = os.path.getsize(StringOriginal)/1024 
    unit = 'KB'
    if size_original > 1000: 
        size_original = size_original/1024
        unit = 'MB'
    print("The original CityJSON file size in " + str(unit)+ ": " + str(size_original))
    #3. Load the original CityJSON file as JSON 
    a = json.load(original) 
    
    #4. Open new CityJSON file 
    StringExtracted = str('/Users/karinstaring/GeomaticsThesis/datasets/new/' + file_name + '.json')
    extracted = open(StringExtracted, encoding='utf-8-sig')
    #5. New CityJSON file size 
    size_extracted = os.path.getsize(StringExtracted)/1024
    if unit == 'MB': 
        size_extracted = size_extracted/1024
    #6. Load the new CityJSON file as JSON 
    b = json.load(extracted) 

    #7. Calculate differences in size 
    difference = abs(size_original - size_extracted)
    print("difference file sizes in " + str(unit) + ": " + str(difference))

    #cjio validation for original and extracted file 
    #print("cjio validate original file: ")
    #os.system('cjio ' + str(StringOriginal) + ' validate')
    #print("cjio validate extracted file: ")
    #os.system('cjio ' + str(StringExtracted) + ' validate')
    
    #val3dity for original and extracted file 
    #print("val3dity original file: ")
    #os.system("/usr/local/Cellar/val3dity/2.2.0/bin/val3dity  " + str(StringOriginal))
    #print("val3dity extracted file: ")
    #os.system("/usr/local/Cellar/val3dity/2.2.0/bin/val3dity  " + str(StringExtracted))

    #8. Compare keys and values: It will be investigated if the same keys are present and if the values are the same. This is done with comparison operators. 
    changes_list = [] 
    for order1 in b.keys():
        if order1 not in a:
            print("found new key {0} in the extracted file".format(order1))
            continue
            
        else:
            if a[order1] != b[order1]: 
                print("for key {0} values are different".format(order1))
                if order1 == 'CityObjects':
                    for obj_b in b[order1]:
                        obj_a = a[order1][obj_b]
                        #print(b[order1][obj_b])
                        #print(obj_a)
                        for order2 in b[order1][obj_b].keys():
                            if order2 not in obj_a:
                                print("found new key {0} in the extracted file".format(order2))
                                continue
                            else:
                                if obj_a[order2] != b[order1][obj_b][order2]:
                                    value_string = "for key {0} values are different".format(order2)
                                    if value_string not in changes_list:
                                        changes_list.append(value_string)
                                if order2 == 'geometry':
                                    i = 0 
                                    for geom in b[order1][obj_b][order2]:
                                        for order3 in b[order1][obj_b][order2][i].keys():
                                            geom_a = obj_a[order2][i][order3]
                                            if order3 not in obj_a[order2][i]:
                                                print("found new key {0} in the extracted file".format(order3))
                                                continue
                                            else:
                                                if b[order1][obj_b][order2][i][order3] != geom_a:
                                                    value_string = "for key {0} values are different".format(order3)
                                                    if value_string not in changes_list:
                                                        print(b[order1][obj_b][order2][i][order3])
                                                        changes_list.append(value_string)
                                        i = i + 1 
                                    
    for order1 in a.keys():
        if order1 not in b:
            print("found new key {0} in the original file".format(order1))
            continue
        else:
            continue 
    print(changes_list)