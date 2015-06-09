# intro.jl
# Script to be included before running anything in Julia
# Authored by Arthur J Delarue on 6/9/15


include("../taxi-simulation/definitions.jl")
include("../taxi-simulation/Cities/manhattan.jl")
using HDF5, JLD, LightGraphs
using JuMP, Gurobi