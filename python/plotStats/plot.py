#%matplotlib notebook
import  matplotlib.pyplot as plt
from pandas.io.json import json_normalize
import json
import re
import yaml

#keywords is a dict of keyword to be analyzed, for example : { default:[enrichment_rate], s1mme:[decipher_rate,map_size]} 
#excludeModules is a list to exclude from analyze, for example: ['dns','sgsap']
def analyze(keywords,excludeModules, data):
    
    regexs = { module: re.compile('|'.join(keys)) for module,keys in keywords.items() }  
        
    # toBeAnalyzed = { moduleName : [column_name] } while column has the keywords    
    toBeAnalyzed = {}
    for key,arrOfColumns in data.items():
        if ( key.lower() in map(lambda x:x.lower(), excludeModules) ): 
            continue
        
        # For each module, if there is a pattern to search with, find out all the columns 
        regex = regexs.get('default',None)
        for module, searchPattern in regexs.items():
            if module.lower() in key.lower() : 
               regex = searchPattern
        if regex == None:
            continue        
        
        filterColumns = [ x for x in arrOfColumns.columns if regex.search(x) != None ]
        # find columns with large than 0 cells
        filteredColumns = [ x for x in filterColumns if arrOfColumns[x].max() > 0 ]
        if len(filteredColumns) > 0:
            toBeAnalyzed.setdefault(key,[]).extend(filteredColumns)
            
    return toBeAnalyzed        

#Union of two dicts with format: {key : []}, {key: []}
# {'a':['A','B'],'b':'B'} , {'a':['A','C']} will return {'a':['A','B','C'],'b':'B'} 
def unionDicts(dict1, dict2):
    unionedDict={}
    for key in set(dict1).union(dict2):
        if key in dict1 and key in dict2: 
            unionedDict[key] = list (set(dict1.get(key)) | set(dict2.get(key)))
        elif key in dict1: 
            unionedDict[key] = dict1.get(key)
        else:
            unionedDict[key] = dict2.get(key)
    return unionedDict        

#only support plot of two data together
def plot(title, toBeAnalyzed,data,toBeAnalyzed1={},data1={} ):
    NUMOfPOINTS = 500    #One point represents 1 min, so this is about ~6 hours data.
    unionedPloteds = unionDicts(toBeAnalyzed,toBeAnalyzed1)
    
    size=0
    for key,columns in unionedPloteds.items():
        size = size + len(columns)

    if size == 0 :
        return 
    
    print(size) 
    fig,axes = plt.subplots(size,1,sharex=True,figsize=(8,4*size))
    fig.suptitle(item+'_Analyze', fontsize=16)
    i=0
    for key,columns in unionedPloteds.items(): 
        for column in columns:
            axRef = axes if size ==1 else axes[i]
            axRef.set_title(key + ":" + '.'.join(column.split('.')[-3:]))
            if key in data and column in data[key].columns:
                data[key][column].plot(ax=axRef)
            if key in data1 and column in data1[key].columns:    
                data1[key][column].plot(ax=axRef)
            axRef.set_xlim(0,NUMOfPOINTS)               
            i=i+1
    
    saveFile = item+'.pdf'
    #Need to make sure all the file are closed when this is called otherwise, this will fail in the runtime
    plt.savefig(saveFile) 

# This load json file and return { key: [dataframe..] } while key is the module name and a list of dataframes            
def load(jsonFile):
    db = json.load(open(jsonFile))

    # moduleJson is a { moduleName: [json record...] }
    moduleJson = {}
    for record in db: 
        module = record['xcp']['module']
        if module == "stats.CStateMachinePipelineModule" :
            module = record['xcp']['measurements']['pipeline_name']
        elif module == "stats.CCsvWriterModule":
            module = record['xcp']['measurements']['writer_name']
        else:
            module = module.split('.')[1]
        moduleJson.setdefault(module,[]).append(record)

    # data is normalized data, key as the module name    
    # see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.io.json.json_normalize.html on how json format can turn into a dataframe
    data = { key: json_normalize(x) for key ,x in moduleJson.items() } 
    return data

            
if __name__ == '__main__':

    with open("analyzeLog.yml") as stream:
        config = yaml.safe_load(stream)
           
    data = load('xcp.probed_stats.log.json')
    for item in config['Pickup']:
        toBeAnalyzed = analyze(config[item],config['ExcludeModules'],data)
        #toBeAnalyzed1 = analyze(config[item],config['ExcludeModules'],data1)
        #plot(item, toBeAnalyzed,data,toBeAnalyzed1,data1)
        plot(item, toBeAnalyzed,data)