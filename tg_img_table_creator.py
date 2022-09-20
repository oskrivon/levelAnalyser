import pandas as pd 
import dataframe_image as dfi


def img_table_creator(df, function_flag):
    path = 'screener_results/'

    df_ = df[['quotation', 'turnover_24h', 'open_interest', 'funding_rate', 'natr']]
    df_.rename(columns = {'turnover_24h' : 'volume', 
                          'open_interest' : 'OI', 
                          'funding_rate' : 'funding rate'}, inplace = True)
    df_.reset_index(drop=True, inplace=True)
    
    df_img = df_.style.set_properties(
        **{
            'background-color': 'magenta',
            'subset':'funding rate'
        }
    )

    if function_flag == 'get_screening': 
        df_img = df_.style.set_properties(
            **{
                'background-color': 'magenta',
                'subset':'volume'
            }
        )
        name = path + 'get_screening.png'
    if function_flag == 'get_top_natr': 
        df_img = df_.style.set_properties(
            **{
                'background-color': 'magenta',
                'subset':'natr'
            }
        )
        name = path + 'get_top_natr.png'
    if function_flag == 'get_upcoming_fundings': 
        df_img = df_.style.set_properties(
            **{
                'background-color': 'magenta',
                'subset':'funding rate'
            }
        )
        name = path + 'get_upcoming_fundings.png'

    dfi.export(df_img, name)