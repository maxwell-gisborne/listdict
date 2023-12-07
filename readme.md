# listdict

Pure Python utility functions for working with lists of dictionaries.

I have found that, in Python, lists of dictionaries are very powerful and flexible datastructures
when handling moderate amounts of data, given a handful of functions to deal with them properly.

If the data is too large, or performance is very important,
then storing data in Python objects and manipulating them with pure Python code is a bad idea,
but for moderate amounts of data, I have found that performance has not been an issue.


## Example


Given some data;
``` python
data = [
    {name: 'Sherlock', age: 32, address: '21 Bakers street, Ldn'},
    {name: 'Jhon', age: 37, address: 'i dont know ive not read the books'},
    {name: 'Kevin', age: 55, address: 'less then 5 connections from you'},
    {name: 'Joe', age: inf, address: 'The White House, DC'},
    ]
```

It's easy to pull out a list of each of the variables
```python
names, ages = get('name','age', data)
```

Its easy to transform the data
```python
data = transform(
    dict(
        name = lambda nm: nm.title(),
        address = lambda add: add.upper(),
        age = lambda age: age+1,
        ),
    data)
```

If some of the data is missing, we can add stand-in data, so that all the dicts have the same field
```python
data = hermoginise(data, default='missing data')
```

If you want to print out the data, you can use the ``to_table(data)`` function to output an OrgMode formatted table.

If you want to read or write to csv, you can use the ``to_csv`` and ``from_csv`` functions.

Several other functions like `remove`, `join`, and `filter` are also available.


## Conventions and Principles

1. in the source code variables called `LD` == List Dictionary :: [dict]
2. D == dictionary
3. functions that act on LDs,
4. have them as their last argument.
5. no functions modify their arguments
6. all functions functions are eager, not lazy.
7. Code is PEP8 complient
