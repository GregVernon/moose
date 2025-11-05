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
The current implementation in MOOSE is based upon the [!ac](FRM) developed by Coreform Inc., which is one such implementation.

## Mathematic Preliminaries

### Bézier Extraction

A core concept in modern isogeometric analysis is *Bézier extraction* ([!cite](borden2011isogeometric)), which provides a mechanism for representing spline basis functions in terms of standard finite element shape functions.
This allows existing finite element codes, such as MOOSE, to utilize spline basis functions while minimizing significant changes to the underlying codebase.

!alert note
The terminology of *Bézier extraction* comes from the initial development's use of $C^0$ Bernstein polynomials as the underlying basis functions, which are the basis functions used in Bézier curves and surfaces.
However, the exact same technique can also be applied to a spline of any continuity, with $C^{-1}$ basis functions being of particular interest.
The approach can also be applied to other basis function families, an example being the Lagrange polynomials ([!cite](schillinger2016lagrange)) which was coined *Lagrange* extraction.
Rather than provide unique names for each basis function family, the more general term *extraction* is often used.

Consider a quadratic $C^1$ B-spline basis, $N(x)$, defined over three uniformly spaced elements on the interval $[0,3]$ and a corresponding $C^{-1}$ B-spline basis, $B(x)$, defined over the same elements.

!media solid_mechanics/iga/BezierExtraction_BasisFunctions.png
    id=bez-extract-basis
    caption=Quadratic $C^1$ B-spline basis functions (top) and corresponding $C^{-1}$ basis functions. Element boundaries are denoted by vertical black lines.
    style=width:70%;margin-left:auto;margin-right:auto;

The global Bézier extraction operator, $\mathbf{C}$, can be computed by

\begin{equation}
    \label{eqn-bez-ext-op-global}
    \mathbf{C}^g = \left( \frac{ \langle B, N^T \rangle_{ij} }{ \langle B, B^T \rangle_{ij} } \right)^T
\end{equation}

where $\langle \cdot , \cdot \rangle_{ij}$ indicates the element-wise inner product over the domain.
For example:

\begin{equation}
    \label{eqn-elemwise-inner-prod}
    \langle B, N^T \rangle_{ij} =
    \begin{bmatrix}
        \langle B_1, N_1 \rangle & \cdots & \langle B_1, N_5 \rangle \\
        \vdots & \ddots & \vdots \\
        \langle B_7, N_1 \rangle & \cdots & \langle B_7, N_5 \rangle \\
    \end{bmatrix}
\end{equation}

The spline basis functions can then be represented in terms of the Bézier basis functions as:

\begin{equation}
    \label{eqn-bez-ext-compute-spline-basis}
    N(x) = \mathbf{C}^g B(x)
\end{equation}

If the $C^1$ spline coefficients, $n$, are known we can directly compute the $C^{-1}$ (or $C^{0}$) spline coefficients, $b$, by applying the transpose of the Bézier extraction operator:

\begin{equation}
    \label{eqn-bez-ext-compute-coeff}
    b = \left( \mathbf{C}^g \right)^T n
\end{equation}

Because the space of $C^1$ functions are a subset of the space of $C^0$ functions, the global Bézier extraction operator is non-square i.e., it has no inverse.
Therefore if we wish to compute the $C^k$ spline coefficients from the $C^{-1}$ spline coefficients we use the Moore-Penrose inverse, also known as the *psedudoinverse*:

\begin{equation}
    \label{eqn-bez-coeff-pinv}
    n = \left( \mathbf{C}^g \right)^{+} b,
\end{equation}

where $\square^{+}$ denotes the pseudoinverse of $\square$.

The global extraction operator can be also used to perform global assembly:

\begin{equation}
    \label{eqn-bez-extract-global-assembly}
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
    \end{bmatrix}
\end{equation}

\begin{equation}
    \mathbf{C}^g =
    \begin{bmatrix}
        1 & 0 & 0           & 0           & 0 & 0           & 0           & 0 & 0 \\
        0 & 1 & \frac{1}{2} & \frac{1}{2} & 0 & 0           & 0           & 0 & 0 \\
        0 & 0 & \frac{1}{2} & \frac{1}{2} & 1 & \frac{1}{2} & \frac{1}{2} & 0 & 0 \\
        0 & 0 & 0           & 0           & 0 & \frac{1}{2} & \frac{1}{2} & 1 & 0 \\
        0 & 0 & 0           & 0           & 0 & 0           & 0           & 0 & 1 \\
    \end{bmatrix}
