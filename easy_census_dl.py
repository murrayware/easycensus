import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import shapely.wkt
import shapefile

class Census:
    def __init__(self, path):
        self.path = path
        
    
    
    #create easy JSON for census
    def easy_census(self):
        df = pd.read_csv(self.path, encoding='ISO-8859-1')
        #count spaces in string, used to find indentation for grouping in final JSON
        def count_spaces(a):
            count = len(a) - len(a.lstrip())
            return count/2
        
        #apply count spaces to both files
        df['spaces'] = df['CHARACTERISTIC_NAME'].apply(count_spaces)
        
        
        df['CHARACTERISTIC_NAME'] = df['CHARACTERISTIC_NAME'].str.strip()
        
        
        df_grp = df.groupby('ALT_GEO_CODE').agg(list)
        df_grp = df_grp.reset_index(level=0)
        df_grp = df_grp[['C1_COUNT_TOTAL','CHARACTERISTIC_NAME','spaces', 'ALT_GEO_CODE', 'GEO_LEVEL', 'GEO_NAME']]
        
        
        #create dict structuree then apply and create json
        def create_dict(vals, keys, spaces):
            end_dict = {}
            dict_within = {}
            count = 0
            placeholder = ''
            for i in range(len(keys)):
                if i+1 < len(keys):
                    if spaces[i] == 0 and spaces[i+1] == 0:
                        end_dict[keys[i]] = vals[i]
                    if spaces[i] == 0 and spaces[i+1] != 0:
                        count = count + 1
                        placeholder = keys[i]
                    elif spaces[i-1] !=0 and spaces[i] == 0 and spaces[i+1] != 0:
                        end_dict[placeholder] = dict_within
                        dict_within = {}
                        count = 0
                    if spaces[i-1] !=0 and spaces[i] == 0 and spaces[i+1] != 0:
                        end_dict[placeholder] = dict_within
                        dict_within = {}
                        count = 0
                        placeholder = keys[i]
                    if spaces[i-1] !=0 and spaces[i] == 0 and spaces[i+1] == 0:
                        end_dict[placeholder] = dict_within
                        dict_within = {}
                        count = 0
                        end_dict[keys[i]] = vals[i]
                    if spaces[i] != 0:
                        dict_within[keys[i]] = vals[i]
                        count = count + 1
            return end_dict
        
        def grab_first(lst):
            return lst[0]
        df_grp['json'] = df_grp.apply(lambda x: create_dict(x.C1_COUNT_TOTAL, x.CHARACTERISTIC_NAME, x.spaces), axis=1)
        df_grp['GEO_LEVEL'] = df_grp.GEO_LEVEL.apply(grab_first)
        df_grp['GEO_NAME'] = df_grp.GEO_NAME.apply(grab_first)
        df_grp = df_grp[['GEO_NAME', 'ALT_GEO_CODE', 'GEO_LEVEL', 'json']]
        return df_grp

    
        
    def geometry_easy_simplified(self, geo_path, tenser = 80, write_json = ''):
        #read in df from path
        data = self.easy_census()
        #take in shp, geojson 
        bound = gpd.read_file(geo_path, encoding='ISO-8859-1')
        bound['geometry'] = bound['geometry'].simplify(tenser).buffer(0)
        
        bound['PRUID']=bound['PRUID'].astype(int)
        self.geo_file = pd.merge(bound, data, left_on='PRUID', right_on='ALT_GEO_CODE', how='left')
        if write_json == '':
            pass
        else:
            self.geo_file.to_file(write_json, driver='GeoJSON')
        
        
        return self.geo_file
        
                        


