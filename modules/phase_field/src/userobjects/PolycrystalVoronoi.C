//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "PolycrystalVoronoi.h"
#include "IndirectSort.h"
#include "MooseRandom.h"
#include "MooseMesh.h"
#include "MooseVariable.h"
#include "NonlinearSystemBase.h"

registerMooseObject("PhaseFieldApp", PolycrystalVoronoi);

template <>
InputParameters
validParams<PolycrystalVoronoi>()
{
  InputParameters params = validParams<PolycrystalUserObjectBase>();
  params.addClassDescription(
      "Random Voronoi tesselation polycrystal (used by PolycrystalVoronoiAction)");
  params.addRequiredParam<unsigned int>(
      "grain_num", "Number of grains being represented by the order parameters");

  params.addParam<unsigned int>("rand_seed", 0, "The random seed");
  params.addParam<bool>(
      "columnar_3D", false, "3D microstructure will be columnar in the z-direction?");
  params.addParam<FileName>("points_file_name", "", "Name of the points file name");
  params.addParam<MooseEnum>(
      "method", MooseEnum("UserSpecified Random", "Random"), "Dictates whether MOOSE will generate the Voronoi tessellation randomly or whether the user is specifying the Voronoi tessellation via text-file of generator points.");


  return params;
}

PolycrystalVoronoi::PolycrystalVoronoi(const InputParameters & parameters)
  : PolycrystalUserObjectBase(parameters),
    _grain_num(getParam<unsigned int>("grain_num")),
    _columnar_3D(getParam<bool>("columnar_3D")),
    _rand_seed(getParam<unsigned int>("rand_seed")),
    _points_file_name(getParam<FileName>("points_file_name")),
    _points_file_reader(_points_file_name, &_communicator),
    _method(getParam<MooseEnum>("method"))
{
}

void
PolycrystalVoronoi::getGrainsBasedOnPoint(const Point & point,
                                          std::vector<unsigned int> & grains) const
{
  auto n_grains = _centerpoints.size();
  auto min_distance = 100.; //_range.norm()
  // std::cout << "min_distance " << min_distance << std::endl;
  auto min_index = n_grains;
  auto distance = 0.0;

  // Loops through all of the grain centers and finds the center that is closest to the point p
  for (auto grain = beginIndex(_centerpoints); grain < n_grains; ++grain)
  {
    if (_method == "Random")
      {
        std::cout << "HOW?" << std::endl;
        //distance = _mesh.minPeriodicDistance(_vars[0]->number(), _centerpoints[grain], point);
      }
    else if (_method == "UserSpecified")
      {
        Point dist_vec = _centerpoints[grain] - point;
        distance = dist_vec.norm();
        // auto distance = _mesh.minPeriodicDistance(_vars[0]->number(), _centerpoints[grain], point);
      }

    if (distance < min_distance)
    {
      min_distance = distance;
      min_index = grain;
    }
  }

  mooseAssert(min_index < n_grains, "Couldn't find closest Voronoi cell");

  grains.resize(1);
  grains[0] = min_index;
}

Real
PolycrystalVoronoi::getVariableValue(unsigned int op_index, const Point & p) const
{
  std::vector<unsigned int> grain_ids;
  getGrainsBasedOnPoint(p, grain_ids);

  // Now see if any of those grains are represented by the passed in order parameter
  unsigned int active_grain_on_op = invalid_id;
  for (auto grain_id : grain_ids)
    if (op_index == _grain_to_op[grain_id])
    {
      active_grain_on_op = grain_id;
      break;
    }

  return active_grain_on_op != invalid_id ? 1.0 : 0.0;
}

void
PolycrystalVoronoi::precomputeGrainStructure()
{
  if (_method == "Random")
  {
    MooseRandom::seed(_rand_seed);

    // Set up domain bounds with mesh tools
    for (unsigned int i = 0; i < LIBMESH_DIM; i++)
    {
      _bottom_left(i) = _mesh.getMinInDimension(i);
      _top_right(i) = _mesh.getMaxInDimension(i);
    }
    _range = _top_right - _bottom_left;

    // Randomly generate the centers of the individual grains represented by the Voronoi tessellation
    _centerpoints.resize(_grain_num);
    std::vector<Real> distances(_grain_num);

    for (auto grain = decltype(_grain_num)(0); grain < _grain_num; grain++)
    {
      for (unsigned int i = 0; i < LIBMESH_DIM; i++)
        _centerpoints[grain](i) = _bottom_left(i) + _range(i) * MooseRandom::rand();
      if (_columnar_3D)
        _centerpoints[grain](2) = _bottom_left(2) + _range(2) * 0.5;
    }
  }
  else if (_method == "UserSpecified")
  {
    std::cout << "Reading: " << _points_file_name << std::endl;
    MooseUtils::checkFileReadable(_points_file_name);
    std::vector<std::string> _col_names;
    _points_file_reader.read();
    _col_names = _points_file_reader.getNames();
    std::vector<std::vector<Real>> _myData;
    _myData = _points_file_reader.getData();
    _grain_num = _myData[0].size();
    if (_grain_num == 0)
      paramError("points_file_name", "... file is empty!");

    _centerpoints.resize(_grain_num);
    std::vector<Real> distances(_grain_num);

    for (unsigned int i = 0; i < _grain_num; i++)
    {
      for (unsigned int j = 0; j < LIBMESH_DIM; j++)
        {
          _centerpoints[i](j) = _myData[j][i];
          // std::cout << _centerpoints[i](j) << " " << _myData[j][i] << std::endl;
        }
      // std::cout << _centerpoints[i] << std::endl;
    }
  }

}
