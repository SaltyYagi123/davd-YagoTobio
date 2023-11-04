# Seguimiento del libro de The Book of Dash - No starch Press. 
# Python Review 
# * 1. Lists -> Se usan para el layour de Python, para meter Bootstrap y se ve en los callbacks 
lst = [1,2,2]
print(len(lst))
# ? Como añadir un elemento al final de la lista. 
lst.append(4)
print(lst)
# ? Como añadir varios elementos al final de la lista. 
lst.extend([3,5])
print(lst)
# ? Definir en donde quieres insertar el elemento -> lst.insert(posicion, elemento)
lst.insert(2,2)
lst.insert(0,'a') # ? - 
print(lst)
# ? Concatenación de listas (+)
lst = lst + [5]
print(lst)
# ? Como quitar elementos por valor 
lst.remove('a')
print(lst)
# ? Como darle la vuelta a la lista. 
lst.reverse()
print(lst)
# ? Sort lista: 
lst.sort() # Orden normal 
lst.sort(reverse=True) # Orden inverso
lst.sort(key= lambda x:-x) # Orden customizado 
# ? Encontrar el indice del elemento en la lista 
print([2,2,4].index(2,0))  #.index(Elemento a encontrar, Posición de la que empezar a buscar)
# Nos devolvera 0, ya que la primera instancia de 2 es en la posición 0
# ? Slicing 
s = '----p-y-t-h-o-n-----a'
#string[start:stop:step]
print(s[4:15:2])
print(s[-1:])
s = "abcdefghijkl"
print(s[-3:-7:-1])
t = "The quick brown fox jumps over the lazy dog"
print(t[::-3])
u = "1234567890"
print(u[::-2])
# * 2. Dictionaries -> Useful for storing key value pairs. Mutable
calories = {'apple': 52, 'banana':89, 'choco': 546}
print(calories['apple'] < calories['choco'])

# ? - Mutable, es decir que se puede cambiar despues de su creacion
calories['cappu'] = 74 
print(calories['banana'] < calories['cappu']) 

# ? - Acceso de claves y valores. 
print('apple' in calories.keys())
print(52 in calories.values())

# ? - Bucles con diccionarios 
for key, value in calories.items(): 
    if value > 500: 
        print(key)
# ! - List comprehension - Como generar listas y diccionarios con solo una linea. 
numbers = [x for x in range(3)]
print(numbers)
# ? - Se puede usar en Dash para generar elementos de una manera muy rapida. Dropdown
days = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
options = [{'label':day, 'value': day} for day in days]
# Si no tambien se puede hacer asi 
options = [] 
for day in days: 
    options.append({'label':day, 'value':day})
# O tambien si se quiere excluir algún valor por ejemplo, eliminar Sabado y Domingo 
options = [{'label':day, 'value':day} for day in days if day not in ['Sabado', 'Domingo']]

# * 3. Objetos 
class Muggle: 
    def __init__(self, age, name, liking_person): #Tecnicamente no hace falta al definir un metodo con el primer. 
        self.age = age, 
        self.name = name, 
        self.likes = liking_person

class Wizard: 
    def __init__(self, age, name):
        self.age = age
        self.name = name 
        self.mana = 200 #Hardocoded 

    # Componente externo, probablemente Muggle
    def love_me(self, victim): 
        if self.mana >= 100: 
            victim.likes = self.name
            self.mana = self.mana - 100

# ? - Definiciones de los objetos 
Vernon = Muggle(52, "Vernon", None)
Petunia = Muggle(49, "Petunia", Vernon)
# ? - Propiedades mutables 
Vernon.likes = "Petunia"
print(Vernon.likes)

Wiz = Wizard(42, "Tom")
Wiz.love_me(Petunia)
print(Wiz.mana)
Wiz.love_me(Vernon)
print(Petunia.likes == "Tom" and Vernon.likes == "Tom") # Claro porque no le queda mana despues del primero

# * 4. Decorator Functions + Annotations  
def print_text(): 
    print("Hello world!")

def pretty_print(): 
    annotate = '+'
    print(annotate * 30)
    print_text()
    print(annotate*30)

print_text()
pretty_print()

# En este caso le estamos pasando una función, no una variable, que le va a dar el string. 
def pretty_print_decorator(f): 
    annotate = '+'

    def pretty_print(): 
        print(annotate*50)
        f()
        print(annotate*50)
    return pretty_print

def print_text(): 
    print("Hello World!")

def print_text_2(): 
    print("Hello universe!")

pretty_print_decorator(print_text)()
pretty_print_decorator(print_text_2)()

# Pero eso es una manera muy larga de hacerlo, la de verdad es así: 
def pretty_print_decorator(f): 
    annotate = '+'

    def pretty_print(): 
        print(annotate*50)
        f()
        print(annotate*50)
    return pretty_print

@pretty_print_decorator
def print_text(): 
    print("Hello World!")

@pretty_print_decorator
def print_text_2(): 
    print("Hello universe!")

print_text()
print_text_2()