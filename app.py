from flask import Flask, request, render_template
import requests

app = Flask(__name__)
api_key1="1ce7104ac48c4065a3535fb812d5502f"
api_key2="655af0a13ced41668cd396a92f2f7732"
api_key3="8069c5dbc63e4ba0b9ac513e93165dae"

#encrypting passwords while storing in file
def encrypt(password):
    new_pw=""
    for i in password:
        new_pw+=chr(ord(i)+5)
    return new_pw

#entering login details of a new user into file
def add_logins(username,password):
    with open("logins.txt",'a') as f1:
        f1.write(f'{username} {encrypt(password)}\n')
    
#check username
def check_username(username):
    logins={}
    with open("logins.txt",'r') as f1:
        for line in f1:
            us,pw=line.split()
            logins[us]=pw
    if(username in logins):
        return -1
    
#getting login details
def get_logins(username,password):
    logins={}
    password=encrypt(password)
    with open("logins.txt",'r') as f1:
        for line in f1:
            us,pw=line.split()
            logins[us]=pw
    if(username not in logins):
        return -1
    if(logins[username]!=password):
        return 1
    if(logins[username]==password):
        return 0
    
#login authentication for home page
@app.route('/', methods=['GET', 'POST'])
def home1():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if(get_logins(username,password)==0):
            return render_template('mainpage.html')
        elif(get_logins(username,password)==-1):
            return render_template('index.html',error="Invalid Username")
        elif(get_logins(username,password)==1):
            return render_template('index.html',error="Invalid Password")
    return render_template('index.html')

#sign up a new user
@app.route('/sign',methods=['GET','POST'])
def sign():
    if request.method=='POST':
        username = request.form.get('username')
        npassword = request.form.get('npassword')
        cpassword = request.form.get('cpassword')
        if(check_username(username)==-1):
            return render_template('signup.html',error="Username already taken")
        if(npassword!=cpassword):
            return render_template('signup.html',error="Passwords are not matching")
        if(len(npassword)<8):
            return render_template('signup.html',error="Password must be minimum 8 characters")
        add_logins(username,cpassword)
        return render_template('mainpage.html')
    else:
        return render_template('signup.html')

        
#this function gets the list of recipes based on ingredients
def get_recipes(ingredients):
    url=f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={''.join(ingredients)}&apiKey={api_key2}"
    response=requests.get(url)
    recipes=[]
    if(response.status_code!=200):
        print("An error occured")
        return ""
    else:
        recipes=response.json()
        return recipes
    return ""

#this function gets the list of recipes based on time in minutes
def get_recipes_time(time):
    url=f"https://api.spoonacular.com/recipes/complexSearch?maxReadyTime={time}&apiKey={api_key2}"
    response=requests.get(url)
    recipes=[]
    if(response.status_code!=200):
        print("An error occured")
        return ""
    else:
        recipes=response.json()
        return recipes['results']
    return ""

#this function gets recipes based on time and ingredients
def get_recipesit(ingredients,time):
    url=f"https://api.spoonacular.com/recipes/complexSearch?maxReadyTime={time}&includeIngredients={ingredients}&apiKey={api_key2}"
    response=requests.get(url)
    recipes=[]
    if(response.status_code!=200):
        print("An error occured")
        return ""
    else:
        recipes=response.json()
        return recipes
    return ""

#this function gets the recipe details
#it takes the recipe id as input and returns response to html
@app.route('/details/<string:id>', methods=['GET','POST'])
def get_details(id):
    url=f"https://api.spoonacular.com/recipes/{id}/information?apiKey={api_key1}"
    response = requests.get(url)
    
    if response.status_code == 200:
        resp=response.json()
        return render_template('display.html', details=resp)
    return render_template('display.html')

#function where it checks if it is ingredient based or time based
#according to input, it calls the appropriate functions
@app.route('/main', methods=['GET','POST'])
def getIngredients():
    if request.method == 'POST':
        ingredients = request.form.get('ingredients')
        time = request.form.get('time')
        if(ingredients and time):
            recipes=get_recipesit(ingredients,time)
            return render_template('recipes.html', recipes=recipes)
        elif(ingredients):
            recipes=get_recipes(ingredients)
            return render_template('recipes.html', recipes=recipes)
        elif(time):
            recipes=get_recipes_time(time)
            #print(recipes)
            return render_template('recipes.html', recipes=recipes)
    return render_template('recipes.html', recipes="empty")

if __name__ == '__main__':
    app.run(debug=True)