[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
   [igafile]
       type = FileMeshGenerator
       file = 'trimmed_cframe_moose.exo'
       constraint_matrix = 'trimmed_cframe_moose.h5'
       constraint_preconditioning = 1.0
   []
[]

[Variables]
  [disp_x]
    order = FIRST
    family = LAGRANGE
  []
  [disp_y]
    order = FIRST
    family = LAGRANGE
  []
  [disp_z]
    order = FIRST
    family = LAGRANGE
  []
[]

[Physics]
  [SolidMechanics]
    [QuasiStatic]
      [./all]
        strain = SMALL
        # add_variables = true
      [../]
    [../]
  [../]
[]

[AuxVariables]
    [von_mises]
       # Dependent variable used to visualize the von Mises stress
       order = FIRST
       family = MONOMIAL
    []
    [max_princ]
       # Dependent variable used to visualize the maximum principal (max-tensile) stress
       order = FIRST
       family = MONOMIAL
    []
[]

[AuxKernels]
  [von_mises_kernel]
    # Calculates the von Mises stress and assigns it to von_mises
    type = RankTwoScalarAux
    variable = von_mises
    rank_two_tensor = stress
    scalar_type = VonMisesStress
  []
  [MaxPrin]
    type = RankTwoScalarAux
    variable = max_princ
    rank_two_tensor = stress
    scalar_type = MaxPrincipal
  []
[]

[BCs]
  [Pressure]
    [load]
      # Applies the pressure
      boundary = 'load_surface'
      factor = 2000 # psi
    []
  []
  [anchor_x]
    # Anchors the bottom against deformation in the x-direction
    type = PenaltyDirichletBC
    variable = disp_x
    boundary = 'hold_surface'
    value = 0.0
    penalty = 24e9
  []
  [anchor_y]
    # Anchors the bottom against deformation in the y-direction
    type = PenaltyDirichletBC
    variable = disp_y
    boundary = 'hold_surface'
    value = 0.0
    penalty = 24e9
  []
  [anchor_z]
    #Anchors the bottom against deformation in the z-direction
    type = PenaltyDirichletBC
    variable = disp_z
    boundary = 'hold_surface'
    value = 0.0
    penalty = 24e9
  []
[]

[Materials]
  [elasticity_tensor_castiron]
    # Creates the elasticity tensor using cast-iron parameters
    youngs_modulus = 24e6 #psi
    poissons_ratio = 0.33
    type = ComputeIsotropicElasticityTensor
  []
  [stress]
    # Computes the stress, using linear elasticity
    type = ComputeLinearElasticStress
  []
  [density_castiron]
    #Defines the density of castiron
    type = GenericConstantMaterial
    prop_names = density
    prop_values = 6.99e-4 # lbm/in^3
  []
[]

[Preconditioning]
  [SMP]
    # Creates the entire Jacobian, for the Newton solve
    type = SMP
    full = true
  []
[]

[Postprocessors]
  [max_principal_stress_at_probe]
    type = PointValue
    point = '0.000000 -1.500000 -4.3'
    variable = max_princ
    use_displaced_mesh = false
  []
  [max_principal_stress_extremum]
    type = ElementExtremeValue
    variable = max_princ
  []
[]

[Problem]
  type = FEProblem
  kernel_coverage_check = false
  material_coverage_check = false
[]

[Executioner]
  # We solve a steady state problem using Newton's iteration
  type = Steady
  solve_type = Newton
  nl_rel_tol = 1e-9
  l_max_its = 10
  l_tol = 1e-4
  nl_max_its = 9
  petsc_options_iname = '-pc_type -pc_factor_shift_type'
  petsc_options_value = 'lu nonzero'
[]

[Outputs]
  vtk = true
  exodus = true
[]