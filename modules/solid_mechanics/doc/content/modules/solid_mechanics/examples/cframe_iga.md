# Isogeometric Analysis

## Background

[!ac](IGA) is an approach to finite element analysis that was first introduced in 2005 by [!cite](hughes2005isogeometric).
A principal challenge that IGA seeks to address is the inordinate amount time and effort spent generating high-quality meshes for complex geometries.
One issue identified by Hughes was that traditional finite element analysis, at the time, largely relied upon low-order, $C^0$ continuous, interpolatory basis functions while modern [!ac](CAD) systems primarily used higher-order, $C^k$ continuous, non-interpoloatory basis functions known as [!ac](NURBS) to represent complex geometric shapes.
When initially proposed the central hypothesis was that, since NURBS basis functions meet the requirements for both FEM and CAD, that mesh-generation related issues could be largely eliminated simply by utilizing NURBS basis functions within finite element analysis -- thereby linkng the CAD and FEM representations directly.

In practice, however, isogeometric analysis in this nascent form does not address all mesh-generation related issues, namely that the dominant [!ac](BREP) format used by CAD systems defines geometry using (typically trimmed) bounding surfaces rather than volumetric representations.
Furthermore, hexahedral meshes are often preferred for challenging nonlinear problems, yet unlike tetrahedral meshes there is no known algorithm for generating high-quality hexahedral meshes from arbitrary geometries -- a fact that is a primary cause of the principal challenge that IGA was developed to address.
Even the development of various unstructured spline technologies, such as T-splines ([!cite](sederberg2003t)) and U-splines ([!cite](thomas2022u)), have not fully resolved this core mesh-generation issue.

Modern IGA implementations, including the implementation within MOOSE, have focused on immersed-style approaches to the meshing problem.
In these approaches the geometry is "immersed" within a simple or trivial-to-mesh domain, that is then meshed using spline basis functions.
This approach largely eliminates the labor-intensive mesh generation step, at the cost of requiring specialized numerical techniques to accurately and robustly resolve the geometry within the background mesh.

## Mathematic Preliminaries

### Bézier Extraction

A core concept in modern isogeometric analysis is *Bézier extraction* ([!cite](borden2011isogeometric)), which provides a mechanism for representing spline basis functions in terms of standard finite element shape functions.
This allows existing finite element codes, such as MOOSE, to utilize spline basis functions while minimizing significant changes to the underlying codebase.

!alert note
The terminology of *Bézier extraction* comes from the initial development's use of $C^0$ Bernstein polynomials as the underlying basis functions, which are the basis functions used in Bézier curves and surfaces.
However, the exact same technique can also be applied to a spline of any continuity, with $C^{-1}$ basis functions being of particular interest. 
The approach can also be applied to other basis function families, an example being the Lagrange polynomials ([!cite](schillinger2016lagrange)) which was coined *Lagrange* extraction.
Rather than provide unique names for each basis function family, the more general term *extraction* is often used.
!alert-end!

Consider a quadratic $C^1$ B-spline basis, $N(x)$, defined over three uniformly spaced elements on the interval $[0,1]$ and a corresponding $C^{-1}$ B-spline basis, $B(x)$, defined over the same elements.
The global Bézier extraction operator, $\mathbf{C}$, can be computed by 

\begin{equation}
\mathbf{C}^g = \left( \frac{ \langle B, N^T \rangle_{ij} }{ \langle B, B^T \rangle_{ij} } \right)^T
\end{equation}

where $\langle \cdot , \cdot \rangle_{ij}$ indicates the element-wise inner product over the domain.
For example:

\begin{equation}
    \langle B, N^T \rangle_{ij} = 
    \begin{bmatrix}
        \langle B_1, N_1 \rangle & \cdots & \langle B_1, N_5 \rangle \\
        \vdots & \ddots & \vdots \\
        \langle B_7, N_1 \rangle & \cdots & \langle B_7, N_5 \rangle \\
    \end{bmatrix}
\end{equation}

The spline basis functions can then be represented in terms of the Bézier basis functions as:

\begin{equation}
    N(x) = \mathbf{C}^g B(x)
\end{equation}

The global extraction operator can be used to perform global assembly:

\begin{equation}
    \mathbf{K}^g = \mathbf{C}^{g} \mathbf{K}^b \left( \mathbf{C}^g \right)^T
\end{equation}

Where $\mathbf{K}^b$ is the global stiffness matrix assembled using the $C^{-1}$ basis functions and $\mathbf{K}^g$ is the global stiffness matrix assembled using the $C^1$ basis functions:

