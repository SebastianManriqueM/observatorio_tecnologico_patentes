from patents import Patents
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
import nltk



def organize_for_dataframe(raw_data): #melhor indicar informação de cada coluna para o data frame
    l_raw_data = [ ]
    for i_patent in raw_data:
        d_raw_data = {}
        for i_outt_key, i_outt_value in i_patent.items():
            if isinstance( i_patent[i_outt_key], list ) and i_outt_key != "cpcs":
                for i_l_element in i_patent[i_outt_key]:
                    d_raw_data.update(i_l_element)
                continue
            elif i_outt_key == "patent_num_cited_by_us_patents":
                d_raw_data[i_outt_key] = float(i_outt_value)
                continue
            d_raw_data[i_outt_key] = i_outt_value
        l_raw_data.append(d_raw_data)

    return l_raw_data

def n_citation_stats(df_patents):
    d_citations = {"max": [],"min": [], "mean": [], "median": []}
    d_citations["max"]    = df_patents["patent_num_cited_by_us_patents"].max()
    d_citations["min"]    = df_patents["patent_num_cited_by_us_patents"].min()
    d_citations["mean"]   = df_patents["patent_num_cited_by_us_patents"].mean(axis=0)
    d_citations["median"] = df_patents["patent_num_cited_by_us_patents"].median()
    return d_citations

def create_d_plot( ser_top_n ):
    d_plot = {}
    for key in ser_top_n.keys():
        d_plot[ key ] = []
    d_plot ['ROW'] = []
    return d_plot

def get_df_n_cits_per_param_yrs_grouped( df, string_param = 'assignee_country', n_top_par = 5, yr_start = 1980, yr_spam = 10 ):
    d_n_cits_per_param = {}
    for key in pd.unique( df[ string_param ] ) :
        d_n_cits_per_param[ key ] = df[ df[string_param] == key ]['patent_num_cited_by_us_patents'].sum()
    df_n_cits_per_param = pd.Series( d_n_cits_per_param )
    ser_top_n = df_n_cits_per_param.nlargest( n_top_par )
    
    d_plot = create_d_plot( ser_top_n )

    i_year = yr_start
    idx = []
    while 1:
        df_filtered = df.loc[  ( df['app_date'] >= f'{i_year}-01-01' ) & ( df['app_date'] < f'{i_year + yr_spam}-01-01' ) ]
        acum = 0
        for key in ser_top_n.keys():
            value_tmp = df_filtered[ df_filtered[string_param] == key ]['patent_num_cited_by_us_patents'].sum()
            d_plot[ key ].append( value_tmp )
            acum = acum + value_tmp

        d_plot ['ROW'].append( df_filtered['patent_num_cited_by_us_patents'].sum() - acum )
        idx.append( f'{i_year}'[2:] + '-' + f'{i_year+yr_spam}'[2:] )
        if datetime.strptime(f'{i_year + yr_spam}-01-01', '%Y-%m-%d') > max( df['app_date'] ):
            break
        i_year = i_year + yr_spam
        
    df_plot = pd.DataFrame( d_plot, index = idx )
    
    return  df_plot



def get_df_n_patents_per_param_yrs_grouped( df, string_param = 'assignee_country', n_top_par = 5, yr_start = 1980, yr_spam = 10 ):   

    ser       = df[ string_param ].value_counts()
    ser_top_n = df[ string_param ].value_counts()[:n_top_par]

    d_plot = create_d_plot( ser_top_n ) #FAZER DIRETO COM PANDAS

    i_year = yr_start
    idx = []
    while 1:
        df_filtered = df.loc[  ( df['app_date'] >= f'{i_year}-01-01' ) & ( df['app_date'] < f'{i_year + yr_spam}-01-01' ) ]
        for key in ser_top_n.keys(): 
            d_plot[ key ].append( df_filtered[ string_param ].isin( [key] ).sum() ) #Ver como fazer em uma linha

        temp = ~df_filtered[ string_param ].isin( ser_top_n.keys() )
        d_plot ['ROW'].append( temp.sum() )
        idx.append( f'{i_year}'[2:] + '-' + f'{i_year+yr_spam}'[2:] )
        if datetime.strptime(f'{i_year + yr_spam}-01-01', '%Y-%m-%d') > max( df['app_date'] ):
            break
        i_year = i_year + yr_spam
        
    df_plot = pd.DataFrame( d_plot, index = idx )
    return df_plot

