import pandas as pd
import os
import numpy as np

def parse_entry(x):
    x = x.strip()
    if x.startswith("[") and x.endswith("]"):
        inner = x[1:-1].strip()
        items = [i.strip().strip("'\"") for i in inner.split(",")]
        return items
    return [x.strip("'\"")] 

def get_adjacency_matrix(df, type):
    #get adjacency matrix A^{out} for pangraph, pangraph's levi graph,
    df.columns = ['in', 'out']
    nodes = list(set(df['in']).union(set(df['out'])))
    A = [[0 for _ in nodes] for _ in nodes]

    node_idx = {node: i for i, node in enumerate(nodes)}
    for _, row in df.iterrows():
        out_node = row['out']
        in_node = row['in']
        A[node_idx[in_node]][node_idx[out_node]] += 1

    adj_matrix = pd.DataFrame(A, index=nodes, columns=nodes)
    adj_matrix.to_csv(base_path+f'adj_matrix_{type}.csv', sep=';')

def get_h_adjacency_alternative(df, type):
    #get adjacency matrix A^{out} for hypergraph,
    multiedges = []

    for idx, row in df.iterrows():
        left  = parse_entry(row['in'])
        right = parse_entry(row['out'])

        for u in left:
            for v in right:
                multiedges.append((u, v))
                
    nodes = sorted(set([u for u, v in multiedges] + [v for u, v in multiedges]))
    adj = pd.DataFrame(0, index=nodes, columns=nodes)

    for u, v in multiedges:
        adj.loc[u, v] += 1

    adj.to_csv(base_path+f'adj_matrix_{type}.csv', sep=';')

    return adj

def clear(string1):
    return string1.replace(' ', '')

def get_pangraph_vertices(pangraph_edges_df):
    pangraph_levi_adjacency = pd.read_csv('output_files/adjacency_edges_list_files/adj_matrix_levi_pangraph.csv', delimiter=';', index_col='Unnamed: 0')

    levi_edges = []
    for col in pangraph_levi_adjacency.columns:
        for row in pangraph_levi_adjacency.index:
            if pangraph_levi_adjacency.at[row, col] == 1:
                levi_edges.append({'0': col, '1': row})

    levi_edges_df = pd.DataFrame(levi_edges)
    #levi_edges_df.to_csv(base_path+'levi_pangraph_edges_list.csv', sep=';',encoding='utf-8')

    levi_edges_df.columns = ['in','out']

    deg_out = pangraph_levi_adjacency.sum(axis=0)
    deg_in = pangraph_levi_adjacency.sum(axis=1)

    vertex_list = pangraph_levi_adjacency.columns
    vertex_list = list(vertex_list)

    to_del = []
    to_add = []

    del_count, add_count = 0, 0

    for edge2 in vertex_list:#edge2 is in V \cup E_P and if it is not in V_P we will replace it by adjacency relation between its ends
            if '(' in edge2:#is an edge
                if (deg_out[edge2]==1 and deg_in[edge2]==1):#nothing points at it, is not in V_P
                    #print(edge2)
                    for index,row in levi_edges_df.iterrows():
                        new_start, new_end = None, None
                        #print(row['in'] == edge2)

                        if clear(row['in']) == clear(edge2):#so row is the relation starting in edge2
                            new_end = row['out']#and pointing at row['out']

                        if clear(row['out']) == clear(edge2):#this time row points at edge2 
                            new_start = row['in']#and starts in row['in']
                        #so knowing degrees equal to 1, we know there is only one end and one start
                        if ((clear(row['in']) == clear(edge2)) or (clear(row['out']) == clear(edge2))):#here we save which rows pointing/starting at edge2 will be replaced by one edge
                            to_del.append(index)
                            del_count += 1
                            key = edge2

                        if ((new_start is not None) or (new_end is not None)):
                            #print(new_start, new_end)
                            add_count += 1
                            to_add.append([key, new_start, new_end])#here we save the new, direct edge
    return to_add, to_del, levi_edges_df

def df_operations(df, to_add, to_del):
    #operations performed to get df containing pangraph edges list
    dfangraph_edges = df.copy(deep=True)
     
    dfangraph_edges = dfangraph_edges.drop(to_del)

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

        dfangraph_edges = dfangraph_edges._append({'in': new_start, 'out': new_end}, ignore_index=True)

    #dfangraph_edges.to_csv(base_path+'pangraph_edges_list.csv', sep=';',encoding='utf-8')

    return dfangraph_edges

