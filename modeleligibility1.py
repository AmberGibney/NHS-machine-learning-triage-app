import pandas as pd
import numpy as np
import pickle
import joblib
import dill
import re

from compute_NEWS import *

def featureselect1(df):

    # create broader age groups
    df['AgeB_16-40'] = np.where((df['age'] > 15) & (df['age'] <=40), 1, 0)
    df['AgeB_41-64'] = np.where((df['age'] > 40) & (df['age'] <=64), 1, 0)
    df['AgeB_65+'] = np.where((df['age'] > 65), 1, 0)




    # create arrival catgeories
    df['Arrived_Ambulance'] = np.where((df['arrival_mode'] == 'Ambulance'), 1, 0)
    df['Arrived_Blue_Call'] = np.where((df['arrival_mode'] == 'Blue_Call'), 1, 0)
    df['Arrived_Common_Transport'] = np.where((df['arrival_mode'] == 'Common_Transport'), 1, 0)

    # alt arrival mode

    df.loc[ (df['arrival_mode'] == 'Ambulance' ) | (df['arrival_mode'] == 'Blue_Call'), 'Ambulance'] = 1
    df.loc[ (df['arrival_mode'] == 'Common_Transport' ), 'Ambulance'] = 0

    # create referral categories
    
    df['Ref_GPs_Others'] = np.where((df['referral_source'] == 'GPs_Others'), 1, 0)
    df['Ref_MIU'] = np.where((df['referral_source'] == 'MIU'), 1, 0)
    df['Ref_NHS_Direct'] = np.where((df['referral_source'] == 'NHS_Direct'), 1, 0)
    df['Ref_Guardians'] = np.where((df['referral_source'] == 'Guardians'), 1, 0)
    df['Ref_Other'] = np.where((df['referral_source'] == 'Other'), 1, 0)
    df['Ref_Other_Hospital'] = np.where((df['referral_source'] == 'Other_Hospital'), 1, 0)
    df['Ref_Social_Services'] = np.where((df['referral_source'] == 'Social_Services'), 1, 0)


    # fill in hospital name
    df['hosp'] = 1

    # pick out those who have chest pain, headache or abdo pain in complaint
    df['chest_pain'] = np.where((df['triage_notes'].str.contains('no chest pain', na=False, case=False)), 1, 0)
    df['headache'] = np.where((df['triage_notes'].str.contains('headache', na=False, case=False)), 1, 0)
    df['abdo_pain'] = np.where((df['triage_notes'].str.contains('abdo', case=False, regex=True) & (df['triage_notes'].str.contains('pain', case=False, regex=True))), 1, 0)
    
    # Add NEWS Score as new column
    df = df.pipe(compute_NEWS_vec)


    # binarizing outcomes

    # setting <15 as limit for gcs (maybe try 14)

    df.gcs.fillna(0, inplace=True)

    coma = np.array(df['gcs']) 
    coma[(coma < 14.0) & (coma>0 )] = 1
    coma[(coma == 15) | (coma ==14)] = 0
    df['coma'] = coma

    # fill in 0 for supp_o2 and pain_score if unknown

    df['supp_o2'].fillna(0, inplace = True)
    df['pain_score'].fillna(0, inplace = True)

    # create fields for abnormal obs
    df.loc[:,'resp_ab'] = 0
    df.loc[:,'o2_ab'] = 0
    df.loc[:,'bp_ab'] = 0
    df.loc[:,'pulse_ab'] = 0
    df.loc[:,'temp_ab'] = 0


    df.loc[ (df['respiratory_rate'] <= 11) | (df['respiratory_rate'] >= 21), 'resp_ab'] = 1
    df.loc[ (df['heart_rate'] <= 50) | (df['heart_rate'] >= 91), 'pulse_ab'] = 1
    df.loc[ (df['temperature'] <= 36.) | (df['temperature'] >= 38.1), 'temp_ab'] = 1
    df.loc[ (df['blood_pressure_systolic'] <= 110) | (df['blood_pressure_systolic'] >= 220), 'bp_ab'] = 1
    df.loc[ df['saturation_o2'] <= 95, 'o2_ab'] = 1
    
    
    return df





