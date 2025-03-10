import os
import sys
import argparse
import pathlib
import subprocess

path_to_this_script = os.path.dirname( os.path.realpath( __file__ ) )

def main( args ):
    run_flex( args )
    do_interop()

def run_flex( args ):
    flex = import_flex()
    flex.cmd( 'reset' )
    flex.cmd( f'root_dir "{path_to_this_script}"' )
    
    flex.cmd(f'import "{os.path.join( path_to_this_script, "cframe.stp" )}"' )

    flex.cmd( 'name part 1 "cframe"' )
    flex.cmd( 'set hold_surface add surfaces [74]' )
    flex.cmd( 'set load_surface add surfaces [97]' )


    degree = args.degree
    continuity = degree - 1
    mesh_size = args.mesh_size
    flex.cmd(f'mesh mesh_1 rectilinear degree {degree} continuity {continuity} element_size [{mesh_size} {mesh_size} {mesh_size}] padding [{degree} {degree} {degree}]' )
    flex.cmd( 'part 1 mesh 1' )
    flex.cmd( 'part 1 volume_box object_aligned extend_percent [1 1 1]' )

    flex.cmd( f'coreform_iga_version "{flex.version_short()}"' )
    flex.cmd( 'label cframe_failure' )

    flex.cmd( 'materials cast_iron new' )
    flex.cmd( 'materials cast_iron mass_density 1e-6' )
    flex.cmd( 'materials cast_iron elastic youngs_modulus 24e6' )
    flex.cmd( 'materials cast_iron elastic poissons_ratio 0.29' )

    flex.cmd( 'flex_models flex_inf new' )
    flex.cmd( 'flex_models flex_inf database_name geom' )
    flex.cmd( 'flex_models flex_inf small_cell_volume_ratio 0.2' )

    flex.cmd( 'flex_models flex_inf parts cframe_part new' )
    flex.cmd( 'flex_models flex_inf parts cframe_part part cframe' )
    flex.cmd( 'flex_models flex_inf parts cframe_part material cast_iron' )
    flex.cmd( 'flex_models flex_inf parts cframe_part material_model elastic' )

    flex.cmd( 'functions constant_1 new' )
    flex.cmd( 'functions constant_1 constant value 1.0' )

    flex.cmd( 'functions linear_ramp new' )
    flex.cmd( 'functions linear_ramp piecewise_linear abscissa [0.0 1.0]' )
    flex.cmd( 'functions linear_ramp piecewise_linear ordinate [0.0 1.0]' )

    flex.cmd( 'intervals apply_load new' )
    flex.cmd( 'intervals apply_load start_time 0.0' )
    flex.cmd( 'intervals apply_load stop_time 1.0' )
    flex.cmd( 'intervals apply_load time_increment 1.0' )

    flex.cmd( 'intervals output_interval new' )
    flex.cmd( 'intervals output_interval use_start_stop_from_interval apply_load' )
    flex.cmd( 'intervals output_interval step_increment 1' )

    flex.cmd( 'time_steppers linear_statics new' )
    flex.cmd( 'time_steppers linear_statics linear linear_equation_solver multi_frontal' )

    flex.cmd( 'linear_equation_solvers multi_frontal new' )
    flex.cmd( 'linear_equation_solvers multi_frontal direct multi_frontal use_diagonal_scaling true ' )

    flex.cmd( 'solid_mechanics_definitions boundary_conditions hold_bottom new' )
    flex.cmd( 'solid_mechanics_definitions boundary_conditions hold_bottom displacement components 0 x' )
    flex.cmd( 'solid_mechanics_definitions boundary_conditions hold_bottom displacement components 1 y' )
    flex.cmd( 'solid_mechanics_definitions boundary_conditions hold_bottom displacement components 2 z' )
    flex.cmd( 'solid_mechanics_definitions boundary_conditions hold_bottom displacement function constant_1' )
    flex.cmd( 'solid_mechanics_definitions boundary_conditions hold_bottom displacement scale_factor 0.0' )
    flex.cmd( 'solid_mechanics_definitions boundary_conditions hold_bottom set hold_surface' )

    flex.cmd( 'solid_mechanics_definitions load_conditions push_top new' )
    flex.cmd( 'solid_mechanics_definitions load_conditions push_top surface_pressure scale_factor 2307.86806' )  # Scale for a total load of 3000 lbs
    flex.cmd( 'solid_mechanics_definitions load_conditions push_top surface_pressure function linear_ramp' )
    flex.cmd( 'solid_mechanics_definitions load_conditions push_top follower false' )
    flex.cmd( 'solid_mechanics_definitions load_conditions push_top set load_surface' )

    flex.cmd( 'solid_mechanics_definitions outputs field_results new' )
    flex.cmd( 'solid_mechanics_definitions outputs field_results field database_name results' )
    flex.cmd( 'solid_mechanics_definitions outputs field_results field interval output_interval' )
    flex.cmd( 'solid_mechanics_definitions outputs field_results field part cframe' )
    flex.cmd( 'solid_mechanics_definitions outputs field_results field variables displacement 0 x' )
    flex.cmd( 'solid_mechanics_definitions outputs field_results field variables displacement 1 y' )
    flex.cmd( 'solid_mechanics_definitions outputs field_results field variables displacement 2 z' )
    flex.cmd( 'solid_mechanics_definitions outputs field_results field variables stress 0 all' )
    flex.cmd( 'solid_mechanics_definitions outputs field_results field element_variable_output_strategy interpolate ' )
    flex.cmd( 'solid_mechanics_definitions outputs field_results field include_integration_point_output false' )

    flex.cmd( 'solid_mechanics_definitions outputs probe_results new' )
    flex.cmd( 'solid_mechanics_definitions outputs probe_results history interval output_interval' )
    flex.cmd( 'solid_mechanics_definitions outputs probe_results history probe_variables 0 stress_probe' )
    flex.cmd( 'solid_mechanics_definitions outputs probe_results history probe_variables 1 load_reaction_force' )

    flex.cmd( 'solid_mechanics_definitions probes stress_probe new' )
    flex.cmd( 'solid_mechanics_definitions probes stress_probe field single_point location [0 -1.5 -4.25]' )
    flex.cmd( 'solid_mechanics_definitions probes stress_probe field location_configuration reference' )
    flex.cmd( 'solid_mechanics_definitions probes stress_probe field field_variable_configuration reference' )
    flex.cmd( 'solid_mechanics_definitions probes stress_probe field variables stress 0 max_principal' )

    flex.cmd( 'solid_mechanics_definitions probes load_reaction_force new' )
    flex.cmd( 'solid_mechanics_definitions probes load_reaction_force integrated_surface_quantity variables reaction_force 0 x' )
    flex.cmd( 'solid_mechanics_definitions probes load_reaction_force integrated_surface_quantity variables reaction_force 1 y' )
    flex.cmd( 'solid_mechanics_definitions probes load_reaction_force integrated_surface_quantity variables reaction_force 2 z' )
    flex.cmd( 'solid_mechanics_definitions probes load_reaction_force integrated_surface_quantity use_set_from_load_condition push_top' )
    flex.cmd( 'solid_mechanics_definitions probes load_reaction_force integrated_surface_quantity part cframe' )

    flex.cmd( 'procedures apply_load_procedure new' )
    flex.cmd( 'procedures apply_load_procedure solid_mechanics flex_model flex_inf' )
    flex.cmd( 'procedures apply_load_procedure solid_mechanics interval apply_load' )
    flex.cmd( 'procedures apply_load_procedure solid_mechanics time_stepping_method linear_statics' )
    flex.cmd( 'procedures apply_load_procedure solid_mechanics outputs 0 field_results' )
    flex.cmd( 'procedures apply_load_procedure solid_mechanics outputs 1 probe_results' )
    flex.cmd( 'procedures apply_load_procedure solid_mechanics load_conditions 0 push_top' )
    flex.cmd( 'procedures apply_load_procedure solid_mechanics boundary_conditions 0 hold_bottom' )

    flex.cmd( 'job trimmed_cframe new' )
    flex.cmd( 'job trimmed_cframe trim processor_count 1' )
    flex.cmd( 'job trimmed_cframe trim trim_parts [cframe]' )
    flex.cmd( 'job trimmed_cframe submit' )
    flex.cmd( 'job trimmed_cframe wait' )