def get_incidence_matrices(new_edges_df):
    incidence_rows_list = list(set(set(new_edges_df['in']).union(set(new_edges_df['out']))))
    incidence_columns_list = list(new_edges_df.apply(lambda row: f'({row['in']},{row['out']})', axis=1))
    '''
    for idx, row in new_edges_df.iterrows():
        incidence_rows_list.append(row['in'])
        incidence_rows_list.append(row['out'])
        incidence_columns_list.append(f'({row['in']},{row['out']})')
        '''
    #incidence_rows = list(set(incidence_rows_list))
    #incidence_columns = list(set(incidence_columns_list))
    incidence_minus = pd.DataFrame(0, index = incidence_rows_list, columns = incidence_columns_list)
    incidence_plus = pd.DataFrame(0, index = incidence_rows_list, columns = incidence_columns_list)
    for idx, row in new_edges_df.iterrows():
        incidence_minus.loc[row['in'],f'({row['in']},{row['out']})'] += 1 
        incidence_plus.loc[row['out'],f'({row['in']},{row['out']})'] += 1

    return incidence_minus, incidence_plus

def is_in_k_prim(pangraph_edges_df):
    k_prim_names =[]
    zero_data = np.zeros(shape=(len(pangraph_edges_df),1))
    indicator_series = pd.Series()

    for _, edge in pangraph_edges_df.iterrows():
        name = "(" + edge['in'] + ',' + edge['out'] + ")"
        if name in list(pangraph_edges_df.out):
            indicator_series[name] = True
        else:
            indicator_series[name] = False

    return indicator_series
    

def get_adjacency_pangraph(incidence_minus, incidence_plus, indicator_matrix):
    idx = incidence_minus.index
    cols = incidence_minus.columns
    k_minus_k_prim = list(set(cols) - (set(idx)))
    i_minus = incidence_minus.to_numpy()
    i_plus = incidence_plus.to_numpy()
    '''
    k_prim_vertices = list(indicator_matrix[indicator_matrix].index)
    base_vertices = [x for x in idx if '(' not in x]
    adj_index = base_vertices + k_prim_vertices
    '''
    adj_in_matrix = pd.DataFrame(0, index=idx, columns=idx)
    
    for v1 in idx:
        for v2 in idx:
            if v2 in cols: #is v2 an edge
                if indicator_matrix[v2]: #is v2 in k_prim
                    adj_in_matrix.loc[v1, v2] += incidence_minus.loc[v2, v1]
            if v1 in cols: #is v1 an edge
                if indicator_matrix[v1]: #is v1 in k_prim
                    adj_in_matrix.loc[v1, v2] += incidence_plus.loc[v1, v2] 
            
            for k in k_minus_k_prim: #for k in K\K'
                adj_in_matrix.loc[v1, v2] += incidence_minus.loc[v1, k] * incidence_plus.loc[v2, k]
                    
    adj_out_matrix = adj_in_matrix.T
    
    return adj_in_matrix, adj_out_matrix



def sort_df(df):
    #alphabetic sorting function
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.sort_values(by=list(df.columns))
    df = df.reset_index(drop=True)
    
    return df

def test_adjacency_matrix():
    #acceptance test of the adjacency matrix values for test case
    for key, item in adjacency_dict.items():
        df_code = pd.read_csv(item, delimiter=",", index_col=0)
        df_input = pd.read_csv(os.path.join("test_input_files",key+"_adjacency_matrix.csv"),delimiter=";", index_col=0)

        df_code =  sort_df(df_code)
        if "hyper" in key:
            df_input = sort_df(df_input.T)
        else:
            df_input = sort_df(df_input)

        if df_code.equals(df_input):
            print(f"[PASSED] Adjacency matrix acceptance test: {key}")
        else:
            print(f"[FAILED] Adjacency matrix acceptance test: {key}")

