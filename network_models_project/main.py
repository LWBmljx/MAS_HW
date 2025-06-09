
from demo import run_sir_model_demo,run_lt_model_demo

def main():
    print("Select the network model simulation to run:")
    print("1: Linear Threshold Model")
    print("2: SIR Epidemic Model")
    
    while True:
        try:
            choice = input("Enter your choice (1 or 2): ")
            if choice == '1':
                print("Starting Linear Threshold Model Demo...")
                run_lt_model_demo()
                break
            elif choice == '2':
                print("Starting SIR Epidemic Model Demo...")
                run_sir_model_demo()
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:                                                                   
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == '__main__':
    main()
