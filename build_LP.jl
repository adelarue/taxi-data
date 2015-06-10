# build_LP.jl
# Once Manhattan problem is loaded, builds instance of LP necessary
# Authored by Arthur J Delarue on 6/9/15

function run_LP(graph::Network, travelTimes::Array{Float64,2}, roadTimes::SparseMatrixCSC{Int, Int}, sp::ShortPaths)
	roads = edges(graph)
	nodes = vertices(graph)
	out = [copy(out_neighbors(graph,i)) for i in nodes]
	
	# Create JuMP model
	println("**** Creating LP instance ****")
	m = Model(solver=GurobiSolver(TimeLimit=100, Method=1))
	
	# Add one variable for each road
	@defVar(m, t[i=nodes,j=out[i]])

	# Define objective function
	@setObjective(m, Min, sum{ t[i,j], i=nodes, j=out[i] })

	# Add constraints
	println("**** Constraints ****")
	for i in nodes, j in nodes
		if travelTimes[i,j] > 0 && i != j
			pathNodes = [j]
			k = j
			while k != i
				k = sp.previous[i,k]
				push!(pathNodes, k)
			end
			reverse!(pathNodes)
			@addConstraint(m, sum{ t[pathNodes[a],pathNodes[a+1]], a=1:(length(pathNodes)-1) } >= travelTimes[i,j])
		end
	end

	for i in nodes, j in out[i]
		@addConstraint(m, t[i,j] >= times[i,j])
	end

	function generate_paths(cb)
		# TODO
	end

	# Solve LP
	status = solve(m)

	# Debug if infeasible
	if status == :Infeasible
		buildInternalModel(m)
		print_iis_gurobi(m)
		return status
	# Prepare output
	elseif status == :Optimal
		st = getValue(t)
		println(length(st))
		newTimes = spzeros(length(nodes), length(nodes))
		for element in st
			newTimes[element[1], element[2]] = element[3]
		end
		return status, newTimes
	end
end

status, new_times = run_LP(graph, travel_times, times, sp)

if false
	println("**** Creating LP instance ****")
	# Create JuMP model
	m = Model(solver=GurobiSolver(TimeLimit=100, Method=1))

	# Add one variable for each road
	@defVar(m, t[i=nodes,j=out[i]])

	# Define objective function
	@setObjective(m, Min, sum{ t[i,j], i=nodes, j=out[i] })

	println("**** Constraints ****")
	# Add all the constraints
	l = 0
	#println(maximum(times))
	max = maximum(travel_times)
	#println(maximum(travel_times))
	for i in nodes, j in nodes
		if travel_times[i,j] > 0 && i != j
			pathNodes = [j]
			k = j
			while k != i
				k = sp.previous[i,k]
				push!(pathNodes, k)
			end
			reverse!(pathNodes)
			@addConstraint(m, sum{ t[pathNodes[a],pathNodes[a+1]], a=1:(length(pathNodes)-1) } >= travel_times[i,j])
		end
	end

	for i in nodes, j in out[i]
		#setValue(t[i,j], max)
		@addConstraint(m, t[i,j] >= times[i,j])
	end
	println("**** LP Instance created ****")

	status = solve(m)

	if status == :Infeasible
		buildInternalModel(m)
		print_iis_gurobi(m)
	end

	# m_internal = getInternalModel(m)
	# A = MathProgBase.getconstrmatrix(m_internal)
	# xlb = MathProgBase.getvarLB(m_internal)
	# xub = MathProgBase.getvarUB(m_internal)
	# l = MathProgBase.getconstrLB(m_internal)
	# u = MathProgBase.getconstrUB(m_internal)
	# result = A * xub
	# for (i,element) in enumerate(result)
	# 	if element < l[i]
	# 		print(A[i,:])
	# 	end
	# end

	if status == :Optimal
		st = getValue(t)
		println(st)
	end
end