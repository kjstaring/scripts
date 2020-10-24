from insertion_MongoDB import store_in_MongoDB
from extract_MongoDB import extract_in_MongoDB
from compare_MongoDB import check_files_MongoDB

#main file 
def mainStorage(file_name, new_old):
    store_in_MongoDB(file_name, new_old)
    sentence1 = str(file_name + ' is stored in MongoDB')
    print(sentence1)
    extract_in_MongoDB(file_name)
    sentence2 = str(file_name + ' is extracted from MongoDB')
    print(sentence2)
    check_files_MongoDB(file_name)

file_name = input('Enter file name: ')
new_old = input('Enter new_or_old: ')
mainStorage(file_name, new_old)