def test_degrees():
    #acceptance test of the node degree values for test case
    df_code = pd.read_csv('test_output_files/degrees.csv')
    df_code = df_code.drop(columns=[c for c in df_code.columns if 'Unnamed' in c])
    df_code = df_code.set_index('species')
    df_input = pd.read_csv('test_input_files/degrees-test.csv')
    df_input = df_input.set_index('Unnamed: 0')
    df_input.index.name = 'species'

    df_input = df_input.sort_index(axis=0)
    df_code = df_code.sort_index(axis=0)

    if (df_input).equals(df_code):
        print(f"[PASSED] Degree values acceptance test")
    else:
        print(f"[FAILED] Degree values acceptance test")

def get_node_degrees(df, type):
    #getting node degree values based on adjacency matrix
    
    df = df.set_index('Unnamed: 0')
    degrees_in = df.sum(axis=0)
    degrees_out = df.sum(axis=1)
    degree_df = pd.DataFrame({'species': degrees_in.index, 'degree_in': degrees_in.values, 'degree_out': degrees_out.values})
    degree_df.to_csv(base_path+f'degrees_df_{type}.csv', sep=';')

def merge_degrees():
    #merging degrees values for different representations
    final_df = pd.DataFrame()
    for key, __ in adjacency_dict.items():
        df = pd.read_csv(base_path+f'degrees_df_{key}.csv', sep=';')
        df = df.rename(columns={'degree_in': f'degree_in_{key}', 'degree_out': f'degree_out_{key}'})
        if final_df.empty:
            final_df = df
        else:
            final_df = final_df.merge(df[['species', f'degree_in_{key}', f'degree_out_{key}']], on='species', how='inner')
        final_df.to_csv(base_path.replace('adjacency_edges_list_files/', '')+'degrees.csv', index=False, sep=';')

for test_run_on in [False]: #[True, False]:
    #running processing for test case and coffee agroecosystem 

    base_path = 'test_output_files/adjacency_edges_list_files/' if test_run_on else 'output_files/adjacency_edges_list_files/'

    h_df = pd.read_csv(base_path+'hypergraph_edges_list.csv',index_col=0, delimiter = ';')
    h_df.columns = ['in', 'out']
    p_old_df = pd.read_csv(base_path+'levi_pangraph_edges_list.csv',index_col=0, delimiter = ';')
    p_old_df.columns = [ 'in', 'out']
    pangraph_edges_df = pd.read_csv(base_path+'pangraph_edges_list.csv',index_col=0, delimiter = ';')
    pangraph_edges_df.columns = ['in', 'out']

    options_dict = {'hypergraph': h_df,
                'pangraph': pangraph_edges_df,
                'levi_pangraph': p_old_df}
    
    adjacency_dict = {'hypergraph': base_path+'adj_matrix_hypergraph.csv',
                'pangraph': 'output_files/0206_adj_in.csv',
                'levi_pangraph': base_path+'adj_matrix_levi_pangraph.csv'}

    for key, item in options_dict.items():
        if 'levi' in key:
            get_adjacency_matrix(item, key)
        elif 'hyper' in key:
            get_h_adjacency_alternative(item, key)
        else:
            continue
    
    #get vertices from V_P
    to_add, to_del, levi_edges = get_pangraph_vertices(pangraph_edges_df)
    new_edges_df = df_operations(levi_edges, to_add, to_del)
    new_edges_df.to_csv(base_path+'pangraph_edges_for_fundamental_vertices.csv', sep=';')
   
    #make adjacency matrix for pangraph

    incidence_minus, incidence_plus = get_incidence_matrices(new_edges_df)
    incidence_minus.to_csv('output_files/0206_incidence_minus.csv')
    incidence_plus.to_csv('output_files/0206_incidence_plus.csv')
    indicator_df = is_in_k_prim(pangraph_edges_df)
    _, a_out = get_adjacency_pangraph(incidence_minus, incidence_plus, indicator_df)
    a_out.to_csv('output_files/0206_adj_in.csv', sep = ';')

    '''
    options_dict['pangraph'] = new_edges_df

    for key, item in options_dict.items():
        if 'hyper' not in key and 'levi' not in key:
                get_adjacency_matrix(options_dict['pangraph'],'pangraph')
        else:
            continue
    '''

    for key, source in adjacency_dict.items():
        df = pd.read_csv(source, sep=';')
        get_node_degrees(df, key)

    merge_degrees()

    if test_run_on:
        test_adjacency_matrix()
        test_degrees()


