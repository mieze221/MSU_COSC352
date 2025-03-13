import os

proc main() =
  if paramCount() < 1:
    echo "Usage: ./hello <name> [number]"
    return

  let name = paramStr(1)
  let count = if paramCount() > 1: parseInt(paramStr(2)) else: 1

  if count <= 0:
    echo "Error: The number of greetings must be a positive integer."
    return

  for i in 1..count:
    echo "Hello ", name

main()
