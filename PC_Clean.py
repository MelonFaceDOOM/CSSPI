# -*- coding: utf-8 -*-
import csv
from PC_dicts import cleaning_dicts

def main():
    
    r = csv.reader(open(r'b_Merge Output/PC_merge.csv', encoding ="utf8"))
    data = [l for l in r]
    headers = data[0]
    
    new_data = []
    
    for header in headers:
    #following cleaning procedure according to name
        var_index = headers.index(header)
        to_clean = [row[var_index] for row in data[1:]] # define the range that need to be cleaned
        
        #look for the variable name in the dict file. If a corresponding dict is found, clean the variable. otherwise, do nothing
        try:
            dict = getattr(cleaning_dicts, header)
        except:
            dict = {}
            
        if dict == {}:
            new_data.append(to_clean) # if no cleaning needs to be done to this column, the original column can be appended to new_data
        else:
            #pass values from the original column one at a time to the appropriate function and build a new list based on these.
            cleaned = [] 
            for item in to_clean:
                item = item.lower().strip(' ')
                
                if item == "":
                    item = "Unknown"
                else:
                    item = clean_var(item, dict)
                    
                cleaned.append(item)
            
            new_data.append(cleaned) # append new column to new table list
    
    #add headers to each column
    for idx, column in enumerate(new_data):
        column.insert(0,headers[idx])
        
    #create new column for year variable
    year_var = ["Year"]
    for date_val in new_data[headers.index('DateOfCall')][1:]:
        year_var.append(date_val[:4])
    new_data.append(year_var)
    
    #transpose and write to csv
    transposed = zip(*new_data)
    writer = csv.writer(open(r'c_Clean Output/PC_cleaned.csv', 'w', encoding='utf-8'),lineterminator='\n')
    writer.writerows(transposed)

def clean_var(string, dict):
    if len(string) < 1:
        return string
    try:
        string = str(string) # convert input to string
        out = dict[string]
        return out
    except:
        #if the string isn't found in the dictionary, return the string.
        return string    

if __name__ == "__main__":
    main()