import pandas as pd
import numpy as np

# Implement the NEWS Score table from numeric variables
def NEWS_DASH(patient):
    
    # initialise empty list and dictionaries
    missing_list = []
    newsdict = {}

    # replace blanks with placeholder variable 'ph'
    patient.fillna(value='ph', inplace = True)
    
    # initialise NEWS variable
    NEWS = 0.
    
    # age
    if patient.iloc[0]['age'] == 'ph':
        missing_list.append('Age') 
    else:
        pass
    
    # bp diastolic
    if patient.iloc[0]['blood_pressure_diastolic'] == 'ph':
        missing_list.append('Diastolic BP') 
    else:
        pass
    
    # Respiration rate
    if patient.iloc[0]['respiratory_rate'] == 'ph':
        NEWS += 0.
        missing_list.append('Respiratory rate')
        newsdict['respiratory_rate'] =0
    elif (patient['respiratory_rate'] <= 8.).any():
        NEWS += 3.
        newsdict['respiratory_rate'] =3
    elif (patient['respiratory_rate'] <= 11.).any():
        NEWS += 1.
        newsdict['respiratory_rate'] =1
    elif (patient['respiratory_rate'] >= 25.).any():
        NEWS += 3.
        newsdict['respiratory_rate'] =3
    elif (patient['respiratory_rate'] >= 21.).any():
        NEWS += 2.
        newsdict['respiratory_rate'] =2
    else: 
        newsdict['respiratory_rate'] =0


    # Oxygen saturation
    if patient.iloc[0]['saturation_o2'] == 'ph':
        NEWS += 0.
        missing_list.append('Oxygen saturation')
        newsdict['saturation_o2'] =0
    elif (patient['saturation_o2'] <= 91.).any():
        NEWS += 3.
        newsdict['saturation_o2'] =3
    elif (patient['saturation_o2'] <= 93.).any():
        NEWS += 2.
        newsdict['saturation_o2'] =2
    elif (patient['saturation_o2'] <= 95.).any():
        NEWS += 1.
        newsdict['saturation_o2'] =1
    else: 
        newsdict['saturation_o2'] =0

    # Supplemental Oxygen
    if patient.iloc[0]['supp_o2'] == 'ph':
        NEWS += 0.
        missing_list.append('Supplemental oxygen')
        newsdict['supp_o2'] =0
    elif (patient['supp_o2'] == 1).any():
        NEWS += 2.
        newsdict['supp_o2'] =2
    else: 
        newsdict['supp_o2'] =0
        
    # Temperature
    if patient.iloc[0]['temperature'] == 'ph':
        NEWS += 0.
        missing_list.append('Temperature')
        newsdict['temperature'] =0
    elif (patient['temperature'] <= 35.0).any():
        NEWS += 3.
        newsdict['temperature'] =3
    elif (patient['temperature'] <= 36.0).any():
        NEWS += 1.
        newsdict['temperature'] =1
    elif (patient['temperature'] >= 39.1).any():
        NEWS += 2.
        newsdict['temperature'] =2
    elif (patient['temperature'] >= 38.1).any():
        NEWS += 1.
        newsdict['temperature'] =1
    else: 
        newsdict['temperature'] =0

    # Systolic Blood Pressure
    if patient.iloc[0]['blood_pressure_systolic'] == 'ph':
        NEWS += 0.
        missing_list.append('Systolic BP')
        newsdict['blood_pressure_systolic'] =0
    elif (patient['blood_pressure_systolic'] <= 90.0).any():
        NEWS += 3.
        newsdict['blood_pressure_systolic'] =3
    elif (patient['blood_pressure_systolic'] <= 100.0).any():
        NEWS += 2.
        newsdict['blood_pressure_systolic'] =2
    elif (patient['blood_pressure_systolic'] <= 110.0).any():
        NEWS += 1.
        newsdict['blood_pressure_systolic'] =1
    elif (patient['blood_pressure_systolic'] >= 220.0).any():
        NEWS += 3.
        newsdict['blood_pressure_systolic'] =3
    else: 
        newsdict['blood_pressure_systolic'] =0

    # Heart Rate
    if patient.iloc[0]['heart_rate'] == 'ph':
        NEWS += 0.
        missing_list.append('Heart rate')
        newsdict['heart_rate'] =0
    elif (patient['heart_rate'] <= 40.0).any():
        NEWS += 3.
        newsdict['heart_rate'] =3
    elif (patient['heart_rate'] <= 50.0).any():
        NEWS += 1.
        newsdict['heart_rate'] =1
    elif (patient['heart_rate'] >= 131.0).any():
        NEWS += 3.
        newsdict['heart_rate'] =3
    elif (patient['heart_rate'] >= 111.0).any():
        NEWS += 2.
        newsdict['heart_rate'] =2
    elif (patient['heart_rate'] >= 91.0).any():
        NEWS += 1.
        newsdict['heart_rate'] =1
    else: 
        newsdict['heart_rate'] =0

    # Consciousness (using Glasgow Consc Score <= 12 as proxy)
    if patient.iloc[0]['gcs'] == 'ph':
        NEWS += 0.
        missing_list.append('GCS')
        newsdict['gcs'] =0
    elif (patient['gcs'] <= 12.0).any():
        NEWS += 3.
        newsdict['gcs'] =3
    else: 
        newsdict['gcs'] =0
        
        
    # create a dataframe of items for the NEWS graph 
    newsdf = pd.DataFrame(list(newsdict.items()))
    newsdf.columns = ['news', 'vals']
    newsa = patient.transpose().reset_index()
    newsa.columns = ['news', 'vals2']
    result = pd.merge(newsdf, newsa, on='news')
    
    
    keys = ['gcs', 'heart_rate', 'temperature', 'supp_o2', 'blood_pressure_systolic', 'saturation_o2', 'respiratory_rate']
    values = ['GCS', 'Heart rate', 'Temperature', 'Supplemental oxygen', 'Systolic blood pressure', 'Oxygen saturation', 'Respiratory rate' ]
    reasons = dict(zip(keys, values))
    
    newsdf1 = result[result['vals'] > 0].copy()
    newsdf1['vals2'] = np.where(newsdf1['news'] == 'supp_o2', 'yes', newsdf1['vals2'])
    newsdf1.loc[:,'final'] = newsdf1['news'].map(reasons)
    
    # create a dataframe of items for the missing variables graph
    missingdf = pd.DataFrame(missing_list, columns = ['Missing data'])
        
    missingdf['vals'] = 1
    missingdf['marker'] = 'mark'
    
    while (missingdf.shape[0] > 0) & (missingdf.shape[0] < 10):
        missingdf = missingdf.append({'Missing data': 'Missing','vals' : 2.5, 'marker': 'no'},  "ignore_index=True")
    
    if missingdf.shape[0] == 0:
        missingdf = pd.DataFrame()
        missingdf = missingdf.append({'Missing data': 'None','vals' : 2.5, 'marker': 'no'},  "ignore_index=True")


        
    
    # return NEWS score, missing list, news dataframe and missing dataframe
    
    
    
    return str(round(NEWS)), missing_list, newsdf1, missingdf
    
        
    