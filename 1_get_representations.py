'''
This file processes the adjacency matrices of pangraph's Levi graph. It uses the labels of columns and rows to deduce vertices,
edges and orientations: convention (u,v) = edge from u to v. To get hyperedges it effectively flattens the nested structure of pangraph interactions.
The output of the file consists of edge lists for compared representations. 
'''

import pandas as pd

def getends(panedge):#Returns [e^in, e^out] for an panedge given as string
    d=0
    i=0
    if len(panedge)==0: return()
    if not (panedge[0]=='(' and panedge[-1]==')'): raise Exception("The ends are wrong. Correct are: '(...,...)")
    u=panedge[1:-1] #we extract the content, so we discard the brackets
    
    for x in u:
       
       if x=='(': d+=1.  #then the nearest comma won't be the main comma of the panedge
       elif x==')': d+=-1
       elif x==',':
           if len(u)<=i+1: 
               raise Exception("Incomplete panedge, some brackets are missing")
           elif d==0: #we know this is the main comma
               return(list([u[:i],u[i+1:]])) #return [e^in, e^out]
                   
       i+=1
    raise Exception("We have not reached the desired midpoint comma") 
    
def flatten(foo):
    for x in foo:
        if hasattr(x, '__iter__') and not isinstance(x, str):
            for y in flatten(x):
                yield y
        else:
            yield x
    
def hyper_from_pan(panedge): 
    ''' Given a panedge computes the corresponding hyperedge.'''

    commas=panedge.split(',')
    if len(commas)<=1: raise Exception("panedge does not contain a comma")
    ends=getends(panedge)
    if len(commas)==2: #then we know ends are fundamental vertices
        return(ends)
    
    #the HOI case
    comm_ends=[ends[j].split(',') for j in [0,1]] #list of 2 lists
    hyperedge=[[],[]]
    for k in [0,1]:
        if len(comm_ends[k])<2: #one of e^in/e^out is a fundamental vertex
            hyperedge[k].append(ends[k]) #we save vertices from in to in; from out to out;
        else: #otherwise we enter recursion
            other_k=(k+1) % 2
            hyperk=hyper_from_pan(ends[k])
            hyperedge[k].append(hyperk[k]) #ins from in to in and vice versa
            hyperedge[other_k].append([hyperk[other_k]]) #outs from in to out and vice versa
    hyperedge=[[y for y in flatten(hyperedge[k])] for k in [0,1]]#!isinstance(x, str)]    

    return(hyperedge)

def process_edges(x):
    if '], [' in str(x):
        i, o =  str(x).split('], [')
    else:
        i, o =  str(x).split(',')
    return i, o
    

def clear(string1):
    return string1.replace(' ', '')

def levi_from_pan(panedge):
    """ Each panedge e is a Levi graph vertex and means 2 Levi graph edges: (e^in, e) and (e,e^out)."""
    commas=panedge.split(',')
    if len(commas)<=1: raise Exception("panedge does not contain a comma")
    else: 
        ends=getends(panedge)
        return([[ends[0],ends],[ends,ends[1]]]) 

for test_run_on in [True, False]:#[True, False]:
    #running processing for test case and coffee agroecosystem 

    if test_run_on:
        base_path='test_output_files/adjacency_edges_list_files/'
    else:
        base_path='output_files/adjacency_edges_list_files/'

    if test_run_on == True:
        panedges = pd.read_csv('./files/test-panedges.csv', delimiter=';', index_col=0, header = None)
    else:
        panedges = pd.read_csv('./files/panedges.csv', delimiter=';', index_col=0, header = None)

    panedges.columns = ['panedges']
    panedges_list = list(panedges['panedges'])

    pan_df = []
    
    for panedge in panedges_list:
            panedge_dict = {'in': [], 'out': []}
            l = getends(panedge)
            panedge_dict['in'] = l[0]
            panedge_dict['out'] = l[1]
            pan_df.append(panedge_dict)
    pd.DataFrame(pan_df).to_csv(base_path+'pangraph_edges_list.csv', sep=';',encoding='utf-8')

    hyperedge_list = []
    for panedge in panedges_list:
        #if '(' in s and ',' in s:
        hyperedge_list.append(hyper_from_pan(panedge))

    hyperedges_df = pd.DataFrame(hyperedge_list, columns=["in", "out"])
    #hyperedges_df = split_edges(hyperedge_list)
    #hyperedges_df["in"] = hyperedges_df["in"].apply(lambda x: x.replace('[[', '[').replace(']]', ']').replace("'",""))
    #hyperedges_df["out"] = hyperedges_df["out"].apply(lambda x: x.replace(']]', ']').replace('[[', '[').replace("'",""))

    hyperedges_df.to_csv(base_path+"hypergraph_edges_list.csv", sep=';',encoding='utf-8')

    levi_edges = []
    for panedge in panedges_list: 
        l = levi_from_pan(panedge)
        levi_edges.append(l[0])
        levi_edges.append(l[1])

    levi_edges_df = pd.DataFrame(levi_edges)
    levi_edges_df.columns = ['in', 'out']
    levi_edges_df["in"] = levi_edges_df["in"].apply(lambda x: str(x).replace('[', '(').replace(']', ')').replace("'", '').replace(', ',','))
    levi_edges_df["out"] = levi_edges_df["out"].apply(lambda x: str(x).replace('[', '(').replace(']', ')').replace("'", '').replace(', ',','))
    levi_edges_df.to_csv(base_path+'levi_pangraph_edges_list.csv', sep=';')#,encoding='utf-8')

