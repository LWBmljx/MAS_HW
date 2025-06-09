from demo import run_boids_demo, run_pedestrian_demo, run_pursuit_evasion_demo

def main():
    print("Select the simulation to run:")
    print("1: Boids Flocking Model")
    print("2: Pedestrian Wander Model")
    print("3: Pursuit-Evasion Model")
    
    while True:
        try:
            choice = input("Enter your choice (1, 2, or 3): ")
            if choice == '1':
                print("Starting Boids Flocking Model Demo...")
                run_boids_demo()
                break
            elif choice == '2':
                print("Starting Pedestrian Wander Model Demo...")
                run_pedestrian_demo()
                break
            elif choice == '3':
                print("Starting Pursuit-Evasion Model Demo...")
                run_pursuit_evasion_demo()
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nExiting.")
            break

if __name__ == '__main__':
    main()
