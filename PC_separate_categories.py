import csv
import pandas as pd
import re
from PC_dicts.symptoms_dict import symptoms_dict


def main(main_drug):
    
    #open files with information on drug classifications
    df_aapc = pd.read_csv(r'PC_dicts/AAPC codes.csv', sep=',', error_bad_lines=False, index_col=False, dtype='unicode')
    df_aapc_BC = pd.read_csv(r'PC_dicts/AAPC codes_BC.csv', sep=',', error_bad_lines=False, index_col=False, dtype='unicode')
    
    with open(r'c_Clean Output/PC_cleaned.csv','r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        
        #sort by casenumber, as it is crucial that all rows for a given case are grouped together.
        reader = sorted(reader, key=lambda row:(row['CaseNumber']), reverse=False)
    
    new_data = [] #Will be filled as the csv is processed

    #define a list of all variables that will be collected, and another list which specifies which ones accept list values
    case_variables=['source','CaseNumber','Year','AgeGroup','SEX','CallType','Reason','ExposureSite','CallerSite','CallerRelation','FSA','CallerCity','Province','Hospital','OutCome','Acuity','PatientFlow']
    drug_variables=['SubstanceGenericAAPCCCode','SubstanceProdCode','SubstanceFormula','SubstanceQty','SubstanceQtyUnits','SubstanceCalculation','Route','**Substance**']

    CaseNumber = 0 # set to 0 so that when the first row is compared against it, it will be different
    first_row = True

    for row in reader:
        
        #-----------------------------------------------#
        #Extra steps to take if this is a new CaseNumber#
        #-----------------------------------------------#
        
        if row['CaseNumber'] != CaseNumber:
                
            if first_row == True:
                first_row = False
            else:
                case_info['case_drugs'] = case_drugs
                new_data.append(case_info) # add row_info as a new case into the new_data list.

            case_info = {} #create dict to add all info from rows associated with this case
            case_drugs = [] #create list to add all drug info from rows associated with this case
            case_info['Symptoms'] = [] #define new key as list
            case_info['Treatment'] = [] #define new key as list
            
            #extract basic case info for variables that have one value per case
            for var in case_variables:
                case_info[var] = row[var]
        
        #---------------------------------------------------------------------#
        #These steps apply to all rows, regardless of whether it is a new case#
        #---------------------------------------------------------------------#
        
        #check to see if the AAPC code is already present in the drugs for this case
        aapc_present = False
        for case_drug in case_drugs:
            if case_drug['SubstanceGenericAAPCCCode'] == row['SubstanceGenericAAPCCCode']:
                aapc_present = True

        #if new aapc, record info. otherwise do nothing
        if aapc_present == False:
            #aapc not present, add new drug
            drug_row = {}
            for var in drug_variables:
                drug_row[var] = row[var]
            
            case_drugs.append(drug_row)

        #add unique symptom info
        if row['Symptoms'] in case_info['Symptoms']:
            pass
        else:
            case_info['Symptoms'].append(row['Symptoms'])
        
        #add unique treatment info
        if row['Treatment'] in case_info['Treatment']:
            pass
        else:
            case_info['Treatment'].append(row['Treatment'])
            
        CaseNumber = row['CaseNumber'] #update CaseNumber for the next iteration
    
    #append the last case, since the normal check at the start of the for loop won't have caught it
    case_info['case_drugs'] = case_drugs
    new_data.append(case_info)
    pcc = pd.DataFrame(new_data)
    
    #--------------------------------------------------------------------------------#
    #The database has now been restructured so that redundant information is removed;#
    #now it can be split into four tables                                            #
    #--------------------------------------------------------------------------------#

    #------------------------------#
    #TABLE 1 - Case Characteristics#
    #------------------------------#
    
    df_case_chars = pcc.drop(['case_drugs','Symptoms','Treatment'],axis=1)
    
    
    #------------------------------#
    #TABLE 2 - Case Drugs          #
    #------------------------------#
    
    #create new df with a row for each drug, along with its associated CaseNumber
    df_case_drugs = pd.DataFrame(pcc['case_drugs'].tolist(), index=pcc['CaseNumber']).stack()
    df_case_drugs = df_case_drugs.reset_index()
    df_case_drugs = pd.concat([df_case_drugs['CaseNumber'], 
        pd.DataFrame(df_case_drugs[0].tolist())], axis=1)
    
    #declare lists that will keep track of relevant drug information
    drug_classifications = []
    drug_names = []
    drug_names_BC = []
    
    #go through df_case_drugs and classify each aapc code
    for index, row in df_case_drugs.iterrows():
        drug_classifications.append(classify_drug(row['SubstanceGenericAAPCCCode'],df_aapc))
        drug_names.append(aapc_to_name(row['SubstanceGenericAAPCCCode'],df_aapc))
        drug_names_BC.append(aapc_to_name(row['SubstanceGenericAAPCCCode'],df_aapc_BC))
        
    #merge list of new values into df
    df_case_drugs['drug_classification']=drug_classifications
    df_case_drugs['drug_name_cleaned']=drug_names
    df_case_drugs['drug_name_cleaned_BC']=drug_names_BC

    #loop through. look at all drug classifications. Make new DB with casenumber and variable for "Opioid/Cannabis-only" or "combination"
    Case_drug_or_combination = []
    for i, row in df_case_chars.iterrows():
        one_case_drug_or_combination = {}
        one_case_drug_or_combination['CaseNumber'] = row['CaseNumber']
        df_one_case_drugs = df_case_drugs.loc[df_case_drugs['CaseNumber'] == row['CaseNumber']] #get subset of all rows with this CaseNumber
        one_case_drug_or_combination['Case_drug_or_combination'] = check_drug_or_combination(df_one_case_drugs,main_drug)
        Case_drug_or_combination.append(one_case_drug_or_combination)

    #convert to dataframe
    df_drug_or_combination = pd.DataFrame(Case_drug_or_combination)
    
    #------------------------------#
    #TABLE 3 - Case Symptoms       #
    #------------------------------#
    
    #create new df with a row for each symptom, along with its associated CaseNumber
    df_case_symptoms = pd.DataFrame(pcc['Symptoms'].tolist(), index=pcc['CaseNumber']).stack()
    df_case_symptoms = df_case_symptoms.reset_index()
    df_case_symptoms = pd.concat([df_case_symptoms['CaseNumber'], 
    pd.DataFrame(df_case_symptoms[0].tolist())], axis=1)
    df_case_symptoms = df_case_symptoms.rename(index=str,columns={"CaseNumber" : "CaseNumber", 0 : "Symptoms"})
    
    #remove the "/related"-type text at the end of each string
    for i, row in df_case_symptoms.iterrows():
        Symptoms_value = re.sub(r"[ ]{0,1}[\/-]{1,3}[ A-z]+$","",row['Symptoms'])
        df_case_symptoms.loc[i,'Symptoms'] = Symptoms_value

    
    #split all symptom strings with multiple symptoms into multiple rows
    reg_pattern = r"([0]*(?:[2-9]+|[1-9][0-9][0-9]*)[.][A-z ,.-/]+)[0-9]??"
    to_delete = [] # will hold a list of all row number values that contain a symptom that matches reg_pattern
    new_symptom_rows = []
    
    for i, row in df_case_symptoms.iterrows():
        if re.search(reg_pattern, str(row['Symptoms'])) is not None:
            to_delete.append(int(i))
            chain_list = [[row['CaseNumber'],symptom] for symptom in split_chain_text(row['Symptoms'])]
            new_symptom_rows = new_symptom_rows + chain_list
    
    df_case_symptoms = df_case_symptoms.drop(df_case_symptoms.index[to_delete]) #drop list of rows
    df_new_symptoms = pd.DataFrame(new_symptom_rows,columns=['CaseNumber','Symptoms'])
    df_case_symptoms = df_case_symptoms.append(df_new_symptoms)
    df_case_symptoms = df_case_symptoms.reset_index(drop=True)

    df_case_symptoms['Symptoms'] = df_case_symptoms['Symptoms'].map(lambda x: x.lstrip(" .123456789"))
    
    #further cleaning using a dict
    for i, row in df_case_symptoms.iterrows():
        symptom_input = row['Symptoms'].lower()
        symptom_input = symptom_input.strip(" ")
        if symptom_input == "":
            new_symptom_val="Unknown"
        else:
            new_symptom_val = symptoms_dict[symptom_input]
        df_case_symptoms.loc[i,'Symptoms'] = new_symptom_val

    #------------------------------#
    #TABLE 4 - Case Treatment      #
    #------------------------------#
    
    #create new df with a row for each treatment, along with its associated CaseNumber
    df_case_treatment = pd.DataFrame(pcc['Treatment'].tolist(), index=pcc['CaseNumber']).stack()
    df_case_treatment = df_case_treatment.reset_index()
    df_case_treatment = pd.concat([df_case_treatment['CaseNumber'], 
    pd.DataFrame(df_case_treatment[0].tolist())], axis=1)
    df_case_treatment = df_case_treatment.rename(index=str,columns={"CaseNumber" : "CaseNumber", 0 : "Treatment"})

    #split all strings with multiple treatments into multiple rows
    reg_pattern = r"([0]*(?:[2-9]+|[1-9][0-9][0-9]*)[.][A-z ,.-/]+)[0-9]??"
    to_delete = []
    new_treatment_rows = []
    for i, row in df_case_treatment.iterrows():
        if re.search(reg_pattern, str(row['Treatment'])) is not None:
            to_delete.append(int(i))
            chain_list = [[row['CaseNumber'],treatment] for treatment in split_chain_text(row['Treatment'])]
            new_treatment_rows = new_treatment_rows + chain_list
    df_case_treatment = df_case_treatment.drop(df_case_treatment.index[to_delete])
    df_case_treatment = df_case_treatment.reset_index(drop=True)
    df_new_treatments = pd.DataFrame(new_treatment_rows,columns=['CaseNumber','Treatment'])
    df_case_treatment = df_case_treatment.append(df_new_treatments)

    df_case_treatment['Treatment'] = df_case_treatment['Treatment'].map(lambda x: x.lstrip(" .123456789"))
    
    #-------------------------------------------#
    #Merge some variables across the four tables#
    #-------------------------------------------#

    #Merge into df_case_drugs
    df_case_drugs = pd.merge(df_case_drugs,pcc[['CaseNumber','source']],on='CaseNumber', how='left')
    df_case_drugs = pd.merge(df_case_drugs,pcc[['CaseNumber','Year']],on='CaseNumber', how='left')
    df_case_drugs = pd.merge(df_case_drugs,pcc[['CaseNumber','OutCome']],on='CaseNumber', how='left')
    df_case_drugs = pd.merge(df_case_drugs,pcc[['CaseNumber','AgeGroup']],on='CaseNumber', how='left')
    df_case_drugs = pd.merge(df_case_drugs,pcc[['CaseNumber','Reason']],on='CaseNumber', how='left')
    df_case_drugs = pd.merge(df_case_drugs,df_case_chars[['CaseNumber','PatientFlow']],on='CaseNumber', how='left') # i don't know what some are from pcc and some are from case_drugs because they should be the same
    df_case_drugs = pd.merge(df_case_drugs,df_case_chars[['CaseNumber','CallerRelation']],on='CaseNumber', how='left')
    df_case_drugs = pd.merge(df_case_drugs,df_drug_or_combination[['CaseNumber','Case_drug_or_combination']],on='CaseNumber', how='left')
    
    #Merge into df_case_chars
    df_case_chars = pd.merge(df_case_chars,df_drug_or_combination[['CaseNumber','Case_drug_or_combination']],on='CaseNumber', how='left')
    
    #Merge into df_case_symptoms
    #df_case_symptoms['CaseNumber']=df_case_symptoms['CaseNumber'].apply(int) # Deprecated - CaseNumber is converted to int before to allow for merge to take place
    df_case_symptoms = pd.merge(df_case_symptoms,pcc[['CaseNumber','source']],on='CaseNumber', how='left')
    df_case_symptoms = pd.merge(df_case_symptoms,pcc[['CaseNumber','Year']],on='CaseNumber', how='left')
    df_case_symptoms = pd.merge(df_case_symptoms,pcc[['CaseNumber','CallerRelation']],on='CaseNumber', how='left')
    df_case_symptoms = pd.merge(df_case_symptoms,df_drug_or_combination[['CaseNumber','Case_drug_or_combination']],on='CaseNumber', how='left')
    
    #Merge into df_case_treatment
    df_case_treatment = pd.merge(df_case_treatment,pcc[['CaseNumber','source']],on='CaseNumber', how='left')
    df_case_treatment = pd.merge(df_case_treatment,pcc[['CaseNumber','Year']],on='CaseNumber', how='left')
    df_case_treatment = pd.merge(df_case_treatment,pcc[['CaseNumber','CallerRelation']],on='CaseNumber', how='left')
    df_case_treatment = pd.merge(df_case_treatment,df_drug_or_combination[['CaseNumber','Case_drug_or_combination']],on='CaseNumber', how='left')
    
    #----------#
    #Save files#
    #----------#

    df_case_chars.to_csv(r'd_output_{}/Case Characteristics.csv'.format(main_drug),index=False)
    df_case_drugs.to_csv(r'd_output_{}/Case Drugs.csv'.format(main_drug),index=False)
    df_case_symptoms.to_csv(r'd_output_{}/Case Symptoms.csv'.format(main_drug),index=False)
    df_case_treatment.to_csv(r'd_output_{}/Case Treatment.csv'.format(main_drug),index=False)

def classify_drug(AAPC, df_aapc):
    #look in df_aapc['AAPC']
    AAPC = AAPC.lstrip("0")
    try:
        return df_aapc.loc[df_aapc['AAPC'] == AAPC, 'Classification'].iloc[0]
    except:
        return "Other"

def aapc_to_name(AAPC, df_aapc):
    #look in df_aapc['AAPC']
    AAPC = AAPC.lstrip("0")
    try:
        return df_aapc.loc[df_aapc['AAPC'] == AAPC, 'Name'].iloc[0]
    except:
        return "Other"

        
def check_drug_or_combination(df_one_case_drugs,main_drug):
    #The case is assumed to be main_drug only unless any other text appears
    if all(x == main_drug for x in df_one_case_drugs['drug_classification'].unique()):
        case_classification = "Main_drug_only"
    else:
        case_classification = "Combination"
    return case_classification

    
def split_chain_text(chain_text):
#receive chain text in format "1.aaa 2.bbb 3.ccc", and return list: ["aaa", "bbb", "ccc"]
    split_list = []
    reg_pattern = r"([0]*(?:[2-9]+|[1-9][0-9][0-9]*)[.][A-z ,.-/]+)[0-9]??" # matches the next item found after the frirst(i.e. '1.abc [2. def] 3.ghi')
    working_chain = chain_text
    while True:
        try:
            second_item = re.search(reg_pattern,working_chain).groups(1)[0]
            split_list.append(second_item)
            working_chain = working_chain.replace(second_item,"")
        except:
            if working_chain != chain_text:
                split_list.append(working_chain)
            break
    
    #remove any spaces, numbers, or periods at the start of each string
    split_list = [x.lstrip(" .123456789") for x in split_list]
    return split_list
    
if __name__ == "__main__":
    main_drug = "Cannabis" # Cannabis or Opioid
    main(main_drug)