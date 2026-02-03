import numpy as np
import pandas as pd
from scipy.linalg import eig, inv
import numpy as np

def preprocess_df(df):
    #preparing representations for in- and out-centrality calculation
    df = df.values
    rep = df
    reversed_rep = df.T
    return rep, reversed_rep

def katz_centrality(obj, b):
    #katz centrality formula 
    A = np.array(obj, dtype=float) 
    eigenvalues, _ = eig(A)
    leadingeigenvalue = np.max(eigenvalues.real)
    
    n = A.shape[0]
    a = 0.9 * (1 / leadingeigenvalue)
    
    s = inv(np.eye(n) - (a * A.T)) @ (b * np.ones((n, 1)))
    
    return s, leadingeigenvalue

def test_centralities(df):
    #acceptance test of the centrality values for test case
    df_test = pd.read_csv('test_input_files/centralities_test_file.csv', delimiter=";", decimal=",")
    num_cols = ['Katz_in_H','Katz_out_H', 'Katz_in_P', 'Katz_out_P', 'Katz_in_G', 'Katz_out_G']

    passed = np.isclose(df_test[num_cols], df[num_cols], atol=1e-3).all().all()

    if passed:
        print(f"[PASSED] Centrality values acceptance test")
    else:
        print(f"[FAILED] Centrality values acceptance test")
    

    
for test_run_on in [True, False]:
    #running processing for test case and coffee agroecosystem 

    if test_run_on:
        base_path = 'test_output_files/'
    else:
        base_path = 'output_files/'

    # representations import
    HAM0 = pd.read_csv(base_path+'adjacency_edges_list_files/adj_matrix_hypergraph.csv')
    HAM0 = HAM0.drop(columns=['Unnamed: 0'])
    PAM0 = pd.read_csv(base_path+'adjacency_edges_list_files/adj_matrix_pangraph.csv')
    PAM0 = PAM0.drop(columns=['Unnamed: 0'])
    PGAM0 = pd.read_csv(base_path+'adjacency_edges_list_files/adj_matrix_levi_pangraph.csv')
    PGAM0 = PGAM0.drop(columns=['Unnamed: 0'])
    HAM0.name = "HAM0"
    PAM0.name = "PAM0"
    PGAM0.name = "GPAM0"

    centrality_df = None
    # calculations
    for i, df in enumerate([HAM0, PAM0, PGAM0]):

        rep, reversed_rep = preprocess_df(df)
        katz_rep, _ = katz_centrality(rep, 1)
        katz_reversed_rep, _ = katz_centrality(reversed_rep, 1)
        # create a temporary df for each representation
        temp_df = pd.DataFrame({
            'species': df.columns,
            f'Katz_in_{df.name[0]}': katz_rep.flatten(),
            f'Katz_out_{df.name[0]}': katz_reversed_rep.flatten()
        })

        if df is PAM0:
            temp_df.to_csv(base_path+'pangraph_centralities.csv')

        if i == 0:
            centrality_df = temp_df
        else:
            centrality_df = centrality_df.merge(temp_df, on='species', how='inner')
    
    if test_run_on:
        test_centralities(centrality_df)

    centrality_df.to_csv(base_path+'katz_centralities.csv')

