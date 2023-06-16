# Imports

import re, argparse, logging

logger = logging.getLogger('vm')

DEBUG = False
LOGGING_LEVEL = logging.DEBUG

# Décalarations

pile = [] # pile de données
po = [] # pile d'instructions
co = 0 # compteur ordinal
ip = -1 # pointeur de pile
base = 0 # registre de base (bas du bloc)

def afficherPile():
	global ip
	global base
	res = ""
	for i in range(len(pile)-1,-1,-1):
		res += "| %s\t|"%(pile[i])
		if ip == i: 
			res += " <- ip"
		if base == i: 
			res += " <- base"
		res += '\n'
	return res

def main():
	global base
	global ip
	global co

	parser = argparse.ArgumentParser(description='Execute the compiled NNP program.')
	parser.add_argument('inputfile', type=str, nargs=1, help='name of the code file')
	parser.add_argument('-d', '--debug', action='store_const', const=logging.DEBUG, default=logging.INFO, help='show debugging info on output')
	parser.add_argument('-s', '--step-by-step', action='store_true', help='execute step by step')
	args = parser.parse_args()

	filename = args.inputfile[0]
	f = None
	try:
		f = open(filename, 'r')
	except:
		print("Error: can\'t open input file!")
		return
	
	# create logger      
	LOGGING_LEVEL = args.debug
	logger.setLevel(LOGGING_LEVEL)
	ch = logging.StreamHandler()
	ch.setLevel(LOGGING_LEVEL)
	formatter = logging.Formatter('%(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)

	STEP_BY_STEP = args.step_by_step
	
	for line in f:
		instr = line.rstrip('\r\n')
		po.append(instr)
	f.close()

	finProg = False

	while not finProg :
		instr = po[co]
		logger.debug("pile : \n%s"%(afficherPile()))
		logger.debug(instr)

		if STEP_BY_STEP:
			input()
				
		# debutProg
		if re.match(r"debutProg()", instr):
			base = 0
			co = co + 1
		
		# finProg
		elif re.match(r"finProg()", instr):
			finProg = True

		# reserver
		elif re.match(r"reserver\(\d+\)", instr):
			n = int(re.search(r"\d+",instr).group())
			for i in range(n):
				pile.append(None)
			ip = ip + n # n : nombre de blocs à réserver
			co = co + 1
			 
		# empiler
		elif re.match(r"empiler\(\d+\)", instr):
			val = int(re.search(r"\d+",instr).group())
			pile.append(val) # val : valeur à empiler
			ip = ip + 1
			co = co + 1
		
		# empilerAd
		elif re.match(r"empilerAd\(\d+\)", instr):
			ad = int(re.search(r"\d+",instr).group())
			ip = ip + 1
			pile.append(base+ad+2)
			co = co + 1
			
		# affectation
		elif re.match(r"affectation()", instr):
			# ip - 1 : emplacement sous le sommet 
			# on place la valeur en sommet de pile à l'adresse sur laquelle pointe l'emplacement sous le sommet 
			pile[ pile[ip - 1] ]= pile[ip]
			pile.pop() # on retire la valeur du sommet de pile, après l'avoir déplacé 
			pile.pop()
			ip = ip - 2 # on maj l'endroit où pointe ip 
			co = co + 1

		# valeurPile
		elif re.match(r"valeurPile()", instr):
			#  On remplace le sommet de pile par le contenu de l’emplacement désigné
			#  par le sommet.
			pile[ip] =  pile[ pile[ip] ]  # Dans pile[ip] : on stocke l'@ de la case pointé par la case d'indice ip
											# pile [ pile[ip] ] : désigne la valeur de l'emplacement désigné par le sommet de pile
			co = co + 1

		# get
		elif re.match(r"get()", instr): # a corriger
			# L'instruction permet de placer la valeur lue sur le clavier dans la variable qui est désignée par le sommet de pile
			# v : valeur lue 
			v = int(input("saisir valeur: "))
			pile [ pile[ip] ] = v
			ip = ip - 1 
			co = co + 1
			pile.pop()

		# put
		elif re.match(r"put()", instr):
			# Cette instruction permet d’afficher la valeur présente au sommet de la pile
			v = pile[ip] # valeur présente au sommet de la pile
			print(v) # on affiche v 
			ip = ip - 1 # maj du pointeur de pile 
			pile.pop()
			co = co + 1

		# moins
		elif re.match(r"moins()", instr):
			pile[ip] = - pile[ip]
			co = co + 1

		# sous
		elif re.match(r"sous()", instr):
			pile[ip - 1] = pile[ip - 1] - pile[ip]
			ip = ip - 1 
			co = co + 1
			pile.pop()

		# add
		elif re.match(r"add()", instr):
			pile[ip - 1] = pile[ip - 1] + pile[ip]
			ip = ip - 1
			co = co + 1
			pile.pop()

		# mult
		elif re.match(r"mult()", instr):
			pile[ip - 1] = pile[ip - 1] * pile[ip]
			ip = ip - 1
			co = co + 1
			pile.pop()

		# div
		elif re.match(r"div()", instr):
			pile[ip - 1] = pile[ip - 1] // pile[ip]
			ip = ip - 1
			co = co + 1
			pile.pop()

		# egal
		elif re.match(r"egal()", instr):
			# Cette instruction compare les deux valeurs op1 et op2 en sommet de pile et empile le code de l’expression booléenne op1=op2.
			code = (pile[ip] == pile[ip - 1]) # expression booléenne op1=op2, avec op1 et op2 stockées respectivement dans pile[ip] et pile[ip - 1]
			pile[ip - 1] = code
			pile.pop()
			ip = ip - 1
			co = co + 1

		# diff
		elif re.match(r"diff()", instr):
			code = (pile[ip]  != pile[ip - 1]) # expression booléenne op1/=op2, avec op1 et op2 stockées respectivement dans pile[ip] et pile[ip - 1]
			pile[ip - 1] = code
			pile.pop()
			ip = ip - 1     
			co = co + 1

		# inf
		elif re.match(r"inf()", instr):
			code = (pile[ip - 1] < pile[ip]) # expression booléenne op1<op2, avec op1 et op2 stockées respectivement dans pile[ip] et pile[ip - 1]
			pile[ip - 1] = code
			pile.pop()
			ip = ip - 1 
			co = co + 1

		# infeg
		elif re.match(r"infeg()", instr):
			code = (pile[ip - 1] <= pile[ip]) # expression booléenne op1<=op2, avec op1 et op2 stockées respectivement dans pile[ip] et pile[ip - 1]
			pile[ip - 1] = code
			pile.pop()
			ip = ip - 1 
			co = co + 1

		# sup
		elif re.match(r"sup()", instr):
			code = (pile[ip - 1] > pile[ip]) # expression booléenne op1>op2, avec op1 et op2 stockées respectivement dans pile[ip] et pile[ip - 1]
			pile[ip - 1] = code
			pile.pop()
			ip = ip - 1 
			co = co + 1

		# supeg
		elif re.match(r"supeg()", instr):
			code = (pile[ip - 1] >= pile[ip]) # expression booléenne op1>=op2, avec op1 et op2 stockées respectivement dans pile[ip] et pile[ip - 1]
			pile[ip - 1] = code
			pile.pop()
			ip = ip - 1 
			co = co + 1

		# et
		elif re.match(r"et()", instr):
			code = (pile[ip - 1] and pile[ip]) # expression booléenne (op1 and op2), avec op1 et op2 stockées respectivement dans pile[ip] et pile[ip - 1]
			pile[ip - 1] = code
			pile.pop()
			ip = ip - 1 
			co = co + 1

		# ou
		elif re.match(r"ou()", instr):
			code = (pile[ip - 1] or pile[ip]) # expression booléenne (op1 or op2), avec op1 et op2 stockées respectivement dans pile[ip] et pile[ip - 1]
			pile[ip - 1] = code
			pile.pop()
			ip = ip - 1 
			co = co + 1

		# non
		elif re.match(r"non()", instr):
			# Cette instruction permet de calculer la négation du booléen en sommet de pile
			pile[ip] = not (pile[ip])
			co = co + 1

		# tra
		elif re.match(r"tra\(\d+\)", instr):
			# ette instruction donne le contrôle à l’instruction située à l’adresse ad
			ad = int(re.search(r'\d+',instr).group())
			co = ad 

		# tze
		elif re.match(r"tze\(\d+\)", instr):
			ad = int(re.search(r'\d+',instr).group())
			# Cette instruction donne le contrôle à l’instruction située à l’adresse ad si le sommet de pile contient faux, continue en séquence sinon
			if pile[ip] == 0 : # cas 1 : 0 (faux) en sommet de pile
				co = ad
				ip = ip - 1
			elif pile[ip] == 1 : # cas 2 : 1 (vrai) en sommet de pile 
				co = co + 1
				ip = ip - 1
			pile.pop()

		# reserverBloc
		elif re.match(r"reserverBloc()", instr):
			# Cette instruction permet, lors de l’appel d’une opération, 
			# de réserver les emplacements du futur bloc de liaison 
			# et d’initialiser la partie pointeur vers le bloc de liaison de l’appelant .
			pile.append(None)
			pile.append(None)
			ip = ip + 2
			pile[ip - 1] = base
			co = co + 1 

		# retourFonct
		elif re.match(r"retourFonct()", instr):
			# Cette instruction est produite à la fin de la compilation d’une instruction return dans
			# une fonction. Outre son rôle dans le retour, elle assure que la valeur en sommet de pile
			# sera le résultat de l’appel.
			#ar = int(re.search(r'\d+',instr).group())
			n = ip - base
			v = pile[ip]
			ip = base
			co = pile[base + 1] 
			base = pile[base] 
			for i in range(n):
				pile.pop()
			pile[ip] = v
	

		# retourProc
		elif re.match(r"retourProc()", instr):
			# Cette instruction est produite à la fin de la compilation d’une procédure. 
			# Elle assure le retour à l’appelant.
			n = ip - base
			ip = base
			co = pile[base + 1] 
			base = pile[base] 
			for i in range(n):
				pile.pop()

		# empilerParam
		elif re.match(r"empilerParam\(\d+\)", instr):
			ad = int(re.search(r"\d+",instr).group())
			pile.append( pile[base+2+ad])
			ip = ip +1
			co = co +1

		# traStat
		elif re.match(r"traStat\(\d+,\d+\)", instr):
			params = re.findall(r"\d+", instr)
			ad = int(params[0])
			nbp = int(params[1])
			base = ip-nbp-1
			pile[base+1] = co + 1
			co = ad

		else:
			print("Instruction inconnue : ", instr)
			finProg = True



if __name__ == "__main__":
    main()
