import os
import sys
import math
import argparse
from pathlib import Path
import subprocess
from coreform_utils import import_cubit, import_flex, get_coreform_paths

path_to_this_script = os.path.dirname( os.path.realpath( __file__ ) )

def main( args ):
    run_cubit( args )
    run_flex( args )
    do_interop( args )
    run_moose( args )

def run_cubit( args ):
    ## This routine verified to run with Coreform Cubit 2025.10
    cubit = import_cubit()
    cubit.cmd( 'reset' )
    ## Import geometry
    cubit.cmd( f'import step "{os.path.join( path_to_this_script, "c-frame.step" )}" noheal' )
    if args.mesh_mode == "boundingbox":
        ## Let Coreform Flex handle meshing...
        ### Assign sets for boundary conditions
        #### Partition surfaces to create sets for boundary and load conditions
        cubit.cmd( f'create vertex on curve 12 73  distance {1.575 + 0.025} from surface 74' )
        cubit.cmd( f'create vertex on curve 17 78  distance {1.575 + 0.025} from surface 72' )
        cubit.cmd( 'split surface 63  across location vertex 117  location vertex 118' )
        cubit.cmd( 'split surface 97  across location vertex 119  location vertex 120' )
        cubit.cmd( 'delete vertex all' )
        #### Make set assignments
        cubit.cmd( 'block 1 volume 1' )
        cubit.cmd( 'block 1 name "cframe"' )
        cubit.cmd( 'sideset 1 surface 102' )
        cubit.cmd( 'sideset 1 name "load_surface"' )
        cubit.cmd( 'sideset 2 surface 103' )
        cubit.cmd( 'sideset 2 name "hold_surface"' )
    else:
        ## Mesh according to user input
        if args.mesh_mode == "bodyfit":
            ### Defeature for body-fitted meshing
            #### Remove blend surfaces
            S = cubit.get_blend_surfaces( (1,) ) # Find blend surfaces in volume 1
            cubit.cmd( f'remove surface {cubit.get_id_string( S )} extend' )
            ### Assign sets for boundary conditions
            #### Partition surfaces to create sets for boundary and load conditions
            cubit.cmd( f'create vertex on curve 12 74  distance {1.575 + 0.025} from surface 74' )
            cubit.cmd( f'create vertex on curve 17 79  distance {1.575 + 0.025} from surface 72' )
            cubit.cmd( 'split surface 63  across location vertex 117  location vertex 118' )
            cubit.cmd( 'split surface 97  across location vertex 119  location vertex 120' )
            cubit.cmd( 'delete vertex all' )
            #### Make set assignments
            cubit.cmd( 'block 1 volume 1' )
            cubit.cmd( 'block 1 name "cframe"' )
            cubit.cmd( 'sideset 1 surface 101' )
            cubit.cmd( 'sideset 1 name "load_surface"' )
            cubit.cmd( 'sideset 2 surface 103' )
            cubit.cmd( 'sideset 2 name "hold_surface"' )
            ### Partition for body-fitted meshing
            cubit.cmd( 'webcut volume all with plane from surface 92' )
            cubit.cmd( 'webcut volume all with plane normal to curve 219  close_to vertex 121' )
            cubit.cmd( 'webcut volume all with plane normal to curve 219  close_to vertex 10' )
            cubit.cmd( 'webcut volume all with plane normal to curve 15  fraction .5 from start' )
            cubit.cmd( 'webcut volume all with plane normal to curve 150  fraction .5 from start' )
            cubit.cmd( 'webcut volume all with plane normal to curve 382  fraction .5 from start' )
            cubit.cmd( 'webcut volume all with sheet extended from surface 134 131 182 167 130 146' )
            ### Enforce mesh continuity across partitions
            cubit.cmd( 'imprint volume all' )
            cubit.cmd( 'merge volume all' )
            ### Assign mesh schemes and generate mesh
            cubit.cmd( f'volume all size {args.mesh_size}' )
            cubit.cmd( "mesh volume all" )
        elif args.mesh_mode == "flexfit":
            ### Assign sets for boundary conditions
            #### Partition surfaces to create sets for boundary and load conditions
            cubit.cmd( f'create vertex on curve 12 73  distance {1.575 + 0.025} from surface 74' )
            cubit.cmd( f'create vertex on curve 17 78  distance {1.575 + 0.025} from surface 72' )
            cubit.cmd( 'split surface 63  across location vertex 117  location vertex 118' )
            cubit.cmd( 'split surface 97  across location vertex 119  location vertex 120' )
            cubit.cmd( 'delete vertex all' )
            #### Make set assignments
            cubit.cmd( 'block 1 volume 1' )
            cubit.cmd( 'block 1 name "cframe"' )
            cubit.cmd( 'sideset 1 surface 102' )
            cubit.cmd( 'sideset 1 name "load_surface"' )
            cubit.cmd( 'sideset 2 surface 103' )
            cubit.cmd( 'sideset 2 name "hold_surface"' )
            ### Create simplified geometry for "flex-fitted" meshing
            cubit.cmd( 'volume 1 copy' )
            #### Remove blend surfaces
            S = cubit.get_blend_surfaces( (2,) ) # Find blend surfaces in volume 2
            cubit.cmd( f'remove surface {cubit.get_id_string( S )} extend' )
            #### Remove remaining small features
            cubit.cmd( f'remove surface 165 167 171 173 188 189 190 198 199 200 201 202 204 205 extend' )
            ### Assign volume to a mesh block
            cubit.cmd( 'block 2 volume 2' )
            cubit.cmd( 'block 2 name "cframe_flexmesh"' )
            ### Assign mesh schemes and generate mesh
            cubit.cmd( f'volume 2 size {args.mesh_size}' )
            cubit.cmd( 'curve 312 307 233 229 317 353 301 375 interval same' )
            cubit.cmd( 'curve 310 248 445 446 interval same' )
            cubit.cmd( 'volume 2 redistribute nodes off' )
            cubit.cmd( 'volume 2 autosmooth target on  fixed imprints off  smart smooth off' )
            cubit.cmd( 'volume 2 scheme Sweep source surface 180 target surface 178 sweep transform least squares' )
            cubit.cmd( 'mesh volume 2' )
    ## Save Coreform Cubit file for potential debugging
    cubit.cmd( 'save cub5 "cframe.cub5" overwrite' )
    ## Export Coreform Flex file
    cubit.cmd( 'export coreform "cframe_geom.cf" overwrite' )

