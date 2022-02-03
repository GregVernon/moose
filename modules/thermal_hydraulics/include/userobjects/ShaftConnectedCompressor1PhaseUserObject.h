#pragma once

#include "VolumeJunction1PhaseUserObject.h"
#include "ShaftConnectableUserObjectInterface.h"

class SinglePhaseFluidProperties;
class NumericalFlux3EqnBase;

/**
 * Computes and caches flux and residual vectors for a 1-phase compressor
 *
 * This class computes and caches the following quantities:
 * \li residuals for the scalar variables associated with the compressor,
 * \li fluxes between the flow channels and the compressor, and
 * \li compressor torque and inertia which are passed to the connected shaft.
 */
class ShaftConnectedCompressor1PhaseUserObject : public VolumeJunction1PhaseUserObject,
                                                 public ShaftConnectableUserObjectInterface
{
public:
  ShaftConnectedCompressor1PhaseUserObject(const InputParameters & params);

  virtual void initialSetup() override;
  virtual void initialize() override;
  virtual void execute() override;

  /// Isentropic torque computed in the 1-phase shaft-connected compressor
  Real getIsentropicTorque() const;
  /// Dissipation torque computed in the 1-phase shaft-connected compressor
  Real getDissipationTorque() const;
  /// Friction torque computed in the 1-phase shaft-connected compressor
  Real getFrictionTorque() const;
  /// Compressor head computed in the 1-phase shaft-connected compressor
  Real getCompressorDeltaP() const;

  virtual void finalize() override;
  virtual void threadJoin(const UserObject & uo) override;

  virtual void getScalarEquationJacobianData(const unsigned int & equation_index,
                                             DenseMatrix<Real> & jacobian_block,
                                             std::vector<dof_id_type> & dofs_i,
                                             std::vector<dof_id_type> & dofs_j) const override;

protected:
  virtual void computeFluxesAndResiduals(const unsigned int & c) override;

  /// Direction of the compressor outlet
  Point _di_out;
  /// Rated compressor speed
  const Real & _omega_rated;
  /// Rated compressor mass flow rate
  const Real & _mdot_rated;
  /// Rated compressor inlet stagnation fluid density
  const Real & _rho0_rated;
  /// Rated compressor inlet stagnation sound speed
  const Real & _c0_rated;
  /// Compressor speed threshold for friction
  const Real & _speed_cr_fr;
  /// Compressor friction constant
  const Real & _tau_fr_const;
  /// Compressor friction coefficients
  const std::vector<Real> & _tau_fr_coeff;
  /// Compressor speed threshold for inertia
  const Real & _speed_cr_I;
  /// Compressor inertia constant
  const Real & _inertia_const;
  /// Compressor inertia coefficients
  const std::vector<Real> & _inertia_coeff;
  /// Compressor speeds which correspond to Rp and eff function order
  const std::vector<Real> & _speeds;
  /// Names of the pressure ratio functions
  const std::vector<FunctionName> & _Rp_function_names;
  /// Names of the adiabatic efficiency functions
  const std::vector<FunctionName> & _eff_function_names;
  /// Size of vector _speeds
  const unsigned int _n_speeds;
  /// Pressure ratio functions
  std::vector<const Function *> _Rp_functions;
  /// Adiabatic efficiency functions
  std::vector<const Function *> _eff_functions;

  /// Compressor name
  const std::string & _compressor_name;

  const VariableValue & _omega;

  /// Compressor isentropic torque
  Real _isentropic_torque;
  /// Compressor dissipation torque
  Real _dissipation_torque;
  /// Compressor friction torque
  Real _friction_torque;
  /// Compressor delta p
  Real _delta_p;

  /// Jacobian entries of junction variables wrt shaft variables
  std::vector<DenseMatrix<Real>> _residual_jacobian_omega_var;

public:
  static InputParameters validParams();
};