\begin{equation}
    \mathbf{K}^b =
    \begin{bmatrix}
        k^1_{1,1} & k^1_{1,2} & k^1_{1,3} & 0 & 0 & 0 & 0 & 0 & 0 \\
        k^1_{2,1} & k^1_{2,2} & k^1_{2,3} & 0 & 0 & 0 & 0 & 0 & 0 \\
        k^1_{3,1} & k^1_{3,2} & k^1_{3,3} & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & k^2_{1,1} & k^2_{1,2} & k^2_{1,3} & 0 & 0 & 0 \\
        0 & 0 & 0 & k^2_{2,1} & k^2_{2,2} & k^2_{2,3} & 0 & 0 & 0 \\
        0 & 0 & 0 & k^2_{3,1} & k^2_{3,2} & k^2_{3,3} & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & k^3_{1,1} & k^3_{1,2} & k^3_{1,3} \\
        0 & 0 & 0 & 0 & 0 & 0 & k^3_{2,1} & k^3_{2,2} & k^3_{2,3} \\
        0 & 0 & 0 & 0 & 0 & 0 & k^3_{3,1} & k^3_{3,2} & k^3_{3,3}
    \end{bmatrix}, \quad
    \mathbf{K}^g =
    \begin{bmatrix}
        K_{1,1} & K_{1,2} & K_{1,3} & 0       & 0 \\ 
        K_{2,1} & K_{2,2} & K_{2,3} & K_{2,4} & 0 \\ 
        K_{3,1} & K_{3,2} & K_{3,3} & K_{3,4} & K_{3,5} \\ 
        0       & K_{4,2} & K_{4,3} & K_{4,4} & K_{4,5} \\ 
        0       & 0       & K_{5,3} & K_{5,4} & K_{5,5} \\
    \end{bmatrix}
\end{equation}

If a traditional finite element code provides $K^b$ on its own $C^0$ basis then one simply performs Bézier extraction on the $C^0$ basis.

# Isogeometric Analysis in MOOSE

## Implementation details

## Limitations

1. While Coreform Flex supports generation of body-fitted or partially-fitted spline meshes, MOOSE currently only supports the use of fully-immersed meshes.
2. While isogeometric analysis encompasses one- and two-dimensional problems, Coreform Flex currently only supports three-dimensional problems, thus no testing has been performed for one- or two-dimensional problems.
3. The current implementation in MOOSE often results in very-poorly conditioned linear systems, thus we recommend using the `lu` preconditioner, which is limited to serial execution only.


# Example: Hydraulic press c-frame stress analysis

This problem is adapted from an undergraduate textbook [!cite](collins_busby_staab_2010) that analyzes the stress in a hydraulic press's main structural component: a c-frame.

## Problem statement

A 13-kN hydraulic press for removing and reinstalling bearings in small-to medium-sized electric motors is to consist of a commercially available cylinder mounted vertically in a C-frame, with dimensions as sketched in Figure P4.32. It is being proposed to use ASTM A-48 (Class 50) gray cast iron for the C-frame material. Predict whether the C-frame can support the maximum load without failure.

## Running the example

### Required software

We provide a self-contained Python script, `cframe_iga.py`, that automates the model setup, mesh generation, conversion to libMesh-compatible formats and export of extraction operators, and execution of the MOOSE simulation.
To run the example, you will need the following software installed:

1. MOOSE, with a built `solid_mechanics` module (using the default `opt` mode).
2. Coreform Cubit (version 2025.10 or later).
3. Coreform Flex (version 2025.10 or later).
4. ParaView (for visualization of results).

Coreform Cubit and Coreform Flex are products released and maintained by Coreform, Inc.
Non-commercial MOOSE users can acquire free "associate" licenses for both products by registering at [Coreform's website](https://coreform.com/products/coreform-cubit/free-meshing-software/).
Funded academic and commercial users should [contact Coreform directly](https://coreform.com/support/contact/) for licensing information.

Additionally, to support CI/CD we have provided preprocessed mesh files and extraction operators in the example directory, so it is not strictly necessary to have Coreform Cubit or Flex installed to run the MOOSE simulation used in the automated test-suite.

### Coreform pipeline execution

```bash
cd ~/projects/moose/modules/solid_mechanics/examples/flex_iga/cframe
python3 cframe_iga.py --degree 2 --mesh-size 0.25 --mesh-mode boundingbox --num-trim-proc 1 --num-moose-proc 1
```

Within the Python script file, see [!ref](cframe_iga), there are unique methods that will generate a uspline on the discretized mesh. 

!listing examples/flex_iga/cframe/cframe_iga.py id=cframe_iga caption=Complete Coreform Cubit file for generating [!ac](IGA) input mesh 

## MOOSE-IGA Simulation

Performing the simulation utilizing the mesh created above does not require much with respect to the MOOSE input, simply 
load the mesh from a file and select utilize the RATIONAL_BERNSTEIN element family as shown in [!ref](moose-iga-input).
Exporting using the VTK format (`vtk = true`) input will output in a format that will capture the higher-order nature 
of the [!ac](IGA) based elements using Paraview visualization. 

!listing examples/flex_iga/cframe/cframe_iga.i id=moose-iga-input caption=Complete input file for running example problem with [!ac](IGA) in MOOSE.

!media solid_mechanics/cframe_iga.png id=moose-iga-vtk caption=Maximum principal stress for "c-frame" example utilizing [!ac](IGA) in MOOSE.