\end{equation}

\begin{equation}
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

In practice, the global extraction operator is not formed explicitly.
Instead, element-level extraction operators, $\mathbf{C}^e$, are computed and applied during element-level calculations.
These element-level extraction operators are change-of-basis matrices that map from the local $C^{-1}$ basis to the local spline basis for each element, and are sub-matrices of the global extraction operator.
This allows the use of standard finite element assembly procedures, with only minor modifications to account for the extraction operators during element-level computations.

## Tessellation Extraction

A novel form of extraction implemented by [!ac](FRM) is *tessellation extraction* wherein a linear tessellation is generated on a boundary(e.g., triangle mesh) or on the volume (e.g., tetrahedral mesh) of the domain.
For example, we again consider a quadratic $C^1$ B-spline basis, $N(x)$, defined over three uniformly spaced elements on the interval $[0,3]$ and a corresponding $C^{0}$ tessellation, $\triangle(x)$, defined over the same domain but its own unique elements.

!media solid_mechanics/iga/TessellationExtraction_BasisFunctions.png
    id=tess-extract-basis
    caption=Quadratic $C^1$ B-spline basis functions (top) and corresponding $C^{0}$ linear tessellation's basis functions. Element boundaries are denoted by vertical black lines.
    style=width:70%;margin-left:auto;margin-right:auto;

We can again define an extraction operator between the B-spline basis ($N(x)$) and the tessellation's basis ($\triangle(x)$) as we did with Bézier extraction:

\begin{equation}
    \label{eqn-tess-extract-op}
    \mathbf{C}^g = \left( \frac{ \langle \triangle, N^T \rangle_{ij} }{ \langle \triangle, \triangle^T \rangle_{ij} } \right)^T
\end{equation}

The usefulness of this extraction operator is that it allows for certain computations to occur on the linear tessellation, which is interpolatory, such as boundary condition enforcement, application of load conditions (forcing functions), mechanical-contact force calculations, ray-tracing, computing view factor for radiative heat transfer, etc.
Using the pseudoinverse approach in [!eqref](eqn-bez-coeff-pinv), these values can then be projected into the space of the $C^k$ spline basis functions as demonstrated in [!ref](tess-coeff-project).
This operator can also be used to map variables from the $C^k$ spline onto the linear tessellation, e.g., using a linear tetrahedral mesh as for visualization and mapping variables from the $C^k$ spline onto the visualization mesh.

!media solid_mechanics/iga/TessellationExtraction_CoefficientProjection.png
    id=tess-coeff-project
    caption=In (a) we compute the tessellation coeffients, $\mathrm{t}$, by interpolating a known function (black) with our linear tessellation from [!ref](tess-extract-basis). We compute the spline coefficients, $n$, according to [!eqref](eqn-bez-coeff-pinv). In (c) we the approximation produced by the linear tessellation, $f^{\triangle}(x)$ and by the projection of the tessellation into the $C^k$ spline basis, $f^{N}(x)$, against the known target function approximation, $f(x)$.
    style=width:70%;margin-left:auto;margin-right:auto;

# Isogeometric Analysis in MOOSE

## Implementation details

## Limitations

1. The MOOSE implementation supports body-fitted and fully-immersed spline meshes, and *should* support partially-immersed spline meshes however, as Coreform Flex does not currently support export of partially-fitted meshes to MOOSE, this capability has not been tested.
2. While isogeometric analysis encompasses one- and two-dimensional problems, Coreform Flex currently only supports three-dimensional problems, thus no testing has been performed for one- or two-dimensional problems.
3. When working with immersed meshes, the current implementation in MOOSE often results in very-poorly conditioned linear systems.  Thus we recommend using the `LU` preconditioner for immersed problems, which is limited to serial execution only (see discussion [here](executioners/Steady.md#petsc-options)).

## Examples

- [Hydraulic Press C-Frame](solid_mechanics/examples/cframe_iga.md)