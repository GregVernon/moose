

# Example: Hydraulic press C-frame stress analysis

This problem is adapted from an undergraduate textbook [!cite](collins_busby_staab_2010) that analyzes the stress in a hydraulic press's main structural component: a c-frame.

## Problem statement

A 3000-lbf hydraulic press for removing and reinstalling bearings in small-to medium-sized electric motors is to consist of a commercially available cylinder mounted vertically in a C-frame.
It is being proposed to use ASTM A-48 (Class 50) gray cast iron for the C-frame material.
Predict whether the C-frame can support the maximum load without failure.
-- *Adapted with permission from [!cite](collins_busby_staab_2010)*

The dimensions of the C-frame are showin in [!ref](cframe-dimside), [!ref](cframe-dimsection), and [!ref](cframe-dimconditionsurface).

!media solid_mechanics/iga/CFrame_DimSide.png
    id=cframe-dimside
    caption=A sideview of the C-frame with dimensional information.
    style=width:70%;margin-left:auto;margin-right:auto;

!media solid_mechanics/iga/CFrame_DimSection.png
    id=cframe-dimsection
    caption=A cross-sectional view of the C-frame with dimensional information.
    style=width:70%;margin-left:auto;margin-right:auto;

!media solid_mechanics/iga/CFrame_DimConditionSurface.png
    id=cframe-dimconditionsurface
    caption=A detailed view of the surface upon which the pressure load condition will be applied. An equivalent surface will have a fixed-displacement condition.
    style=width:70%;margin-left:auto;margin-right:auto;

!table id=table-material-pros caption=Material properties for ASTM A-48 (Class 50) gray cast iron.
| Property | Value | Units |
| - | - | - |
| Young's modulus           | $24 \times 10^6$ | $\mathrm{psi}$  ( i.e., $\frac{\mathrm{lbf}}{\mathrm{in}^2}$ ) |
| Poisson's ratio           | $0.29$           | $\mathrm{(dimensionless)}$ |
| Ultimate tensile strength | $50 \times 10^3$ | $\mathrm{psi}$  ( i.e., $\frac{\mathrm{lbf}}{\mathrm{in}^2}$ ) |


## Hand-calculation

Cast-iron is considered to have little to no ductility, thus we assume brittle failure theory – thus
determining whether ultimate tensile strength (maximum principal stress) exceeds the ultimate
tensile strength is the goal of this analysis, determining the factor of safety, etc.
Based on our general understanding of the problem, we predict that the maximum tensile stress
occurs on the inside of the C-Frame as shown in [!ref](cframe-expectedmaxstresslocation).

!media solid_mechanics/iga/CFrame_ExpectedMaxStressLocation.png
    id=cframe-expectedmaxstresslocation
    caption=The location at which we intuit the maximum tensile stress will occur, based on our problem definition, is denoted by the yellow sphere.
    style=width:70%;margin-left:auto;margin-right:auto;

At this location, the applied load exerts both a normal force and a bending moment.
Because of the long moment arm, we expect that the moment may be the main participant in the resultant
stresses, so we focus our attention on understanding the bending moment in an initially curved
beam.

!alert! tip prefix=False title=Hand calculation
> \begin{equation}
>   \sigma_{i} = \frac{M c_{i}}{e A r_{i}}, \quad e = r_{c} - \frac{A}{\int \frac{dA}{r}}
> \end{equation}
>
> \begin{equation}
>   \begin{split}
>       \int \frac{dA}{r} &= b_1 \ln\left( \frac{r_{i} h_1}{r_{i}} \right) + b_2 \ln\left( \frac{r_{o}}{r_{i} + h_1} \right) \\
>       \int \frac{dA}{r} &= 1 \ln\left( \frac{1.5 + 0.4}{1.5} \right) + 0.4 \ln\left( \frac{2.6}{1.5 + 0.4} \right) \\
>       \int \frac{dA}{r} &= 0.361852 \ \mathrm{in}
>   \end{split}
> \end{equation}
>
> \begin{equation}
>   A = 0.4 + 0.28 = 0.68 \ \mathrm{in}^2
> \end{equation}
>
> \begin{equation}
>   r_{c} = \frac{0.4 \cdot 1.7 + 0.28 \cdot 2.25}{0.68} = 1.92647 \ \mathrm{in}
> \end{equation}
>
> \begin{equation}
>   e = 0.0472487 \ \mathrm{in}
> \end{equation}
>
> \begin{equation}
>   r_{n} = r_{c} - e = 1.87925 \ \mathrm{in}
> \end{equation}
>
> \begin{equation}
>   c_{i} = r_{n} - r_{i} = 0.37925 \ \mathrm{in}
> \end{equation}
>
> \begin{equation}
>   \begin{split}
>       M &= 3000 \ \mathrm{lbf} \cdot( 3.5 \ \mathrm{in} + r_{c}) \\
>         &= 16279.4 \ \mathrm{lbf} \cdot \mathrm{in}
>   \end{split}
> \end{equation}
>
> \begin{equation}
>   \sigma_{i} \approx 128 \times 10^3 \ \mathrm{psi} \\
> \end{equation}
>
> Since $\sigma_i \gg \sigma_{\mathrm{UTS}}$, we don't bother considering the normal load as we already can say, with confidence, that this part is likely to experience brittle failure.
> For completeness, however, the normal stress due to the applied load applies an additional tensile stress of $\sigma \approx 4.4 \times 10^3 \ \mathrm{psi}$.
> Thus, we might expect our MOOSE simulation to predict a maximum principal stress of $\sigma_{i} \approx 132 \times 10^3 \ \mathrm{psi}$.
!alert-end!

## Running the example

### Required software

