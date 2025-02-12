import java.lang.reflect.Method;
import java.util.Scanner;

class Calculator {
    // Example method
    public int add(int a, int b) {
        return a + b;
    }
    public int multiply(int a, int b) {
        return a * b;
    }

    public int subtract(int a, int b) {
        return a - b;
    }

    public int doubleUp(int a, int b) {
        return 2 * (a * b);
    }
}

public class CalculatorApp {
    public static void main(String[] args) {
        Calculator calculator = new Calculator();
        Class<?> clazz = calculator.getClass();
        Method[] methods = clazz.getDeclaredMethods();
        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.println("Available operations:");
            for (Method method : methods) {
                if (method.getParameterCount() == 2 && method.getParameterTypes()[0] == int.class) {
                    System.out.println("\t-> " + method.getName() + " int int");
                }
            }
            System.out.println("Enter method name and arguments (or 'exit' to quit):");
            
            String input = scanner.nextLine();
            if (input.equalsIgnoreCase("exit")) {
                break;
            }
            
            String[] parts = input.split(" ");
            if (parts.length != 3) {
                System.out.println("Invalid input. Format: methodName num1 num2");
                continue;
            }
            
            String methodName = parts[0];
            try {
                int num1 = Integer.parseInt(parts[1]);
                int num2 = Integer.parseInt(parts[2]);
                
                Method method = clazz.getMethod(methodName, int.class, int.class);
                Object result = method.invoke(calculator, num1, num2);
                System.out.println("Result: " + result);
                System.out.print("\n");
            } catch (NoSuchMethodException e) {
                System.out.println("Operation doesn't exist");
            } catch (Exception e) {
                System.out.println("Error: " + e.getMessage());
            }
        }
        scanner.close();
    }
}
