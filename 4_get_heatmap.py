import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

test_run_on = False

if test_run_on:
    base_path = 'test_output_files/'
else:
    base_path = 'output_files/'

def heatmap_plot(df_map):

    df = pd.read_csv(base_path+'merged_centralities.csv')

    df.index = df['species']
    df = df.drop(columns=['species'])

    df_map = df_map[['species', 'degree_in_hypergraph', 'degree_out_hypergraph', 'degree_in_pangraph', 'degree_out_pangraph']]
    df_map.columns = ['species', 'in-degree-H','out-degree-H', 'in-degree-P', 'out-degree-P']
    
    df = df.merge(df_map, left_index=True, right_on='species')

    df_in = df[['Katz_in_P', 'Katz_in_G', 'in-degree-P', 'Katz_in_H', 'in-degree-H', 'species']]
    df_in.set_index('species', inplace=True)
    df_in.columns = [
       'Katz_pangraph_in', 
       'Katz_pangraph_Levi_graph_in', 'in-degree-P','Katz_hypergraph_in','in-degree-H',]
    df_in = df_in.sort_values('Katz_pangraph_in', ascending=False)
    

    df_out = df[[  'Katz_out_P',
        'Katz_out_G',
       'out-degree-P', 'Katz_out_H', 'out-degree-H', 'species']]
    df_out.set_index('species', inplace=True)
    df_out.columns = [  'Katz_pangraph_out',
        'Katz_pangraph_Levi_graph_out','out-degree-P','Katz_hypergraph_out', 'out-degree-H',]
    df_out = df_out.sort_values('Katz_pangraph_out', ascending=False)

    for (df_map,type) in zip([df_in,df_out],['in','out']):
        fig, axes = plt.subplots(1, df_map.shape[1], figsize=(15, 15))
        subtle_grey_palette = sns.light_palette("gray", n_colors=10, reverse=False, as_cmap=True)

        for i, col in enumerate(df_map.columns):
            if 'Katz_pangraph_' in col and 'Levi_graph' not in col:
                col_min = df_map[col].min()
                col_max = df_map[col].max()
                sns.heatmap(df_map[[col]], annot=True, cmap="crest", fmt='.2f', vmin=0, vmax=50, ax=axes[i], cbar=(i == 8), xticklabels=False)
                axes[i].set_title(f"{col}")
                axes[i].set_xlabel('')
                axes[i].set_ylabel('')
            else:
                if 'Katz' in str(col):
                    col_min = df_map[col].min()
                    col_max = df_map[col].max()
                    sns.heatmap(df_map[[col]], annot=True, cmap="crest", fmt='.2f', vmin=0, vmax=50, ax=axes[i], cbar=(i == 8), xticklabels = False, yticklabels=False)
                    axes[i].set_title(f"{col}")
                    axes[i].set_ylabel('')
                else:
                    col_min = df_map[col].min()
                    col_max = df_map[col].max()
                    sns.heatmap(df_map[[col]], annot=True, cmap=subtle_grey_palette, vmin=1, vmax=26, ax=axes[i], cbar=(i == 8), xticklabels = False, yticklabels=False)
                    axes[i].set_title(f"{col}")
                    axes[i].set_ylabel('')

        plt.tight_layout()
        fig.savefig(base_path+f'heatmap_{type}.pdf', bbox_inches = "tight")

df = pd.read_csv(base_path+'merged_degrees.csv')
heatmap_plot(df)