def bar_plot_per_param( df, str_per, string_param , new_dir, root_dir = 'C:/Users/sebastiand/Documents/0_UTFPR/EXTENSÃO/Res_api_pview' , show_flag = 1 ):
    try:
        os.mkdir( root_dir + "/" + new_dir  )
    except OSError as error: 
        print(error)

    if str_per == 'n_patents':
        str_ylabel = 'Patents Quantity'
    else:
        str_ylabel = 'Times Patents were cited'

    ax = df.plot.bar()
    ax.set_xlabel( "Group of Years" )
    ax.set_ylabel( str_ylabel )
    plt.grid(axis='y', color='#CCCCCC', linestyle=':')

    

    str_tmp = str_per + '_per_' + string_param
    plt.savefig( root_dir + "/" + new_dir + '/' + str_tmp + ".png" )
    plt.savefig( root_dir + "/" + new_dir + '/' + str_tmp + ".pdf" )
    if show_flag:
        plt.show()
    

def get_cits_per_param(df_unfilt, years, param='country'):  #APAGAR
    if param == 'country':
        string_param = "assignee_country" 
    elif param == 'company':
        string_param = "assignee_organization" 

    df = df_unfilt.loc[  ( df_unfilt['app_date'] >= f'{years[0]}-01-01' ) & ( df_unfilt['app_date'] < f'{years[1]}-01-01' ) ]

    n_count_series = df[string_param].value_counts()
    #print("PATENTS PER ", param, "\n", n_count_series)
    d_idx_param = {}
    d_n_cits_per_param = {}
    d_cit_stats_per_param = {}
    for param in pd.unique( df[string_param] ) :
        d_idx_param[param]           = df.index[ df[string_param] == param ].tolist()
        d_n_cits_per_param[param]    = df[ df['assignee_country'] == param ]['patent_num_cited_by_us_patents'].sum()
        d_cit_stats_per_param[param] = df[ df['assignee_country'] == param ]['patent_num_cited_by_us_patents'].describe()
        #d_n_cits_per_param[param]    = df.iloc[ d_idx_param[param] ]['patent_num_cited_by_us_patents'].sum()
        #d_cit_stats_per_param[param] = df.iloc[ d_idx_param[param] ]['patent_num_cited_by_us_patents'].describe()
        #print(param, ": ", len(d_idx_param[param]), "-", d_n_cits_per_param[param] )

    d_cits_param = {'n_patents': n_count_series, 'index': d_idx_param, 'n_cits':  pd.Series( d_n_cits_per_param ), 'cit_stats': d_cit_stats_per_param }
    #d_cits_param = { 'index': d_idx_param, 'n_cits': pd.Series(d_n_cits_per_param), 'cit_stats': d_cit_stats_per_param }
   
    return d_cits_param

#-----------------------------------------------*****-----------------------------------------------


d_user_dates = {"ini": { "year": '1980', #usar formato de data
                "month" : '01', 
                "day"   : '01' },
        "fin": { "year": '2022', 
                "month": '01', 
                "day"  : '01' },
        }
d_l_pb_patents_code = {
    "Automotive":                      [ "H01M2/1072" ],#not H01M6/,  H01M4/06
    "Cell_development":                [ "H01M10/06", "H01M4/14", "H01M4/56", "H01M4/627", "H01M4/68", "H01M4/73"  ],
    "Cell_manufacturing":              [ "H01M10/38", "H01M10/28", "H01M10/12", "H01M10/058", "H01M10/04" ],
    "Condition_monitoring_elect_var":  [ "G01R31/379" ],#G01R31/36
    "Electrodes_manufacturing":        [ "H01M4/04", "H01M4/139", "H01M4/16", "H01M4/26" ],
    "Electrolyte":                     [ "H01M2/36" ],#*
    "Machines_for_cell_assembly":      [ "H01M10/0404" ],
    "Recycling" :                      [ "H01M10/54", "H01M6/52" ],#"Y02W30/84"
    "State_of_charge":                 [ "G01R31/3842", "G01R31/387" ],
    "Thermal_management":              [ "H01M10/60" ]
}

