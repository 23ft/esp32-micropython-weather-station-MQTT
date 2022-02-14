import sys

num1 = int(input("Num1: "))
num2 = int(input("Num2: "))

try:
    division = num1 / num2

except Exception as e:
    print("error is: ", e)
    sys.exit()

finally:
    print("End program!")