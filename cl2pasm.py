# This file converts source code to pseudo assembly (pasm)
# (pasm because I still have to learn assembly)

''' ----------------------------INITIALISATION---------------------------- '''
from sys import argv
if   len(argv) <2: raise ValueError('Input file not specified')
elif len(argv)==2: argv.append('a.pasm')
infile  = open(argv[1])
outfile = open(argv[2], 'w')
# argv[0] is the path of this python file

'''Outline:
Pass 1 - dict of variable locations, shapes and sizes
       - dict of function return shapes and sizes
Pass 2 - method substitution (including __data_definition__ methods)
       - assignment substitution
       - functions and .text section
'''

''' -------------------------------REGEX---------------------------------- '''
import re
# match     Match a regular expression pattern to the beginning of a string.
# fullmatch Match a regular expression pattern to all of a string.
# search    Search a string for the presence of a pattern.
# sub       Substitute occurrences of a pattern found in a string.
# subn      Same as sub, but also return the number of substitutions made.
# split     Split a string by the occurrences of a pattern.
# findall   Find all occurrences of a pattern in a string.
# finditer  Return an iterator yielding a Match object for each match.
# compile   Compile a pattern into a Pattern object.
# purge     Clear the regular expression cache.
# escape    Backslash all non-alphanumerics in a string.

word_re = r'[\w_][\w\d_]*'
word_pattern = re.compile(word_re)

# Pass 1
unit_re = r'[0-8]'	# will add tuples later
shape_re = r'(\[\d+\]|[0-8])*'

dec_re = f'({shape_re}{unit_re})({word_re})'
dec_pattern = re.compile(dec_re)
label_pattern = re.compile('#'+dec_re)
func_pattern  = re.compile(dec_re+':')

blank_pattern = re.compile(r'^(--.*)?$')

# Pass 2
exp_re = fr'(\d*|{word_re})'	# only identifiers and numbers for now
# allocations will also be method calls
# other syntax for the __methods__ will be added also
alloc_re = fr'\[{exp_re}\]+'	# shape and unit alloc later
alloc_pattern = re.compile(alloc_re+word_re)

'''  -------------------------PASS 1 - CREATING DICTS--------------------- '''
data = {'': (None, {'':(None, {})})}
# {label: (label_type, {func: (func_type, {var: var_type})})}
indent = ''

token = lambda t: None # do something

loc = 0
head_func = ''
head_label = ''
for line_no, line in enumerate(infile, 1):
	if blank_pattern.match(line): continue

	if line.startswith(indent): token('INDENT')
	else:
		curr_indent = line.match(r'\s*')[0]
		if indent.startswith(curr_indent): token('DEDENT') #get how many levels
		else: raise SyntaxError('Inconsistant use of tabs and spaces.')

	if   decl:=label_pattern.match(line):
		label_type = decl[1]
		label = decl[3]
		Dict = data
		if label in Dict: raise ValueError(
			f"Label '{label}' already declared before line {line_no}.")
		Dict[label] = (label_type, {})
		head_label = ''

	elif decl:=func_pattern.match(line):
		func_type = decl[1]
		func = decl[3]
		Dict = data[head_label][1]
		if func in Dict: raise ValueError(
			f"Function '{func}' already declared before line {line_no}.")
		Dict[func] = (func_type, {})
		head_func = ''

	elif decl:=dec_pattern.match(line):
		var_type = decl[1]
		var = decl[3]
		if var in Dict: raise ValueError(
			f"Variable '{var}' already declared before line {line_no}.")
		Dict = data[head_label][1][head_func][1]
		Dict[var] = var_type

	loc += len(line)

print(data)