We provide a self-contained Python script, `cframe_iga.py` (see [!ref](cframe_iga)), that automates the model setup, mesh generation, conversion to libMesh-compatible formats and export of extraction operators, and execution of the MOOSE simulation.
To run the example, you will need the following software installed:

1. MOOSE, with a built `solid_mechanics` module (using the default `opt` mode).
2. Coreform Cubit (version 2025.10 or later).
3. Coreform IGA with `build_cf.py`, `coreform_iga_mesh`, and `exodus_interop`.
4. ParaView (for visualization of results).

Coreform Cubit and Coreform IGA are products released and maintained by Coreform, Inc.
Non-commercial MOOSE users can acquire free "associate" licenses for both products by registering at [Coreform's website](https://coreform.com/products/coreform-cubit/free-meshing-software/).
Funded academic and commercial users should [contact Coreform directly](https://coreform.com/support/contact/) for licensing information.

Additionally, to support CI/CD we have provided preprocessed mesh files and extraction operators in the example directory, so it is not strictly necessary to have Coreform Cubit or Coreform IGA installed to run the MOOSE simulation used in the automated test-suite.

### Coreform pipeline execution

```bash
cd ~/projects/moose/modules/solid_mechanics/examples/flex_iga/cframe
python3 cframe_iga.py
```

If Coreform is installed in a non-default location, provide the Coreform IGA `bin` directory and the Cubit Python module directory explicitly:

```bash
python3 cframe_iga.py --bin-dir /path/to/Coreform-IGA/bin --cubit-python-module-path /path/to/Coreform-Cubit/bin
```

The Python script performs five main tasks:

1. `run_cubit()`

    - Setup the CAD model, assign the block and sidesets, and export a Coreform `.cf` file from Coreform Cubit.

2. `run_build_cf()`

    - Convert the Cubit-exported `.cf` file into the meshing-ready Coreform IGA `.cf` file, including the rectilinear mesh frame and trimming options.

3. `run_iga_mesh()`

    - Run `coreform_iga_mesh` to create the generic SQL mesh database.

4. `run_interop()`

    - Run `exodus_interop` to create the Exodus mesh and HDF5 extraction-operator sidecar used by MOOSE.

5. `run_moose()`

    - Setup and run the MOOSE simulation using the generated mesh and extraction operators.

!listing examples/flex_iga/cframe/cframe_iga.py id=cframe_iga caption=Complete Python script for setting up and running the "c-frame" example problem with [!ac](IGA) in MOOSE.

## Isogeometric Model Setup

The refreshed `cframe_iga.py` script currently uses the immersed Coreform IGA workflow. Older body-fitted and partially-immersed Flex workflows are not part of this Exodus export path.

### Body-fitted mesh

!media solid_mechanics/iga/CFrame_BodyfitMesh.png 
    id=cframe-mesh-bodyfit 
    caption=Bodyfit mesh generated in Coreform Cubit for the C-frame. Note the significant defeaturing.
    style=width:70%;margin-left:auto;margin-right:auto;

### Partially-fitted mesh

!media solid_mechanics/iga/CFrame_FlexFitMesh.png 
    id=cframe-mesh-flexfit 
    caption=A partially-immersed mesh that conforms to the overall shape of the C-frame while immersing small, complex-to-mesh, features (i.e., flex-fitted).
    style=width:70%;margin-left:auto;margin-right:auto;

### Immersed mesh

!media solid_mechanics/iga/CFrame_BoundingBoxMesh.png 
    id=cframe-mesh-boundingbox 
    caption=Immersed mesh based on a bounding-box approach generated in Coreform Flex for the C-frame.
    style=width:70%;margin-left:auto;margin-right:auto;

## MOOSE-IGA Simulation

The current implementation of [!ac](IGA) in MOOSE expects the mesh and extraction operators to be provided from an external source, such as Coreform Flex.
These files are then specified in the MOOSE input file using the `[Mesh]` block, as shown in [!ref](moose-iga-input).
Because the [!ac](IGA) implementation in MOOSE relies on the tessellated extraction approach the primal variables `disp_x`, `disp_y`, and `disp_z` must use first-order Lagrange basis functions.
Similarly the `AuxVariables` for stress post-processing must also use first-order monomial basis functions.
In addition to visual interrogation of the output results, shown in [!ref](moose-iga-vtk), we define a `PointValue` probe, located at the anticipated maximum tensile stress location, in MOOSE to attempt to extract the maximum-value of the maximum principal stress (i.e., the maximum tensile stress).
The reported values of these probes is reported in [!ref](table-probe-results).

!table 
    id=table-probe-results 
    caption=Reported values of maximum tensile stress from MOOSE probes for a quadratic immersed-spline mesh at different element sizes
    style=width:70%;margin-left:auto;margin-right:auto;
| Element Size | Value | Units | % Deviation from hand-calculation |
| - | - | - | - |
| $0.5000$ | $104 \times 10^3$ | $\mathrm{psi}$ | $-21\%$ |
| $0.2500$ | $129 \times 10^3$ | $\mathrm{psi}$ | $-3\%$ |
| $0.1250$ | $142 \times 10^3$ | $\mathrm{psi}$ | $7\%$ |
| $0.0625$ | $141 \times 10^3$ | $\mathrm{psi}$ | $6\%$ |

!listing examples/flex_iga/cframe/cframe_iga.i 
    id=moose-iga-input 
    caption=Complete input file for running example problem with [!ac](IGA) in MOOSE.

!media solid_mechanics/iga/cframe_iga_results.png 
    id=moose-iga-vtk 
    caption=Maximum principal stress on the C-Frame. This figure was produced with the execution options: `--degree 2 --mesh-size 0.0625`.
    style=width:70%;margin-left:auto;margin-right:auto;
