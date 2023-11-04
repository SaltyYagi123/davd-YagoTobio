import pandas as pd

# * Crear objetos en pandas -> Series y DataFrames. 
# * 1.  - Series -> Unidimensionales 
s = pd.Series([42,21,7,3.5])
print(s)

#* 2. DataFrames -> 2 dimensiones (Dpreadhseet)
df = pd.DataFrame({'age': 18,
        'name': ['Alice', 'Bob', 'Carl'],
        'cardio': [60, 70, 80]})
print(df)
#df = pd.read_csv('path')
# ? - Seleccionar columnas 
print(df['age'])
# ? - Seleccionar por indice and slice 
print(df[2:3]) # Esto nos da acceso a la fila 3
# ? - Acceder a elementos particulares
print(df.iloc[2,1]) # Fila i+1, columna j+1. Devolverá Carl

# ? - Boolean indexing (aka: Filtrado)
print(df[df['cardio']>60]) #Devuelve el subdataset para el cual la condición sea verdadera.

# ? - Seleccionar por columna: 
print(df.loc[:, 'name']) # -> df.loc[rows, columns] 
print(df.loc[:,['age', 'cardio']])

# ! - Modificación de dataframes: 
# ? - Modificación de toda la dolumna 
df['age'] = 16 
print(df)

# ? - Para algo más especifico 
df.loc[1:, 'age'] = 16 # Modifica todas las filas tras la primera a que sean 16

# ? - Ejemplo más avanzado
df = pd.DataFrame({'age': 18,
       'name': ['Alice', 'Bob', 'Carl'],
       'cardio': [60, 70, 80]})

df.loc[1:, 'age'] = 16 # Modifica todas las filas tras la primera a que sean 16
df.loc[:, 'friend'] = 'Alice' #Añadimos una nueva columna a todas las filas
# Metodo alternativo -> df['friend'] = 'Alice'
print(df)

# Awesome, but what if we do 
df.loc[1:, 'papaya'] = 'Yes'
print(df) #For non-filled in filters we get a NaN