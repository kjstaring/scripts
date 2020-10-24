import json

with open('datasets/vienna.json', encoding='utf-8-sig') as CityJSON_file:
    data = json.load(CityJSON_file)

    CityObjects = data['CityObjects']
    for ID in CityObjects:
        try:
            CityObjects[ID].pop('address', None)
        except:
            pass
        geometries = CityObjects[ID]['geometry']
        for geom in geometries:
            try:
                geom.pop('material', None)
            except:
                pass
            try:
                geom.pop('texture', None)
            except:
                pass 
            try: 
                geom.pop('semantics', None)
            except:
                pass
    try:
        data.pop('appearance', None)
    except:
        pass

with open('cityjson_datasets/NOdatasets/NOvienna.json', 'w') as data_file:
    print('done')
    json.dump(data, data_file)
    data_file.close()


