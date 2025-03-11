function main()
    
    if length(ARGS) < 4 || ARGS[1] != "--name" || ARGS[3] != "--number"
        println("Usage: julia hello.jl --name <name> --number <number>")
        return
    end

    name = ARGS[2]
    number = parse(Int, ARGS[4])  

    for _ in 1:number
        println("Hello $name")
    end
end

if abspath(PROGRAM_FILE) == abspath(@__FILE__)
    main()
end