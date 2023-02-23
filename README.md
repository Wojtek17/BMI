# BMI
BMI calculation 
Simple script that calculates BMI and gives the category based of the user's data

print('Enter your weight:')
try:
    weight=int(input())
except ValueError:
        print('Weight must be a number! Enter correct value or programm will stop')
        error=True
        if error==True:
            try:
                weight=int(input())
            except ValueError:
                print('Program stopped due to incorrect input for second time')
                
print('Enter your height:')
try:
    height=int(input())
except ValueError:
        print('Height must be a number! Enter correct value or programm will stop')
        error=True
        if error==True:
            try:
                Height=int(input())
            except ValueError:
                print('Program stopped due to incorrect input for second time')    

adjusted_height= height/100

bmi=weight/adjusted_height**2

print('Your bmi is:', bmi)

if bmi > 40:
    print('Your BMI is really high, you have Obese Class III')
elif bmi < 40 and bmi >= 35:
    print('Your BMI is really high, you have Obese Class II')
elif bmi < 35 and bmi >= 30:
    print('Your BMI is pretty high, you have Obese Class I')
elif bmi < 30 and bmi >= 25:
    print('Your BMI is pretty high, you have Overweight')
elif bmi < 25 and bmi >=18.5:
    print('Your BMI is on the right level, you have Normal Weight')
elif bmi < 18.5 and bmi >= 17:
    print('Your BMI is pretty low, you have Mild Thinness')
elif bmi < 17 and bmi >= 16:
    print('Your BMI is pretty low, you have Moderate Thinness')
else:
    print('Your BMI is really low, you have Severe Thinness')
