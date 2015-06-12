# LP_tools.jl
# Contains helpful functions to debug Gurobi output
# Authored By Arthur J Delarue on 6/10/15

function print_iis_gurobi(m::Model)
	# Taken from JuMP examples online
    grb = MathProgBase.getrawsolver(getInternalModel(m))
    Gurobi.computeIIS(grb)
    numconstr = Gurobi.num_constrs(grb)
    numvar = Gurobi.num_vars(grb)

    iisconstr = Gurobi.get_intattrarray(grb, "IISConstr", 1, numconstr)
    iislb = Gurobi.get_intattrarray(grb, "IISLB", 1, numvar)
    iisub = Gurobi.get_intattrarray(grb, "IISUB", 1, numvar)

    println("Irreducible Inconsistent Subsystem (IIS)")
    println("Variable bounds:")
    for i in 1:numvar
        v = Variable(m, i)
        if iislb[i] != 0 && iisub[i] != 0
            println(getLower(v), " <= ", getName(v), " <= ", getUpper(v))
        elseif iislb[i] != 0
            println(getName(v), " >= ", getLower(v))
        elseif iisub[i] != 0
            println(getName(v), " <= ", getUpper(v))
        end
    end

    println("Constraints:")
    for i in 1:numconstr
        if iisconstr[i] != 0
            println(m.linconstr[i])
        end
    end
    println("End of IIS")
end

@everywhere function parallelShortestPaths(n::Network, roadTime::SparseMatrixCSC{Int, Int},roadCost::SparseMatrixCSC{Float64, Int})
	nLocs  = length( vertices(n))
	# Find number of cores
	nCpus = length(workers())

	# Start processes
	results = cell(nCpus)
	for i = 1:nCpus
		results[i] = @spawnat i partialShortestPaths(n, (div((i-1) * nLocs, nCpus)+1):(div(i * nLocs,nCpus)), roadTime, roadCost)
	end
	# Create return arrays
	pathTime = Array(Int, (nLocs,nLocs))
	pathCost = Array(Float64, (nLocs,nLocs))
	previous = Array(Int, (nLocs,nLocs))
	# Fetch results and add them together
	for i = 1:length(results)
		tmp_time, tmp_cost, tmp_prev = fetch(results[i])
		irange = (div((i-1) * nLocs, nCpus)+1):(div(i * nLocs,nCpus))
		pathTime[irange,:] = tmp_time
		# pathCost[irange,:] = tmp_cost
		previous[irange,:] = tmp_prev
	end
	
	return ShortPaths(pathTime, pathCost, previous)
end

# Define helper function that finds subsets of shortest paths
@everywhere function partialShortestPaths(n::Network, locs::UnitRange{Int}, roadTime::SparseMatrixCSC{Int, Int},roadCost::SparseMatrixCSC{Float64, Int})
	nLocs  = length( vertices(n))
	partialPathTime = zeros(Int, (length(locs),nLocs))
	partialPathCost = zeros(Float64, (length(locs),nLocs))
	partialPrevious = zeros(Int, (length(locs),nLocs))

	for i in locs
		parents, dists, costs = custom_dijkstra_par(n, i, roadTime, roadCost)
		partialPrevious[i-minimum(locs)+1,:] = parents
		partialPathTime[i-minimum(locs)+1,:] = dists
		# partialPathCost[i-minimum(locs)+1,:] = costs
	end
	return partialPathTime, partialPathCost, partialPrevious
end

@everywhere function custom_dijkstra_par(
    g::AbstractGraph,
    src::Int,
    edge_dists::AbstractArray{Int, 2},
    edge_costs::AbstractArray{Float64,2})


    nvg = nv(g)
    dists = fill(typemax(Int), nvg)
    costs = fill(typemax(Float64), nvg)
    parents = zeros(Int, nvg)
    visited = falses(nvg)
    H = Int[]
    dists[src] = 0
    costs[src] = 0.0
    sizehint(H, nvg)
    heappush!(H, src)
    while !isempty(H)
        u = heappop!(H)
        for v in out_neighbors(g,u)
            if dists[u] == typemax(Int)
                alt = typemax(Int)
                alt2 = typemax(Float64)
            else
                alt = dists[u] + edge_dists[u,v]
                alt2 = costs[u] + edge_costs[u,v]

            end
            if !visited[v]
                dists[v] = alt
                costs[v] = alt2
                parents[v] = u
                visited[v] = true
                heappush!(H, v)
            else
                if alt < dists[v]
                    dists[v] = alt
                    costs[v] = alt2
                    parents[v] = u
                    heappush!(H, v)
                end
            end
        end
    end

    dists[src] = 0
    costs[src] = 0.0
    parents[src] = 0


    return parents, dists, costs
end
