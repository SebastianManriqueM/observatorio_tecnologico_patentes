import requests
import json


class Patents():
    def __init__(self):
        self.url="https://api.patentsview.org/patents/query?"
        self.curr_page = 1
        self.n_pt_per_page = 100
        self.filters = {'q': {},
                        'f': [],
                        'o': json.dumps({"page": self.curr_page, "per_page": self.n_pt_per_page})
                        }
        self.raw_data = []
        self.ord_data = []

    def get_with_filters(self):
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
                        d_raw_data[i_outt_key] = int(i_outt_value)
                        continue
                    d_raw_data[i_outt_key] = i_outt_value
                l_raw_data.append(d_raw_data)
            return l_raw_data
            
        s = requests.Session()
        with requests.session() as s:
            url = self.url
            response = s.get( url, params=self.filters )
            self.raw_data.append( response.json() )
            if self.raw_data[0]["total_patent_count"] > self.n_pt_per_page:
                n_pt_read = self.n_pt_per_page
                counter = 2
                while (self.raw_data[0]["total_patent_count"] > n_pt_read):
                    self.curr_page = counter
                    self.filters['o'] = json.dumps({"page": self.curr_page, "per_page": self.n_pt_per_page})
                    response = s.get( url, params=self.filters )
                    self.raw_data.append( response.json() )
                    n_pt_read = n_pt_read + self.raw_data[counter-1]["count"]
                    counter += 1
                
                l_data = []
                count = 0
            
                for i_l_element in self.raw_data:
                    self.ord_data.extend( organize_for_dataframe(self.raw_data[count]['patents']) )
                    count += 1
        return
    
    def write_user_request_filters( self, user_dates: dict , user_pt_code: list, type="cpc" ):

        def date_filter( user_dates ):
            l_dates = []
            for key, value in user_dates.items():
                if key == "ini":
                    l_dates.append( value['year'] + '-' + value['month'] + '-' + value['day'] )
                elif key == "fin":
                    l_dates.append( value['year'] + '-' + value['month'] + '-' + value['day'] )

            l_date_filter = []
            d_date_gte = {"_gte": { "app_date": l_dates[0] } }
            l_date_filter.append( d_date_gte )

            d_date_lte = {"_lt": { "app_date": l_dates[1] } }
            l_date_filter.append( d_date_lte )

            return l_date_filter

        def append_filter_params( List_filter:list, List_append:list):
            for l_element in List_append:
                List_filter.append( l_element )
            return List_filter
        
        def ipc_code_filter( ipc_code ):
            l_ipc_filter = [ {"ipc_section": ipc_code[0]}, {"ipc_class": ipc_code[1]}, {"ipc_subclass": ipc_code[2]}, {"ipc_main_group": ipc_code[3]} ]
            return l_ipc_filter
        
        def cpc_code_filter( cpc_code ):
            d_cpc_filt = {"_or": []}
            for element in cpc_code:
                d_temp = {"cpc_subgroup_id": element }
                d_cpc_filt["_or"].append(d_temp)
            return [d_cpc_filt]
            

        request_filt = {"_and": []}
        request_filt["_and"] = append_filter_params( request_filt["_and"] ,date_filter( user_dates ) )

        if ( type == "cpc" ):
            request_filt["_and"] = append_filter_params( request_filt["_and"] ,cpc_code_filter( user_pt_code ) )
        else:
            request_filt["_and"] = append_filter_params( request_filt["_and"] , ipc_code_filter( user_pt_code ) )
        #print("***",request_filt)

        self.filters['q'] = json.dumps(request_filt)
        return 1
    
    def write_user_back_data( self, user_back_data_filt: list ):
        self.filters['f'] = json.dumps( user_back_data_filt )
        return 1