def modeleligible1(df):
           
    cols2 = ['age', 'gender', 'blood_pressure_diastolic', 'blood_pressure_systolic', 'heart_rate',
            'respiratory_rate', 'saturation_o2', 'temperature']
    
    
    # if there are any missing values for the obs, we can't calculate probability
    # in this case just return any admissions
    
    if df[cols2].isnull().values.any() == True:
        return df
    
    else: 
        
        df = featureselect1(df)
        
        # change to location of pickled columns
        
        col_names = r'\colsdowngbc.pkl'
        list_unpickle = open(col_names, 'rb')

        # load the unpickle object into a variable
        cols = pickle.load(list_unpickle)
        list_unpickle.close()
        
        preddf = df[cols] 
        
     
                   
        #Dump the trained gbc classifier with Pickle
        
        # change to location of pickled classifier
        best_pkl_filename = r'\bestdowngbc.pkl'
        # load the pickled model
        best_model_pkl = open(best_pkl_filename, 'rb')
        best_model = pickle.load(best_model_pkl)
        best_model_pkl.close()
        
        
       
        
        # open pickled lime
        
        # change to location of pickled lime classifier
        explainer_filename = r'\limedowngbc.pkl'
        with open(explainer_filename, 'rb') as f: explainer = dill.load(f)



       # test = best_model.predict(preddf)
        probs = best_model.predict_proba(preddf)
        
        # forcing same random seed each time
        def explain(instance, predict_fn, **kwargs):
            np.random.seed(16)

            return explainer.explain_instance(instance, predict_fn, **kwargs)
        
        exp = explain(preddf.iloc[0,:].astype(int).values, best_model.predict_proba, num_features=5).as_list()
    
        # sending to dataframe
        lime = pd.DataFrame(exp)

        # new data frame with split value columns
        
        new = lime[0].str.split("[=]", n = 2, expand = True) 

        # making separate first name column from new data frame 
        lime["a"]= new[0] 

        # making separate last name column from new data frame 
        lime["b"]= new[1] 

        lime.drop(0, axis=1, inplace=True)

        lime = lime[["a", "b", 1]]

        lime.rename(columns={'a': 'feature', 'b': 'Value', 1: 'Rank'}, inplace=True)
        
        

        keys = ['temp_ab', 'pulse_ab', 'bp_ab', 'o2_ab','resp_ab', 'coma', 'NEWS', 'AgeB_16-40', 'AgeB_41-64', 'AgeB_65+', 
        'admittance_28d', 'admittance_365d', 'admittance_7d', 'attendance_28d', 'attendance_365d', 'attendance_7d', 'gender', 'Ref_GPs_Others', 'Ref_MIU', 
        'Ref_NHS_Direct', 'Ref_Guardians', 'Ref_Other', 'Ref_Other_Hospital', 
        'Ref_Social_Services', 'Arrived_Common_Transport', 'Arrived_Ambulance', 'Arrived_Blue_Call', 'chest_pain', 'headache', 'abdo_pain', 'pain_score', 'hosp']

        values = ['Abnormal temperature', 'Abnormal pulse', 'Abnormal diastolic bp', 'Abnormal o2 sats', 'Abnormal respirator rate', 'Abnormal gcs','Abnormal NEWS', 'Age 16-40', 'Age 41-64', 'Age 65+', 'Admittances in last 28 days','Admittances in last year', 'Admittances in last week', 'Attendances in last 28 days','Attendances in last year', 'Attendances in last week', 'Sex', 'GP/Others referral', 'MIU referral', 'NHS Direct referral', 'Non-medical referral', 'Other referral','Other hospital referral', 'Social services referral', 'Walk-in', 'Arrived by Ambulance', 'Arrived by Blue Call', 'No chest pain', 'Headache',
                 'Abdominal pain', 'Pain score', 'Hospital']

        reasons1 = dict(zip(keys, values))

        # add column mapping dict value to dataframe key

        lime['Feature'] = lime['feature'].map(reasons1)
        
        lime.loc[lime['Feature'].isnull(),'Feature'] = lime['feature']


        lime.drop(columns={'feature'}, inplace=True)

        lime = lime[["Feature", "Value", "Rank"]]
        
        


        lime['Word'] = np.where((lime['Value'] == '0'), 'No', 'Yes')

        res = probs[:, 1]
       # print ("The probability of admission is: %s" % res)

        return res, lime, preddf
                                                                        
