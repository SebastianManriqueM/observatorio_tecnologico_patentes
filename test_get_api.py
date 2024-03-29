from patents import Patents
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
#import nltk
#teste comentário 2 - Endereço GitHub:https://github.com/SebastianManriqueM/observatorio_tecnologico_patentes.git


def get_grouped_counts( df, selected_grouping='assignee_country', item_to_count='n_patent', n_top=5, Y_span = 10 ):
    if selected_grouping == 'assignee_country':
        other_items_legend = 'ROW'
    else:
        other_items_legend = 'ROO'

    top_n_key                  = df[ selected_grouping ].value_counts()[:n_top].keys()
    df_n_patents               = df.groupby( ['app_date', selected_grouping] )[item_to_count].sum().unstack( fill_value=0 ).resample( f'{Y_span}Y' ).sum()
    df_n_patents['Total']      = df_n_patents.sum(axis=1)
    df_filt                    = df_n_patents[ top_n_key ]
    df_filt[other_items_legend]= df_n_patents['Total'] - df_filt.sum(axis=1)
    new_col_index = []
    
    for i in range(len(df_filt.index)-1):
        new_col_index.append( df_filt.index[i].strftime("%Y")[2:] +"-"+ df_filt.index[i+1].strftime("%Y")[2:] )
    
    new_col_index.append( df_filt.index[i+1].strftime("%Y")[2:] +"-"+ str(int(df_filt.index[i+1].strftime("%Y")[2:])+Y_span) )
    df_filt.insert(0, "Yspan", new_col_index, True)
    
    return df_filt.set_index("Yspan")


def bar_plot_per_param( df, count_by, group_by , new_dir, root_dir = 'C:/Users/sebastiand/Documents/0_UTFPR/EXTENSÃO/Res_api_pview' , show_flag = 1 ):
    try:
        os.mkdir( root_dir + "/" + new_dir  )
    except OSError as error: 
        print(error)

    if count_by == 'n_patent':
        str_ylabel = 'Patents Quantity'
    else:
        str_ylabel = 'Times Patents were cited'

    ax = df.plot.bar()
    ax.set_xlabel( "Group of Years" )
    ax.set_ylabel( str_ylabel )
    plt.grid(axis='y', color='#CCCCCC', linestyle=':')

    str_tmp = count_by + '_per_' + group_by
    plt.savefig( root_dir + "/" + new_dir + '/' + str_tmp + ".png" )
    plt.savefig( root_dir + "/" + new_dir + '/' + str_tmp + ".pdf" )
    if show_flag:
        plt.show()
    
def make_all_barplots(df_patents , key , n_top , yr_span , rt_dir ):
    n_dir  = key        
    counts_type = [ 'n_patent', 'patent_num_cited_by_us_patents' ]
    grouping_type = [ 'assignee_country', 'assignee_organization' ]
    for count_type in counts_type:
        for group_type in grouping_type:
            df_plot = pd.DataFrame([])
            df_plot = get_grouped_counts( df_patents , selected_grouping=group_type , item_to_count=count_type , n_top=n_top , Y_span=yr_span )
            bar_plot_per_param( df_plot, count_by=count_type , group_by=group_type , new_dir=n_dir , root_dir=rt_dir , show_flag=0 )
            df_patents.to_csv( rt_dir + '/' + n_dir + '/out.csv' )


def iterate_all_cat( d_l_pb_patents_code, d_user_dates, user_back_data_filt , n_top , yr_span , rt_dir ):
    for key in d_l_pb_patents_code.keys():
        o_api_pview = Patents()
        o_api_pview.write_user_request_filters(d_user_dates, d_l_pb_patents_code[key])
        o_api_pview.write_user_back_data(user_back_data_filt)
        o_api_pview.get_with_filters()

        if o_api_pview.raw_data[0]['count'] > 1:
            df_patents = pd.DataFrame(data = o_api_pview.ord_data)
            df_patents['app_date']    = pd.to_datetime( df_patents['app_date']   , format='%Y-%m-%d' )
            df_patents['patent_date'] = pd.to_datetime( df_patents['patent_date'], format='%Y-%m-%d' )
            df_patents['n_patent']    = [1] * len(df_patents)
            df_patents = df_patents.sort_values(["app_date"]).reset_index( drop=True )
            
            make_all_barplots( df_patents , key , n_top , yr_span , rt_dir )
            

            

#-----------------------------------------------*****-----------------------------------------------


d_user_dates = {"ini": { "year": '1980', #usar formato de data melhor
                "month" : '01', 
                "day"   : '01' },
        "fin": { "year": '2022', 
                "month": '01', 
                "day"  : '01' },
        }
d_l_pb_patents_code = {
    "Automotive":                      [ "H01M2/1072" ],#not H01M6/,  H01M4/06
    "Bidirectional_Converters":        [ "H02M3/33584" ],
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

rt_dir = 'G:/Outros computadores/Meu computador/0_UTFPR/EXTENSÃO/Res_api_pview/Novo'
#C:/Users/sebastiand/Documents/0_UTFPR/EXTENSÃO/Res_api_pview

n_top   = 5
yr_span = 10
iterate_all_cat( d_l_pb_patents_code, d_user_dates, user_back_data_filt, n_top , yr_span , rt_dir )


