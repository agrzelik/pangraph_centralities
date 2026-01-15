# Pangraph centrality analysis

![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)

## Project overview
This project provides a pipeline for processing **pangraph incidence matrices**. It transforms initial file into multiple graph representations, computes Katz centrality values, and generates comparative visualizations. The goal is to analyze the structural importance of fundamental vertices across different graph interpretations (hypergraph, pangraph, and pangraph's Levi graph).

---

## Workflow & methodology

The analysis is divided into four steps:

### 1. Graph representations
The pipeline converts the initial incidence matrix into three distinct edge lists:
* **hypergraph**
* **pangraph** 
* **pangraph's Levi graph** 

### 2. Adjacency matrix construction
In this step, adjacency lists are transformed into **adjacency matrices**. Here, the code computes:
* **in-degree** and **out-degree** for all fundamental vertices,
* a merged DataFrame containing structural properties for downstream analysis.

### 3. Katz centrality computation
We compute **Katz centralities** to measure the relative influence of vertices within the network. 

The calculation uses the following matrix formula:

$$C_{Katz} = (I - \alpha A^T)^{-1} \cdot \beta$$

Where:
* $I$ is the identity matrix.
* $\alpha$ is a parameter that is set to be the inversion of the leading eigenvalue.
* $A^T$ is the transposed adjacency matrix.
* $\beta$ is a parameter set to 1. 

### 4. Visualization & heatmap analysis
The final step produces heatmaps to facilitate comparative analysis. These visualizations allow for an intuitive comparison of vertex importance across the three graph representations.

**Visualizations:**
* **In-centralities:** Comparison of Katz in-centrality scores and vertex in-degrees across representations.
* **Out-centralities:** Comparison of Katz out-centrality scores and vertex out-degrees across representations.

[Katz Centrality Heatmap](output_files/heatmap_out.pdf)

## Execution & modes

The entire analysis pipeline can be executed directly using the `run_all.py` script, which runs the flow from data processing to visualization. The behavior of the underlying modules is controlled by a configuration flag: `test_run_on`. Setting this flag to **False** (default) allows for the processing of the full-scale data described in the research article. Alternatively, switching to **True** enables an execution on a minimal dataset. This test option is specifically designed for rapid code verification and includes a comprehensive suite of acceptance tests to ensure that all steps remain consistent and correct. 

## Installation & setup
To ensure all dependencies are compatible with Python 3.13, install the required packages using the provided `requirements.txt` file:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the complete pipeline
python run_all.py
```

## Citation
 Please, cite as:
 ```
 @misc{iskrzyński2025pangraphsmodelshigherorderinteractions,
       title={Pangraphs as models of higher-order interactions}, 
       author={Mateusz Iskrzyński and Aleksandra Puchalska and Aleksandra Grzelik and Gökhan Mutlu},
       year={2025},
       eprint={2502.10141},
       archivePrefix={arXiv},
       primaryClass={physics.soc-ph},
       url={https://arxiv.org/abs/2502.10141}, 
 }
 ```
