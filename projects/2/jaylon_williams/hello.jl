function main()
    
    if length(ARGS) != 2
    println("Usage: julia hello.jl <name> <number>")
    exit(1)
end

name = ARGS[1]
num = try
    parse(Int, ARGS[2])
catch
    println("Error: Second argument must be an integer.")
    exit(1)
end

# Print the greeting multiple times
for _ in 1:num
    println("Hello $name")
end
