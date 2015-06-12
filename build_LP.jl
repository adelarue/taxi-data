# build_LP.jl
# Once Manhattan problem is loaded, builds instance of LP necessary
# Authored by Arthur J Delarue on 6/9/15

function build_LP(graph::Network, travelTimes::Array{Float64,2}, roadTimes::SparseMatrixCSC{Int, Int}, sp::ShortPaths)
	roads = edges(graph)
	nodes = vertices(graph)
	out = [copy(out_neighbors(graph,i)) for i in nodes]
	
	ITERATIONS = 2 #must be positive

	# Create JuMP model
	println("**** Creating LP instance ****")
	m = Model(solver=GurobiSolver(TimeLimit=100, Method=1))
	
	# Add one variable for each road
	@defVar(m, t[i=nodes,j=out[i]])

	# Define objective function
	#@setObjective(m, Min, sum{ t[i,j] * t[i,j]/(max(roadTimes[i,j],1) * max(roadTimes[i,j],1)), i=nodes, j=out[i] })
	@setObjective(m, Min, sum{ t[i,j], i=nodes, j=out[i] })

	# Add bounds on variables
	for i in nodes, j in out[i]
		@addConstraint(m, t[i,j] >= roadTimes[i,j])
	end

	status = 0
	newTimes = roadTimes
	new_sp = sp
	for l = 1:ITERATIONS
		# Add path constraints
		println("**** Adding constraints ****")
		for i in nodes, j in nodes
			if travelTimes[i,j] > 0 && i != j
				pathNodes = [j]
				k = j
				while k != i
					k = new_sp.previous[i,k]
					push!(pathNodes, k)
				end
				reverse!(pathNodes)
				@addConstraint(m, sum{ t[pathNodes[a],pathNodes[a+1]], a=1:(length(pathNodes)-1) } >= travelTimes[i,j])
			end
		end

		# Solve LP
		println("**** Solving LP ****")
		status = solve(m)

		# Debug if infeasible
		if status == :Infeasible
			buildInternalModel(m)
			print_iis_gurobi(m)
		# Prepare output
		elseif status == :Optimal
			st = getValue(t)
			println(length(st))
			newTimes = spzeros(length(nodes), length(nodes))
			for element in st
				newTimes[element[1], element[2]] = element[3]
			end
		end
		if l < ITERATIONS
			println("**** Computing shortest paths ****")
			@time new_sp = parallelShortestPaths(graph, int(newTimes), newTimes)
		end
	end
	return status, newTimes
end

status, new_times = build_LP(graph, travel_times, times, sp)