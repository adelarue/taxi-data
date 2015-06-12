# intro.jl
# Script to be included before running anything in Julia
# Authored by Arthur J Delarue on 6/9/15


@everywhere using HDF5, JLD, LightGraphs
@everywhere using JuMP, Gurobi
@everywhere using MathProgBase
@everywhere include("../taxi-simulation/definitions.jl")
@everywhere include("../taxi-simulation/Cities/manhattan.jl")
@everywhere include("../taxi-simulation/Cities/squareCity.jl")
@everywhere include("LP_tools.jl")