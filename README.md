PCC Data Merging and cleaning process
1 - Map Equivalent variables

 
2 – Drop all variables that are not of interest and merge databases
3 – Clean messy text fields using dictionaries
AgeGroup = {
	"13-19 yrs" : "13-19 yrs",
	">60 yrs" : ">60 yrs",
	"20-29 yrs" : "20-29 yrs",
	"50-59 yrs" : "50-59 yrs",
	"40-49 yrs" : "40-49 yrs",
	"30-39 yrs" : "30-39 yrs",
	"NA" : "NA",
	"<5 yrs" : "<5 yrs",
	"6-12 yrs" : "6-12 yrs",
	"Pt is in their 60's" : ">60 yrs",
	"Pt is 13-19 Years" : "13-19 yrs",
	"Pt is in their 20's" : "20-29 yrs",
	"Pt is in their 40's" : "40-49 yrs",
	"Pt is in their 50's" : "50-59 yrs",
	"Pt is in their 30's" : "30-39 yrs",
	"Unknown Adult 20 Years or More" : ">20 yrs",
	"Pt is 5 Years or Less" : "<5 yrs",
	"Pt is in their 70's" : ">60 yrs",
	"Pt is 90 Years or More" : ">60 yrs",
	"Pt is in their 80's" : ">60 yrs",
	"Pt is 6-12 Years" : "6-12 yrs",
	"Unknown Age" : "Unknown",
	"Unknown age" : "Unknown",
	"10--15" : "10-15 yrs",
	"0--2" : "<5 yrs",
	"20--29" : "20-29 yrs",
	"Unknown" : "Unknown",
	"6--9" : "6-12 yrs",
	"16--19" : "13-19 yrs",
	"30--39" : "30-39 yrs",
	"40--49" : "40-59 yrs",
	"50--65" : "50-65 yrs",
	"65+ " : ">60 yrs",
	"3--5" : "<5 yrs",
	"30s" : "30-39 yrs",
	"50s" : "50-59 yrs",
	"20s" : "20-29 yrs",
	"70s" : ">60 yrs",
	"60s" : ">60 yrs",
	"13-19 years" : "13-19 yrs",
	"Unknown adult (>=20 yrs)" : ">20 yrs",
	"40s" : "40-49 yrs",
	"80s" : ">60 yrs",
	"0-5 yrs" : "<5 yrs",
	">=90" : ">60 yrs",
	"60-69 yrs":">60 yrs",
	"70-79 yrs":">60 yrs",
	"6-12 years" : "6-12 yrs"
	}
4 – Add variable for opioid/cannabis only or combination
Look at set of drugs belonging to each CaseNumber and determine if there are only opioids, or opioids and other drugs.
5 – Split database into four tables
Table 1 - PCC Database sample
CaseNumber	AgeGroup	SEX	AAPC	Substance	Form	Treatment	Symptoms	Route
90614706	40-49 yrs	Male	37705	OXYCONTIN 	SOLID	Antibiotics	Chest X-Ray (+) Findings	Ingestion
90614706	40-49 yrs	Male	37705	OXYCONTIN 	SOLID	Antibiotics	Confusion 	Ingestion
90614706	40-49 yrs	Male	37705	OXYCONTIN 	SOLID	Antibiotics	Drowsy/lethargy 	Ingestion
90614706	40-49 yrs	Male	37705	OXYCONTIN 	SOLID	Antibiotics	Hypertension 	Ingestion
90614706	40-49 yrs	Male	37705	OXYCONTIN 	SOLID	Antibiotics	Tachycardia 	Ingestion
90614706	40-49 yrs	Male	37705	OXYCONTIN 	SOLID	IV Fluids	Chest X-Ray (+) Findings	Ingestion
90614706	40-49 yrs	Male	37705	OXYCONTIN 	SOLID	IV Fluids	Confusion 	Ingestion
90614706	40-49 yrs	Male	37705	OXYCONTIN 	SOLID	IV Fluids	Drowsy/lethargy 	Ingestion
90614706	40-49 yrs	Male	37705	OXYCONTIN 	SOLID	IV Fluids	Hypertension 	Ingestion
90614706	40-49 yrs	Male	37705	OXYCONTIN 	SOLID	IV Fluids	Tachycardia 	Ingestion
90614706	40-49 yrs	Male	83000	MARIJUANA	OTHER	Antibiotics	Chest X-Ray (+) Findings	Ingestion
90614706	40-49 yrs	Male	83000	MARIJUANA	OTHER	Antibiotics	Confusion 	Ingestion
90614706	40-49 yrs	Male	83000	MARIJUANA	OTHER	Antibiotics	Drowsy/lethargy 	Ingestion
90614706	40-49 yrs	Male	83000	MARIJUANA	OTHER	Antibiotics	Hypertension 	Ingestion

The above table is a sample of the data we have been provided with. If we query this data, we would get 10 instances of Oxycontin, and 4 of marijuana. In reality, there’s only one of each. The data contains duplicates to show the various drugs, treatments, and symptoms that were used. To fix the data, it was split into four tables. One with caller characteristics, where each row is one call; one with drug information, where each row is one drug that was reported during a call; one with treatment information, where each row is one treatment; and one with symptoms, where each row is one symptom. The four tables are all linked by the CaseNumber, so analysis between them is possible.

6 – Some more cleaning on symptoms and treatment:
Treatment and symptom data from PADIS 2016 contain several values per row and need to be split:
Before:
CaseNumber	Treatment
11111	1.EKG/MONITOR  2.MEDICAL ASSESSMENT  3.OBSERVATION
99999	1.MEDICAL ASSESSMENT  2.NONE/REASSURANCE

After:
CaseNumber	Treatment
11111	EKG/MONITOR
11111	MEDICAL ASSESSMENT  
11111	OBSERVATION
99999	MEDICAL ASSESSMENT  
99999	NONE/REASSURANCE


Limitations
CAPQ
Denominator age group categories do not add up to provided totals. It’s probably due to the total including unknown age, which wouldn’t be included in any of the provided age groups.
Did not differentiate between patients already at HCF vs those that were referred.
CAPQ did not separate opioid-only cases from those where opioids were taken in addition to another non-opioid substance. Several tables in the report present data on these two categories separately, therefore CAPQ data could not be included in: Outcome, Reason for use, Exposure Site, Symptoms, and Treatment.
CAPQ did not provide the following tables: Acuity, Substance Formula, and Drug by Reason for use.
DPIC
Can’t use symptoms or treatment data from DPIC since the top 10 lists don’t match, and it doesn’t make sense to add in DPIC numbers for 8 out of 10 symptoms/treatments.
PADIS
1)	PADIS 2016 is missing AAPC codes, but they were added in based on the “Subtsance Verbatim” variable.
2)	PADIS 2016 does not include coexposure data. Only the opioid information from the calls is included.
3)	PADIS 2017 stores the symptoms, treatment, and route variables across 211 variables. This was not processed yet and those variables were left blank for this data set.
4)	Some cases an opioid listed (i.e. codeine), but no AAPC code. Currently drugs are counted by AAPC code, so these cases are not being counted.
5)	PADIS did not provide denominator information for 2016, so 2017 was copied.
Suggestions

