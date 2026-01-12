# Pangraph centrality analysis

![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)

## Project overview
This project provides a pipeline for processing **pangraph incidence matrices**. It transforms initial file into multiple graph representations, computes Katz centrality values, and generates comparative visualizations. The goal is to analyze the structural importance of fundamental vertices across different graph interpretations (hypergraph, pangraph, and pangraph's Levi graph).

---

## Workflow & methodology

The analysis is divided into four steps:

### 1. Graph representations
The pipeline converts the initial incidence matrix into three distinct adjacency list structures:
* **hypergraph**
* **pangraph** 
* **pangraph's Levi graph** 

### 2. Adjacency matrix construction
In this step, adjacency lists are transformed into **adjacency matrices**. Here, the code computes:
* **in-degree** and **out-degree** for all fundamental vertices,
* a merged DataFrame containing structural properties for downstream analysis.

### 3. Katz centrality computation
We calculate the **Katz centralities** to measure the relative influence of vertices within the network. 

The calculation uses the following matrix formula:

$$C_{Katz} = (I - \alpha A^T)^{-1} \cdot (\beta \cdot \mathbf{1})$$

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


---

## Citation
 Please, cite as:

 