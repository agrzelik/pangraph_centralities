import pandas as pd
import os
import ast

test_run_on = True
if test_run_on:
    base_path='test_files/'
else:
    base_path='clean_files/'

def getends(panedge):#Returns [e^in, e^out] for an panedge given as string
    d=0
    i=0
    if len(panedge)==0: return()
    if not (panedge[0]=='(' and panedge[-1]==')'): raise Exception("The ends are wrong. Correct are: '(...,...)")
    u=panedge[1:-1] #we extract the content, so we discard the brackets
    
    for x in u:
       
       if x=='(': d+=1
       elif x==')': d+=-1
       elif x==',':
           if len(u)<=i+1: 
               raise Exception("Incomplete panedge, some brackets are missing")
           elif d==0: 
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
    commas=panedge.split(',')
    if len(commas)<=1: raise Exception("panedge does not contain a comma")
    ends=getends(panedge)
    if len(commas)==2:
        
        return(ends)
    comm_ends=[ends[j].split(',') for j in [0,1]]
    hyperedge=[[],[]]
    for k in [0,1]:
        if len(comm_ends[k])<2: 
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

def preprocessing():
    if test_run_on == True:
        ubergraph_incidence = pd.read_csv('./files/test_incidence.csv', delimiter=';', index_col='Unnamed: 0')
    else:
        ubergraph_incidence = pd.read_csv('./files/pangraph_incidence.csv', delimiter=';', index_col='Unnamed: 0')
    incidence_edges = []
    for col in ubergraph_incidence.columns:
        for row in ubergraph_incidence.index:
            if ubergraph_incidence.at[row, col] == 1:
                incidence_edges.append({'0': col, '1': row})

    incidence_edges_df = pd.DataFrame(incidence_edges)
    incidence_edges_df.to_csv(base_path+'generalized_pangraph_edges_list.csv', sep=';',encoding='utf-8')
    levi_edges = incidence_edges_df

    levi_edges.columns = ['start','end']

    deg_out = ubergraph_incidence.sum(axis=0)
    deg_in = ubergraph_incidence.sum(axis=1)

    vertex_list = ubergraph_incidence.columns
    vertex_list = list(vertex_list)

    new_edges_df = levi_edges.copy()
    to_del = []
    to_add = []

    del_count, add_count = 0, 0

    for edge2 in vertex_list:#edge2 is in V \cup E_P and if it is not in V_P we will replace it by adjacency relation between its ends
            if '(' in edge2:#is an edge
                if (deg_out[edge2]==1 and deg_in[edge2]==1):#nothing points at it, is not in V_P
                    #print(edge2)
                    for index,row in levi_edges.iterrows():
                        new_start, new_end = None, None
                        #print(row['start'] == edge2)

                        if clear(row['start']) == clear(edge2):#so row is the relation starting in edge2
                            new_end = row['end']#and pointing at row['end']

                        if clear(row['end']) == clear(edge2):#this time row points at edge2 
                            new_start = row['start']#and starts in row['start']
                        #so knowing degrees equal to 1, we know there is only one end and one start
                        if ((clear(row['start']) == clear(edge2)) or (clear(row['end']) == clear(edge2))):#here we save which rows pointing/starting at edge2 will be replaced by one edge
                            to_del.append(index)
                            del_count += 1
                            key = edge2

                        if ((new_start is not None) or (new_end is not None)):
                            #print(new_start, new_end)
                            add_count += 1
                            to_add.append([key, new_start, new_end])#here we save the new, direct edge
    return to_add, to_del, levi_edges


def df_operations(df, to_add, to_del):
     
    df_new = df.copy(deep=True)
     
    df_new = df_new.drop(to_del)

    add_dict= {}
    add_rows = {}

    for sublist in to_add:
        key = sublist[0] 
        if key not in add_dict:
            add_dict[key] = []
        add_dict[key].append(sublist)

    for key, item in add_dict.items():

        base_start = item[0]
        base_end = item[1]

        if base_start[1] is not None:
            new_start = base_start[1]
            new_end = base_end[2]
        else:
            new_end = base_start[2]
            new_start = base_end[1]

        df_new = df_new._append({'start': new_start, 'end': new_end}, ignore_index=True)

    df_new.to_csv(base_path+'pangraph_edges_list.csv', sep=';',encoding='utf-8')

    return df_new

def split_edges(raw_list):
    rows = []

    for s in raw_list:
        s_clean = str(s)

        if '], [' in s_clean:
            left, right = s_clean.split('], [')
        else:
            left, right = s_clean.split("', '")

        if '[[' in left:
            left =  left + ']]'
        elif '[' in left:
            left = left + ']'

        if ']]' in right:
            right =  '[[' + right
        elif ']' in right:
            right = '[' + right         
        #left = left.replace("[[", "(") + ')'
        #right = '(' + right.replace("]]", ")") 

        rows.append((left, right))

    return pd.DataFrame(rows, columns=["source", "target"])
        
if (hyper_from_pan('(a,(b,c))')!=[['a', 'b'], ['c']]): print('ERROR test 1 not passed')
else: print('[PASSED] Test 1 passed')

if (hyper_from_pan('(a,(b,(c,d)))')!=[['a', 'b', 'c'], ['d']]): print('ERROR test 2 not passed')
else: print('[PASSED] Test 2 passed')




if test_run_on==True:
    m=pd.read_csv("files/test_incidence.csv" , delimiter= ';', encoding='utf-8', header=0, index_col=0)
else:
    m=pd.read_csv("files/pangraph_incidence.csv" , delimiter= ';', encoding='utf-8', header=0, index_col=0)
edge_list=m.index

hyperedge_list=[]
for s in edge_list:
    if '(' in s and ',' in s:
        hyperedge_list.append(hyper_from_pan(s))


hyperedges_df = split_edges(hyperedge_list)
hyperedges_df["source"] = hyperedges_df["source"].apply(lambda x: x.replace('[[', '[').replace(']]', ']').replace("'",""))
hyperedges_df["target"] = hyperedges_df["target"].apply(lambda x: x.replace(']]', ']').replace('[[', '[').replace("'",""))

hyperedges_df.to_csv(base_path+"hypergraph_edges_list.csv", sep=';',encoding='utf-8')

to_add, to_del, levi_edges = preprocessing()
new_edges_df = df_operations(levi_edges, to_add, to_del)