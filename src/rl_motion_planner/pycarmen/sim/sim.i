
%module sim

%include "/usr/share/swig3.0/python/typemaps.i"
%include "/usr/share/swig3.0/python/std_vector.i" 

namespace std
{
    %template(FloatVector) vector<double>;
    %template(FloatVVector) vector< vector<double> >;
}

%{
// The following lines are responsible for automatically translating std::vector<float> to python tuples.
#include "carmen_sim.h"
%}


// **********************************************************
// List of function and classes we want to expose.
// By including the file the whole content is exposed.
// **********************************************************
%include "carmen_sim.h"