def do_interop():
    coreform_trim = get_coreform_paths()["trim"]
    command = f"{coreform_trim} --ii jobs/trimmed_cframe --io trimmed_cframe_moose"
    subprocess.check_call( command, shell=True )

def import_flex( verbose=False ):
    coreform_paths = get_coreform_paths()
    sys.path.append( os.fspath( coreform_paths["flex_path"] ) )
    from coreform import flex
    flex.init( verbose=verbose, gui=False )
    return flex

def get_coreform_paths():
    coreform_paths = {}
    if "win" in sys.platform:
        coreform_paths["flex"] =         pathlib.Path( r"C:\Program Files\Coreform Flex 2025.3\bin\coreform_flex.exe" )
        coreform_paths["flex_path"] =    pathlib.Path( r"C:\Program Files\Coreform Flex 2025.3\bin" )
        coreform_paths["trim"] =         pathlib.Path( r"C:\Program Files\Coreform Flex 2025.3\bin\coreform_trim.bat" )
        coreform_paths["trim_path"] =    pathlib.Path( r"C:\Program Files\Coreform Flex 2025.3\bin" )
    elif "lin" in sys.platform:
        coreform_paths["flex"] =         pathlib.Path( "/opt/Coreform-Flex-2025.3/bin/coreform_flex" )
        coreform_paths["flex_path"] =    pathlib.Path( "/opt/Coreform-Flex-2025.3/bin" )
        coreform_paths["trim"] =         pathlib.Path( "/opt/Coreform-Flex-2025.3/bin/coreform_trim" )
        coreform_paths["trim_path"] =    pathlib.Path( "/opt/Coreform-Flex-2025.3/bin" )
    return coreform_paths

def script_arguments():
    parser = argparse.ArgumentParser(description="Run the Coreform pipeline.")
    parser.add_argument( "--degree", dest="degree", type=int, default=2 )
    parser.add_argument( "--mesh-size", dest="mesh_size", type=float, default=0.25 )
    return parser.parse_args()

if __name__ == "__main__":
    args = script_arguments()
    print( args )
    main( args )