def run_flex( args ):
    flex = import_flex()
    flex.cmd( 'reset' )
    flex.cmd( f'root_dir "{path_to_this_script}"' )

    flex.cmd(f'open "cframe_geom.cf"' )

    mesh_mode = args.mesh_mode
    degree = args.degree
    continuity = degree - 1
    if mesh_mode == "bodyfit":
        flex.cmd( f'mesh mesh_1 mesh_from_cf degree {degree} continuity {continuity}' )
        flex.cmd( 'part 1 mesh 1' )
    elif mesh_mode == "flexfit":
        flex.cmd( f'mesh mesh_1 mesh_from_part part cframe_flexmesh degree {degree} continuity {continuity}' )
        flex.cmd( 'part 1 mesh 1' )
    elif mesh_mode == "boundingbox":
        mesh_size = args.mesh_size
        flex.cmd(f'mesh mesh_1 rectilinear degree {degree} continuity {continuity} element_size [{mesh_size} {mesh_size} {mesh_size}] padding [{degree} {degree} {degree}]' )
        flex.cmd( 'part 1 mesh 1' )
        flex.cmd( 'part 1 volume_box axis_aligned' )

    flex.cmd( f'coreform_iga_version "{flex.version_short()}"' )
    flex.cmd( 'label flex_cframe' )

    flex.cmd( 'flex_models flex_inf new' )
    flex.cmd( 'flex_models flex_inf database_name geom' )
    flex.cmd( f'flex_models flex_inf small_cell_volume_ratio {args.small_cell_volume_ratio}' )

    flex.cmd( 'flex_models flex_inf parts cframe_part new' )
    flex.cmd( 'flex_models flex_inf parts cframe_part part cframe' )

    flex.cmd( 'solid_mechanics_definitions boundary_conditions hold_bottom new' )
    flex.cmd( 'solid_mechanics_definitions boundary_conditions hold_bottom set hold_surface' )

    flex.cmd( 'solid_mechanics_definitions load_conditions push_top new' )
    flex.cmd( 'solid_mechanics_definitions load_conditions push_top set load_surface' )

    flex.cmd( 'procedures apply_load_procedure new' )
    flex.cmd( 'procedures apply_load_procedure solid_mechanics flex_model flex_inf' )
    flex.cmd( 'procedures apply_load_procedure solid_mechanics load_conditions 0 push_top' )
    flex.cmd( 'procedures apply_load_procedure solid_mechanics boundary_conditions 0 hold_bottom' )

    flex.cmd( 'save "cframe.cf"' )

def do_interop( args ):
    mpiexec = get_coreform_paths()["mpiexec"]
    coreform_trim = get_coreform_paths()["trim"]
    command = f"{mpiexec} -n {args.num_trim_proc} {coreform_trim} --ii cframe.cf --io trimmed_cframe_moose --epic"
    subprocess.check_call( command, shell=True )

def run_moose( args ):
    moose_executable = Path( f"{ os.path.join( path_to_this_script, '../../../solid_mechanics-opt') }" ).resolve()
    input_file = os.path.join( path_to_this_script, "cframe_iga.i" )
    command = f"mpiexec -n {args.num_moose_proc} {moose_executable} -i {input_file}"
    subprocess.check_call( command, shell=True )

def import_flex( verbose=False ):
    coreform_paths = get_coreform_paths()
    sys.path.append( os.fspath( coreform_paths["flex_path"] ) )
    from coreform import flex
    flex.init( verbose=verbose, gui=False )
    return flex

def script_arguments():
    parser = argparse.ArgumentParser(description="Run the Coreform pipeline.")
    parser.add_argument( "--degree", dest="degree", type=int, default=1 )
    parser.add_argument( "--mesh-size", dest="mesh_size", type=float, default=0.25 )
    parser.add_argument( "--mesh-mode", dest="mesh_mode", choices=["bodyfit", "flexfit", "boundingbox"], default="boundingbox" )
    parser.add_argument( "--small-cell-volume-ratio", dest="small_cell_volume_ratio", type=float, default=0.2 )
    parser.add_argument( "--num-trim-proc", dest="num_trim_proc", type=int, default=1 )
    parser.add_argument( "--num-moose-proc", dest="num_moose_proc", type=int, default=1 )
    return parser.parse_args()

if __name__ == "__main__":
    args = script_arguments()
    ## Validate arguments against current limitations
    if args.mesh_mode == "flexfit":
        raise ValueError( f"Currently only 'bodyfit' and 'boundingbox' mesh modes are supported by Coreform Flex Interop. You provided: {args.mesh_mode}" )
    if args.num_trim_proc != 1:
        raise ValueError( f"Coreform Flex currently only supports serial processing (1 CPU) for MOOSE simulations. You provided: {args.num_trim_proc}" )
    if ( args.mesh_mode != "bodyfit" ) and ( args.num_moose_proc != 1 ):
        raise ValueError( f"The current implementation in MOOSE for trimmed meshes only supports LU linear solvers, which is limited to serial processing (1 CPU). You provided: {args.num_moose_proc}" )
    main( args )