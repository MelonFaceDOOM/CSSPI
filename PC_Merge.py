import csv
import sys

def main():
    with open(r'a_Merge Input/variable_mapping.csv','r') as csvfile:
        variable_mapping_csv = csv.reader(csvfile, delimiter=',')
        
        #create list of source files based on first row in csv
        sourcefile_list = next(variable_mapping_csv)
        
        #create list of master variables and the equivalent vars for all source files
        header_list = [] # list of all headers for all sources
        master_header_list = [] # list of only master headers
        for row in variable_mapping_csv:
            header_list.append(row)
            master_header_list.append(row[0])
        
    number_of_columns = len(header_list[0])
    
    #add one column to specify source file name
    merged_db = [["source"] + master_header_list]
    
    #Loop through each of the other columns, find the appropriate column, and paste it to the appropriate location
    for i in range(1,number_of_columns):
    
        #create database that will house re-arranged source data with correct headers
        source_rearranged = []
        
        #find & open source file
        sourcefile_name = r'a_Merge Input/' + sourcefile_list[i] + ".csv"
        with open(sourcefile_name, 'r') as sourcefile:
            sourcefile_csv = csv.reader(sourcefile, delimiter=',')
            sourcefile_data = list(sourcefile_csv)
            headers_sourcefile = sourcefile_data[0] #create list of headers from the first row in sourcefile

        for row in header_list:
            varname_master = row[0]
            varname_source = row[i]
            
            if varname_source == "NULL":
                columnlength = len(source_rearranged[0]) # this will only work if a non-NULL column has already been appended.
                emptylist = []
                for j in range(0,columnlength):
                    emptylist.append("")
                #append list of blanks
                source_rearranged.append(emptylist)
            
            else:
                #find varname in source file
                source_header_index = headers_sourcefile.index(varname_source)
                
                #create list with values in column, excluding header
                copycolumn = []
                firstrow = True
                for source_row in sourcefile_data:
                    if firstrow == True:
                        firstrow = False
                        continue
                    copycolumn.append(source_row[source_header_index])
                
                #append the column to the new database
                source_rearranged.append(copycolumn)
        
        #add a new column that specifies the sourcefile name:
        sourcename_column = [sourcefile_list[i]]*len(source_rearranged[0])
        source_rearranged = [sourcename_column] + source_rearranged
        
        source_rearranged = list(map(list, zip(*source_rearranged)))
        merged_db = merged_db + source_rearranged
    
    with open(r'b_Merge Output/PC_merge.csv', 'w', newline='') as destination_file:
        csv.writer(destination_file).writerows(merged_db)

if __name__ == "__main__":
    main()