import pandas as pd
import numpy as np
import re
from collections import OrderedDict



def modelcleaning1(df):
    # data cleaning code

    
    df['admitted_status'] = np.where((df['recorded_outcome'].str.contains('Admit|To Theatres|EPAU|Labour ward|Maxillary facial', na=False, case=False)), 'Admitted', 'Non-Admitted')


    df.admitted_status = (df.admitted_status != 'Non-Admitted').astype(np.int)
    
    
    
    df['gender'] = np.where((df['gender']== 'Male'), 1, 0)
    
    # clean up triage notes
    # stop it reading nan as a number

    df['triage_notes'].fillna("", inplace = True)

    # clean up triage notes

    # lower case
    df['triage_parsed'] = df['triage_notes'].str.lower()


    # remove punctuation

    punctuation_signs = list("?:!.,;")

    for punct_sign in punctuation_signs:
        df['triage_parsed'] = df['triage_parsed'].str.replace(punct_sign, '')

    
    # remove possessive pronouns
    df['triage_parsed'] = df['triage_parsed'].str.replace("'s", "")


    # Arrival mode - src: Grouping_categorical_vars.R
 
    arrival_reencoding = ('arrival_mode',
                          OrderedDict([(r'Blue Call|Trauma|Stroke|Helicopter|HEMS', 'Blue_Call'),
                                       ('Ambulance', 'Ambulance'),
                                       ('.*', 'Common_Transport')]))



    # Referral Sources
    
    refsource_reencoding = ('referral_source', OrderedDict([('MIU', 'MIU'),
                            (r'Carer|Educational Est.|Child unwell|Parent|Police|Prison|Work|Self Referred|Adult unwell', 'Guardians'),
                            (r'Health Carer|Social Services', 'Social_Services'),
                            (r'Access Clinic|GP|Referred by PCC', 'GPs_Others'),
                            (r'NHS Direct', 'NHS_Direct'),
                            (r'Other Hospital|Nursing Home|A&E Clinician KGH|Emergency Services', 'Other_Hospital'),
                            (r'Other', 'Other')]))


    def reencode_cat(df, cn, od):
        df[cn+'_raw'] = df[cn]
        df[cn] = np.nan
        for k, v in od.items():
            df.loc[df[cn+'_raw'].str.contains(k, case=False) & df.loc[:, cn].isnull(), cn] = v
      
        return df

    reencoding_arr = [arrival_reencoding]
    reencoding_ref = [refsource_reencoding ]

    
    if df.arrival_mode is not None:
        
        for r in reencoding_arr:

            df = reencode_cat(df, *r)
            
    
    if df.referral_source is not None:
        
        for r in reencoding_ref:

            df = reencode_cat(df, *r)
        
 
    ## TEMPERATURE

    # temp RegEx variables

    # Number extractor
    R = re.compile('\D*(\d+\.\d+|\d+).*')

    # Correct numbers with poor decimalisation
    R_num = r'(\d+)([,./]{1,2})(\d*)'


    def repl(x): 
        return x.groups()[-1]

    def repl_num(x):
        return x.group(1)+'.'+x.group(3)

    # Regex indices that can't be coerced to numeric
    df.temperature = df.temperature.astype(str).apply(lambda x: re.sub(R_num, repl_num, x))  # Correct poor decimalisation

    not_num = pd.to_numeric(df.temperature, errors='coerce').isnull() & df.temperature.notnull()
    df.loc[not_num, 'temperature'] = df.loc[not_num, 'temperature'].astype(str).apply(lambda x: re.sub(R, repl, x))


    ## SUPP_O2
    # set up RegEx

    Rair = re.compile('(air|oa|o/a|ao|RA)', re.I)
    Ro2 = re.compile('(neb|liter|litre|lpm|entonox|o2|oxy|\d+\.*\d*\s*l|\s02|concentrator)', re.I)



    def suppl_o2(x):
        if x == 'nan':  # Missing
            return np.nan
        o2 = re.search(Ro2, x)
        if o2 is None:
            return 0  # AIR
        else:  # O2 matches
      #      
            return 1  # O2
     #       air_start = air.start()

       
    df['supp_o2'] = df.saturation_o2.astype(str).apply(lambda x: suppl_o2(x))

    # If no match and no SaO2 could be extracted then it is unreliable
    df.loc[(df.supp_o2 == 0) & df.saturation_o2.isnull(), 'supp_o2'] = np.nan
    # NOTE: If there is an RO2 match but no SaO2 number then it is deemed reliable




    ## SATURATION_O2

    """
        First Group (To be ignored):
        * A digit followed by L - E.g. "`2L`/min"
        * 02 surrounded by non-digit characters - E.g. "`Sa02 `50%"
        * BOL followed by non-digit characters - E.g. "`Sats `50%"

        Second Group:
        * 100
        * One or two digits, decimal point, 1 or more digits
        * One or two digits

        Third Group:
        * Matches if `l` doesn't match next

        First group ignores non-numeric quantities, quantity of oxygen given (suffixed by l), and 02.
        Second Group extracts number.
        Third Group ensures second group doesn't precede an l - Needed for e.g. "2L/min"
    """

    R_sa02 = re.compile('(\d*l|\D*02\D*|^\D*)*\D*(100|\d{1,2}\.{1}\d+|\d{1,2})(?!l).*', re.I)

    sym = ['!', '"', '£', '$', '^', '&', '*', '(', ')', '5']
    num = '123467890%'
    o2_typo = {k: v for k, v in zip(sym, num)}
    

    # Find !"£$^&*() whih should be 123467890
    R_typo = re.compile('!|"|£|\$|\^|&|\*|\(|\)')

    # Find 2 digit number followed by a 5 (which should likely be "%")
    R_perc = re.compile('(\D|^)(\d{2})(5)')



    def repl_sao2(x):
        if x.lastindex is None:
            # If R_typo?
            return o2_typo[x.group()]
        else:
            # If R_perc?
            left = ''.join(x.groups()[:-1])
            return left+o2_typo[x.groups()[-1]]

    def parse_sao2(x):
        return re.sub(R_sa02, repl_sao2, re.sub(R_perc, repl_sao2, re.sub(R_typo, repl_sao2, x)))


    # remove spaces between numbers
    df.loc[:, 'saturation_o2'] = df.loc[:, 'saturation_o2'].astype(str).apply(lambda x: re.sub (r'(\d)\s+(\d)', r'\1\2', x))

    # Regex indices that can't be coerced to numeric
    df.saturation_o2 = df.saturation_o2.astype(str).apply(lambda x: re.sub(R_num, repl_num, x))  # Correct poor decimalisation
    not_num = pd.to_numeric(df.saturation_o2, errors='coerce').isnull() & df.saturation_o2.notnull()
    df.loc[not_num, 'saturation_o2'] = df.loc[not_num, 'saturation_o2'].astype(str).apply(lambda x: re.sub(R, repl, x))
    #news.saturation_o2 = news.saturation_o2.astype(str).apply(parse_sao2)

    # Numeric columns to be parsed and converted to numeric
    cols = ['blood_pressure_diastolic', 'blood_pressure_systolic', 'gcs',
            'heart_rate', 'age', 'saturation_o2', 'temperature',
            'admitted_status', 'respiratory_rate', 'pain_score']


    dfs = df.loc[:, cols]

    for c in cols:
        dfs.loc[:, c] = pd.to_numeric(dfs.loc[:, c], errors='coerce')

    # Physiological reasonable upper and lower bounds:
    LU_Age = ('age', 0, 110)
    LU_SBP = ('blood_pressure_systolic', 50, 250)
    LU_DBP = ('blood_pressure_diastolic', 30, 220)
    LU_HR = ('heart_rate', 25, 350)
    LU_GCS = ('gcs', 0,15)
    LU_BR = ('respiratory_rate', 4, 60)
    LU_SpO2 = ('saturation_o2', 60, 100)
    LU_Temp = ('temperature', 34, 42)
    LU_Pain = ('pain_score', 0, 10)

    def process_generic(x, lb, ub):
        """ Take absolute value of inputs. Set `x` to NaN if $x \notin [lb, ub)"""
        x = x.abs()
        if x.dtype == 'float64':
            #print('float')
            x.loc[x.apply(lambda x: not x.is_integer())] = np.nan
        x.loc[(x <= lb ) | (x > ub)] = np.nan

        return x

    LU_generics = (LU_Age, LU_SBP, LU_DBP, LU_HR, LU_BR)

    for LU in LU_generics:
        dfs.loc[:, LU[0]] = process_generic(dfs.loc[:, LU[0]], LU[1], LU[2])
        #print('Processed {}'.format(LU[0]))

    def process_O2(x, lb, ub):
        """
        Take absolute value of inputs.
        If $x \in (0, 1]$ scale `x` from decimal to percentage.
        Set `x` to NaN if $x \notin [lb, ub)$
        """
        x = x.abs()
        x.loc[(x <= 1) & (x > 0)] = x.loc[(x <= 1) & (x > 0)] * 100
        x.loc[(x <= 10) & (x > 1)] = x.loc[(x <= 10) & (x > 1)] * 10
        x.loc[(x <= lb ) | (x > ub)] = np.nan
        return x

    dfs.loc[:, 'saturation_o2'] = process_O2(dfs.saturation_o2, LU_SpO2[1], LU_SpO2[2])
    #print('Processed O2')

    def process_gcs(x, lb, ub):
        'take absolute value of inputs'
        x = x.abs()
        x.loc[(x <= lb ) | (x > ub)] = np.nan

        return x

    dfs.loc[:, 'gcs'] = process_gcs(dfs.gcs, LU_GCS[1], LU_GCS[2])


    def process_Temp(x, lb, ub):
        """ Take absolute value of inputs.
        Scale `x` down by powers of 10 until $x \in [0, 100)]$.
        Set `x` to NaN if $x \notin [lb, ub)$"""
        x = x.abs()

        def scale_down_log10(x):
            return x/10**(np.floor(np.log10(x))-1)

        x = scale_down_log10(x)
        x.loc[(x <= lb ) | (x > ub)] = np.nan

        return x
    dfs.loc[:, 'temperature'] = process_Temp(dfs.temperature, LU_Temp[1], LU_Temp[2])


    def process_pain(x, lb, ub):
        """ Take absolute value of inputs.
        Pain Scores over 10 are actually more like 8.
        Set `x` to NaN if $x \notin [lb, ub)$"""
        x = x.abs()
        x.loc[(x > ub)] = 8
        x.loc[(x < lb) | (x > ub)] = np.nan
        return x

    dfs.loc[:, 'pain_score'] = process_pain(dfs.loc[:, 'pain_score'], LU_Pain[1], LU_Pain[2])


    df.loc[:, cols] = dfs



    df = df.sort_values("arrival_dttm")



    df.drop_duplicates(subset=["pas_id"], keep='last', inplace=True)

 

    df = df.replace({pd.np.nan: None})
    
    return df