#user_ipc_code = ["H", "1", "M", "10"]
user_back_data_filt = [ "patent_title","app_date", "patent_date",
                        "cpc_group_id", "cpc_group_title", "cpc_subgroup_id", "cpc_subgroup_title", 
                        "assignee_organization", "assignee_country", 
                        "patent_abstract", "patent_num_cited_by_us_patents" ]
curr_page = 1

for key in d_l_pb_patents_code.keys():
    patent_obj = Patents()
    #patent_obj.write_user_request_filters(d_user_dates, user_ipc_code, "ipc")
    patent_obj.write_user_request_filters(d_user_dates, d_l_pb_patents_code[key])
    patent_obj.write_user_back_data(user_back_data_filt)
    data = patent_obj.get_with_filters()


    if patent_obj.raw_data[0]['count'] > 0:
        l_data = []
        count = 0
        
        for i_l_element in patent_obj.raw_data:
            l_data.extend( organize_for_dataframe(patent_obj.raw_data[count]['patents']) )
            count += 1

        df_patents = pd.DataFrame(data=l_data)
        
        df_patents['app_date'] = pd.to_datetime( df_patents['app_date'], format='%Y-%m-%d' )
        df_patents['patent_date'] = pd.to_datetime( df_patents['patent_date'], format='%Y-%m-%d' )
        #df_patents = df_patents.sort_values( by='app_date' )
        print(list(df_patents.columns))
        
        rt_dir = 'C:/Users/sebastiand/Documents/0_UTFPR/EXTENSÃO/Res_api_pview'
        n_dir  = key

        df_plot_n_patents_company = get_df_n_patents_per_param_yrs_grouped( df_patents, string_param = 'assignee_organization' , n_top_par = 5, yr_start = int( d_user_dates['ini']['year'] ) , yr_spam = 10 )
        bar_plot_per_param( df_plot_n_patents_company, str_per = 'n_patents', string_param = 'assignee_organization' , new_dir = n_dir, root_dir = rt_dir , show_flag = 0 )
        df_patents.to_csv( rt_dir + '/' + n_dir + '/out.csv' )
        
                        
        df_plot_n_patents_country = get_df_n_patents_per_param_yrs_grouped( df_patents, string_param = 'assignee_country' , n_top_par = 5, yr_start = int( d_user_dates['ini']['year'] ), yr_spam = 10 )
        bar_plot_per_param( df_plot_n_patents_country, str_per = 'n_patents' , string_param = 'assignee_country' ,new_dir = n_dir, root_dir = rt_dir , show_flag = 0 )


        df_plot_n_cits_company = get_df_n_cits_per_param_yrs_grouped( df_patents, string_param = 'assignee_organization' , n_top_par = 5, yr_start = int( d_user_dates['ini']['year'] ), yr_spam = 10 )
        bar_plot_per_param( df_plot_n_cits_company, str_per = 'n_cits' , string_param = 'assignee_organization', new_dir = n_dir, root_dir = rt_dir , show_flag = 0 )
                        
        df_plot_n_cits_country = get_df_n_cits_per_param_yrs_grouped( df_patents, string_param = 'assignee_country' , n_top_par = 5, yr_start = int( d_user_dates['ini']['year'] ), yr_spam = 10 )
        bar_plot_per_param( df_plot_n_cits_country, str_per = 'n_cits' , string_param = 'assignee_country' , new_dir = n_dir, root_dir = rt_dir , show_flag = 0 )
        

        
    
a=1


    
