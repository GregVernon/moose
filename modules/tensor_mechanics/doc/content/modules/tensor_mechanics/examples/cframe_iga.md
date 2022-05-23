# Isogeometric Analysis in MOOSE

This example illustrates using [!ac](IGA) within MOOSE framework to perform a simulation. 
This example simulates loads applied to a "c-frame" to determine the maximum principal stress.

## Creating IGA Mesh

To create the mesh file included in this example a Coreform Cubit license is needed.
Coreform Cubit is a product released and maintained by Coreform, LLC. 
A free to use [Cubit Learn license](https://coreform.com/products/coreform-cubit/free-meshing-software/) can be acquired.

!alert! note title=Mesh Generation with Cubit
The following is not required to run the example, but is required to generate the input mesh that is included in the example. 
To execute the Cubit journal file in batch from the command line use the following command:

```
coreform_cubit -nographics -batch cframe_build.jou
```
!alert-end!

Within the journal file, see [!ref](cframe_iga_jou), there are unique commands that will generate a U-spline on the discretized mesh. 

- `set uspline volume all degree 2 continuity 1`
    - Defines the properties for a U-spline that will be built on the specified volumes
    - Currently MOOSE only supports U-splines of degree 1 or 2.
    - The maximum continuity level for a U-spline is (degree - 1)
- `build uspline volume all as 1`
    - Builds the U-spline basis on the specified volumes
- `fit uspline 1`
    - Fits the U-spline to the underlying geometry using Bezier projection.

!listing examples/cframe_iga/build_cframe_iga.jou id=cframe_iga_jou caption=Complete Coreform Cubit file for generating [!ac](IGA) input mesh 

## MOOSE-IGA Simulation

Performing the simulation utilizing the mesh created above does not require much with respect to the MOOSE input, simply load the mesh from a file and select utilize the RATIONAL_BERNSTEIN element family as shown in [!ref](moose-iga-input).
Exporting using the VTK format (`vtk = true`) will output in a format that will capture the higher-order nature of the [!ac](IGA) based elements using ParaView visualization. 

!listing examples/cframe_iga/build_cframe_iga.i id=moose-iga-input caption=Complete input file for running example problem with [!ac](IGA) in MOOSE.

!media tensor_mechanics/cframe_iga.png id=moose-iga-vtk caption=Maximum principal stress for "c-frame" example utilizing [!ac](IGA) in MOOSE.
