# Project 1: Hello World Program with Docker

## Objective
Write a "Hello World" program in Python (or any other language other than bash) that:
1. Accepts a command-line argument `<name>` and prints out `"Hello <name>"`.
2. Accepts an additional argument `<number>` to print out `"Hello <name>"` the specified number of times.

This program **must be dockerized**.

---

## Requirements
1. **Program Functionality**:
   - The program should take two command-line arguments:
     - `<name>`: A string input representing the name.
     - `<number>`: An integer input representing how many times the greeting is printed.
   - Output Example:
     ```bash
     $ python hello.py Alice 3
     Hello Alice
     Hello Alice
     Hello Alice
     ```

2. **Dockerization**:
   - Create a `Dockerfile` that builds an image for the program.
   - The image must allow the program to run with `docker run project1 <name> <number>`.

3. **Directory Structure**:
   - Place your project in the following directory:
     ```
     Projects/1/<firstname>_<lastname>/
     ```
   - The directory should contain:
     - The source code file for your program.
     - A `Dockerfile`.

4. **Execution Steps**:
   - Build the Docker image with:
     ```bash
     docker build . -t project1
     ```
   - Run the container with:
     ```bash
     docker run project1 <name> <number>
     ```

---

## Submission Instructions
1. Create the directory structure:
2. Place your `Dockerfile` and source code in the directory.
3. Ensure that your program and Docker configuration meet the requirements.

---
