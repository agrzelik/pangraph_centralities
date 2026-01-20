import numpy as np
import pandas as pd
from scipy.linalg import eig, inv
import numpy as np

test_run_on = True

if test_run_on:
    base_path = 'test_output_files/'
else:
    base_path = 'output_files/'

# REPRESENTATIONS IMPORT
HAM0 = pd.read_csv(base_path+'adj_matrix_hypergraph.csv')
HAM0 = HAM0.drop(columns=['Unnamed: 0'])
PAM0 = pd.read_csv(base_path+'adj_matrix_pangraph.csv')
PAM0 = PAM0.drop(columns=['Unnamed: 0'])
PGAM0 = pd.read_csv(base_path+'adj_matrix_levi_pangraph.csv')
PGAM0 = PGAM0.drop(columns=['Unnamed: 0'])
# Attribute names to dataframes
HAM0.name = "HAM0"
PAM0.name = "PAM0"
PGAM0.name = "GPAM0"

def preprocess_df(df):
    df = df.values
    rep = df
    reversed_rep = df.T
    return rep, reversed_rep

# CENTRALITY

def katz_centrality(obj, b):
    A = np.array(obj, dtype=float) 
    eigenvalues, _ = eig(A)
    leadingeigenvalue = np.max(eigenvalues.real)
    
    n = A.shape[0]
    a = 0.9 * (1 / leadingeigenvalue)
    
    s = inv(np.eye(n) - (a * A.T)) @ (b * np.ones((n, 1)))
    
    return s, leadingeigenvalue

def test_centralities(df):
    df_test = pd.read_csv('test_input_files/centralities_test_file.csv', delimiter=";", decimal=",")
    num_cols = ['Katz_in_H','Katz_out_H', 'Katz_in_P', 'Katz_out_P', 'Katz_in_G', 'Katz_out_G']

    passed = np.isclose(df_test[num_cols], df[num_cols], atol=1e-3).all().all()

    if passed:
        print(f"[PASSED] Centrality values acceptance test")
    else:
        print(f"[FAILED] Centrality values acceptance test")
    

# CALCULATIONS
for df in [HAM0, PAM0, PGAM0]:
    rep, reversed_rep = preprocess_df(df)
    katz_rep, _ = katz_centrality(rep, 1)
    katz_reversed_rep, _ = katz_centrality(reversed_rep, 1)
    # Create a temporary DataFrame for each representation
    temp_df = pd.DataFrame({
        'species': df.columns,
        f'Katz_in_{df.name[0]}': katz_rep.flatten(),
        f'Katz_out_{df.name[0]}': katz_reversed_rep.flatten()
    })

    if df is PAM0:
        temp_df.to_csv(base_path+'pangraph_centralities.csv')

    # If centrality_df doesn't exist, initialize it
    if 'centrality_df' not in locals():
        centrality_df = temp_df
    else:
        # Merge new columns into the main DataFrame
        centrality_df = centrality_df.merge(temp_df, on='species', how='inner')

    

if test_run_on:
    test_centralities(centrality_df)

centrality_df.to_csv(base_path+'merged_centralities.csv')

