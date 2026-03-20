"""
Laboratory Work 3: Python Programming
Main Module
Version: 1.0
Developer: Bryginya Vladislav Vasilevich
Date: 19.03.2026

This module provides menu to run all tasks.
"""

import task1
import task2
import task3
import task4
import task5


def main():
    while True:
        print("\n=== LAB 3 ===")
        print("1 - Task 1")
        print("2 - Task 2")
        print("3 - Task 3")
        print("4 - Task 4")
        print("5 - Task 5")
        print("0 - Exit")

        choice = input("Choose: ")

        if choice == '1':
            task1.run()
        elif choice == '2':
            task2.run()
        elif choice == '3':
            task3.run()
        elif choice == '4':
            task4.run()
        elif choice == '5':
            task5.run()
        elif choice == '0':
            print("Bye!")
            break
        else:
            print("Error")


if __name__ == "__main__":
    main()