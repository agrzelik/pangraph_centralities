import pandas as pd
import networkx as nx
import ast
import numpy as np 
import os

test_run_on = False

base_path = 'test_output_files/' if test_run_on else 'output_files/'

h_df = pd.read_csv(base_path+'hypergraph_edges_list.csv', delimiter = ';')
h_df.columns = ['unnamed', 'in', 'out']
p_old_df = pd.read_csv(base_path+'levi_pangraph_edges_list.csv', delimiter = ';')
p_old_df.columns = ['unnamed', 'in', 'out']
p_new_df = pd.read_csv(base_path+'pangraph_edges_list.csv', delimiter = ';')
p_new_df.columns = ['unnamed', 'in', 'out']

def parse_entry(x):
    x = x.strip()
    if x.startswith("[") and x.endswith("]"):
        inner = x[1:-1].strip()
        items = [i.strip() for i in inner.split(",")]
        return items
    return [x]


def get_adjacency_matrix(df, type):

    nodes = list(set(df['in']).union(set(df['out'])))
    A = [[0 for _ in nodes] for _ in nodes]

    node_idx = {node: i for i, node in enumerate(nodes)}
    for _, row in df.iterrows():
        out_node = row['in']
        in_node = row['out']
        A[node_idx[out_node]][node_idx[in_node]] += 1

    adj_matrix = pd.DataFrame(A, index=nodes, columns=nodes)
    adj_matrix.to_csv(base_path+f'adj_matrix_{type}.csv')

options_dict = {'hypergraph': h_df,
                'pangraph': p_new_df,
                'levi_pangraph': p_old_df}



def get_h_adjacency_alternative(df, type):
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

    adj.to_csv(base_path+f'adj_matrix_{type}.csv')

    return adj

adjacency_dict = {'hypergraph': base_path+'adj_matrix_hypergraph.csv',
                'pangraph': base_path+'adj_matrix_pangraph.csv',
                'levi_pangraph': base_path+'adj_matrix_levi_pangraph.csv'}

def sort_df(df):
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.sort_values(by=list(df.columns))
    df = df.reset_index(drop=True)
    
    return df

def test_adjacency_matrix():
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
    df_code = pd.read_csv('test_output_files/merged_degrees.csv')
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
    df = df.set_index('Unnamed: 0')
    degrees_in = df.sum(axis=0)
    degrees_out = df.sum(axis=1)
    degree_df = pd.DataFrame({'species': degrees_in.index, 'degree_in': degrees_in.values, 'degree_out': degrees_out.values})
    degree_df.to_csv(base_path+f'degrees_df_{type}.csv')

def merge_degrees():
    final_df = pd.DataFrame()
    for key, __ in adjacency_dict.items():
        df = pd.read_csv(base_path+f'degrees_df_{key}.csv')
        df = df.rename(columns={'degree_in': f'degree_in_{key}', 'degree_out': f'degree_out_{key}'})
        if final_df.empty:
            final_df = df
        else:
            final_df = final_df.merge(df[['species', f'degree_in_{key}', f'degree_out_{key}']], on='species', how='inner')
        final_df.to_csv(base_path+'merged_degrees.csv', index=False)

for key, item in options_dict.items():
    if 'hyper' not in key:
        get_adjacency_matrix(item, key)
    else:
        get_h_adjacency_alternative(item, key)

for key, source in adjacency_dict.items():
    df = pd.read_csv(source)
    get_node_degrees(df, key)

merge_degrees()

if test_run_on:
    test_adjacency_matrix()
    test_degrees()


