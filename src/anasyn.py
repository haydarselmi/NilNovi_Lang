#!/usr/bin/python

## 	@package anasyn
# 	Syntactical Analyser package. 
#

import sys, argparse, re
import logging
import CustomFormatter
from utils import Types, Mode
from TDI.variable import Variable
from TDI.fonction import Fonction
from TDI.procedure import Procedure
from TDI.parametre import Parametre


import analex

logger = logging.getLogger('anasyn')

DEBUG = False
LOGGING_LEVEL = logging.DEBUG


# Variables globales pour la table des identifiants
identifierTable = dict()
mainContext = ""
currentContext = ""
cptAdress = 0
listVar = []
listParam = []
# Liste des paramètres d'une fonction
listePeParam = []
#type = ""
# Liste contenant l'ensemble des instructions depuis l'analyseur
# syntaxique exécutable par la VM.
codeGenerator = []
# Pour savoir à quel ligne les procédures et fonctions commencent
addressInstruction = dict()
# Nom de l'appel fonction ou procédure en cours
callName = ""
# Pour savoir à quel paramètre on est dans l'appel de la procédure
currentParam = 0


class AnaSynException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

########################################################################				 	
#### Syntactical Diagrams
########################################################################				 	

def program(lexical_analyser):
	specifProgPrinc(lexical_analyser)
	#definition of "acceptKeyword in analex.py l.340"
	lexical_analyser.acceptKeyword("is")
	corpsProgPrinc(lexical_analyser)
	
def specifProgPrinc(lexical_analyser):
	global mainContext
	global currentContext
	global currentContext

	lexical_analyser.acceptKeyword("procedure")
	ident = lexical_analyser.acceptIdentifier()
	# TDI - table principale
	identifierTable[ident] = dict()
	mainContext = ident
	currentContext = mainContext
	currentContext = mainContext
	# ---
	logger.debug("Name of program : "+ident)
	
def corpsProgPrinc(lexical_analyser):
	global codeGenerator

	codeGenerator.append("debutProg()")

	if not lexical_analyser.isKeyword("begin"):
		logger.debug("Parsing declarations")
		partieDecla(lexical_analyser)
		logger.debug("End of declarations")
	lexical_analyser.acceptKeyword("begin")

	if not lexical_analyser.isKeyword("end"):
		logger.debug("Parsing instructions")
		suiteInstr(lexical_analyser)
		logger.debug("End of instructions")
			
	lexical_analyser.acceptKeyword("end")
	lexical_analyser.acceptFel()
	logger.debug("End of program")

	codeGenerator.append("finProg()")
	
def partieDecla(lexical_analyser):
	if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function") :
		# Pour sauter fonctions et procédures
		addressTra = len(codeGenerator)
		futureAddress = 0
		codeGenerator.append(f"tra({futureAddress})")

		listeDeclaOp(lexical_analyser)

		# Saute jusqu'à la fin des fonctions et procédures
		futureAddress = len(codeGenerator)
		codeGenerator[addressTra] = f"tra({futureAddress})"

		if not lexical_analyser.isKeyword("begin"):
			listeDeclaVar(lexical_analyser)
			
	else:
		listeDeclaVar(lexical_analyser)           

def listeDeclaOp(lexical_analyser):
	declaOp(lexical_analyser)
	lexical_analyser.acceptCharacter(";")
	if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function") :
		listeDeclaOp(lexical_analyser)

def declaOp(lexical_analyser):
	if lexical_analyser.isKeyword("procedure"):
		procedure(lexical_analyser)
	if lexical_analyser.isKeyword("function"):
		fonction(lexical_analyser)

def procedure(lexical_analyser):
	global mainContext
	global currentContext
	global cptAdress
	global codeGenerator
	

	lexical_analyser.acceptKeyword("procedure")
	ident = lexical_analyser.acceptIdentifier()
    # TDI - table de la procedure
	identifierTable[ident] = dict()
	currentContext = ident
	identifierTable[mainContext][currentContext] = Procedure(currentContext)
	cptAdress = 0
	# Pour savoir à quel ligne début la procédure
	addressInstruction[ident] = len(codeGenerator)

	# ---
	logger.debug("Name of procedure : "+ident)
	   
	partieFormelle(lexical_analyser)

	lexical_analyser.acceptKeyword("is")
	corpsProc(lexical_analyser)

	codeGenerator.append("retourProc()")
       

def fonction(lexical_analyser):
	global mainContext
	global currentContext
	global cptAdress
	global codeGenerator

	lexical_analyser.acceptKeyword("function")
	ident = lexical_analyser.acceptIdentifier()
	# TDI - table de la fonction
	identifierTable[ident] = dict()
	currentContext = ident
	identifierTable[mainContext][currentContext] = Fonction(currentContext)
	cptAdress = 0
	# Pour savoir à quel ligne débute la fonction
	addressInstruction[ident] = len(codeGenerator)

	# ---
	logger.debug("Name of function : "+ident)
	
	partieFormelle(lexical_analyser)

	lexical_analyser.acceptKeyword("return")
	type = nnpType(lexical_analyser)
	identifierTable[mainContext][currentContext].setType(type)
		
	lexical_analyser.acceptKeyword("is")
	corpsFonct(lexical_analyser)

	# codeGenerator.append("retourFonct()")


def corpsProc(lexical_analyser):
	global mainContext
	global currentContext
	global cptAdress

	if not lexical_analyser.isKeyword("begin"):
		partieDeclaProc(lexical_analyser)
	lexical_analyser.acceptKeyword("begin")
	suiteInstr(lexical_analyser)
	lexical_analyser.acceptKeyword("end")
	# TDI - fin table procedure
	currentContext = mainContext
	cptAdress = 0
	# ---

def corpsFonct(lexical_analyser):
	global mainContext
	global currentContext
	global cptAdress

	if not lexical_analyser.isKeyword("begin"):
		partieDeclaProc(lexical_analyser)
	lexical_analyser.acceptKeyword("begin")
	suiteInstrNonVide(lexical_analyser)
	lexical_analyser.acceptKeyword("end")
	# TDI - fin table procedure
	currentContext = mainContext
	localAdress = 0 # ?
	# ---

def partieFormelle(lexical_analyser):
	global mainContext
	global currentContext
	global listParam
	listParam = []
	lexical_analyser.acceptCharacter("(")
	if not lexical_analyser.isCharacter(")"):
		listeSpecifFormelles(lexical_analyser)
	lexical_analyser.acceptCharacter(")")
	# TDI - ajout des parametres
	identifierTable[mainContext][currentContext].setParams(listParam)
	listParam = []
	# ---

def listeSpecifFormelles(lexical_analyser):
	specif(lexical_analyser)
	if not lexical_analyser.isCharacter(")"):
		lexical_analyser.acceptCharacter(";")
		listeSpecifFormelles(lexical_analyser)

def specif(lexical_analyser):
	global listVar
	global cptAdress
	global listParam
	listVar = []

	listeIdent(lexical_analyser)
	lexical_analyser.acceptCharacter(":")
	modeParam = Mode.MODE_IN # défaut
	if lexical_analyser.isKeyword("in"):
		modeParam = mode(lexical_analyser)
				
	type = nnpType(lexical_analyser)
	# TDI - ajout des parametres
	for ident in listVar:
		identifierTable[currentContext][ident] = Variable(ident,type,cptAdress)
		identifierTable[currentContext][ident].initialise = True
		listParam.append(Parametre(type,modeParam))
		cptAdress+=1
	listVar = []
	# ---

def mode(lexical_analyser):
	lexical_analyser.acceptKeyword("in")
	if lexical_analyser.isKeyword("out"):
		lexical_analyser.acceptKeyword("out")
		logger.debug("in out parameter") 
		return Mode.MODE_INOUT               
	else:
		logger.debug("in parameter")
		return Mode.MODE_IN

def nnpType(lexical_analyser):
	if lexical_analyser.isKeyword("integer"):
		lexical_analyser.acceptKeyword("integer")
		logger.debug("integer type")
		return Types.TYPE_INTEGER
	elif lexical_analyser.isKeyword("boolean"):
		lexical_analyser.acceptKeyword("boolean")
		logger.debug("boolean type")  
		return Types.TYPE_BOOLEAN              
	else:
		logger.error("Unknown type found <"+ lexical_analyser.get_value() +">!")
		raise AnaSynException("Fonction 'mode' : Unknown type found <"+ lexical_analyser.get_value() +">!")
		

def partieDeclaProc(lexical_analyser):
	listeDeclaVar(lexical_analyser)
	

def listeDeclaVar(lexical_analyser):
	declaVar(lexical_analyser)
	if lexical_analyser.isIdentifier():
		listeDeclaVar(lexical_analyser)

def declaVar(lexical_analyser):
	global listVar
	global cptAdress
	global currentContext
	global codeGenerator
	listVar = []

	listeIdent(lexical_analyser)

	# Réservation de n emplacements pour len(listVar) variables
	n = len(listVar)
	if n != 0:
		codeGenerator.append(f"reserver({n})")

	lexical_analyser.acceptCharacter(":")
	logger.debug("now parsing type...")
	type = nnpType(lexical_analyser)
	lexical_analyser.acceptCharacter(";")
	# TDI - ajout des variables
	for ident in listVar:
		identifierTable[currentContext][ident] = Variable(ident,type,cptAdress)
		cptAdress+=1
	listVar = []
	# ---

def listeIdent(lexical_analyser):
	global cptAdress
	global currentContext

	ident = lexical_analyser.acceptIdentifier()

	logger.debug("identifier found: "+str(ident))
	listVar.append(ident)

	if lexical_analyser.isCharacter(","):
		lexical_analyser.acceptCharacter(",")
		listeIdent(lexical_analyser)

def suiteInstrNonVide(lexical_analyser):
	instr(lexical_analyser)
	if lexical_analyser.isCharacter(";"):
		lexical_analyser.acceptCharacter(";")
		suiteInstrNonVide(lexical_analyser)

def suiteInstr(lexical_analyser):
	if not lexical_analyser.isKeyword("end"):
		suiteInstrNonVide(lexical_analyser)

def instr(lexical_analyser):		
	global codeGenerator
	global mainContext
	global currentContext
	global callName
	global currentParam
	global listePeParam
	
	
	if lexical_analyser.isKeyword("while"):
		boucle(lexical_analyser)
	elif lexical_analyser.isKeyword("if"):
		altern(lexical_analyser)
	elif lexical_analyser.isKeyword("get") or lexical_analyser.isKeyword("put"):
		es(lexical_analyser)
	elif lexical_analyser.isKeyword("return"):
		retour(lexical_analyser)
	elif lexical_analyser.isIdentifier():
		ident = lexical_analyser.acceptIdentifier()
		if lexical_analyser.isSymbol(":="):				
			# affectation
			lexical_analyser.acceptSymbol(":=")

			adIdent = identifierTable[currentContext][ident].adresse
			ident_type = identifierTable[currentContext][ident].type
			identifierTable[currentContext][ident].initialise = True
			# Variable
			if (currentContext != mainContext):
				args = identifierTable[mainContext][currentContext].args
				if (len(args) > 0 and (adIdent < len(args)) and (args[adIdent].mode == Mode.MODE_INOUT)):
					# MODE INOUT
					codeGenerator.append(f"empilerParam({adIdent})")
				else:
					# MODE IN ou variable local
					codeGenerator.append(f"empilerAd({adIdent})")
			else:
				# Variable global
				codeGenerator.append(f"empiler({adIdent})")
			exp_type, ident = expression(lexical_analyser)

			if (ident_type != exp_type):
				logger.error("Affectation of a variable with a wrong type : "+str(ident_type)+" != "+str(exp_type))
				raise AnaSynException("Fonction 'instr' :  Affectation of a variable with a wrong type : expected "+str(exp_type)+", given "+str(ident_type))
			codeGenerator.append("affectation()")
			logger.debug("parsed affectation")
		elif lexical_analyser.isCharacter("("):
			# Appel d'une fonction ou d'une procédure
			callName = ident
			# On commence le comptage à 0
			currentParam = 0
			lexical_analyser.acceptCharacter("(")
			codeGenerator.append("reserverBloc()")
			listePeResult = 0
			if not lexical_analyser.isCharacter(")"):
				# Pour avoir le nombre de paramètres à faire passer dans la fonction ou procédure
				listePeResult = listePe(lexical_analyser)
			
			liste_args = identifierTable[mainContext][ident].args
			
			len_args = len(identifierTable[mainContext][ident].args)
			
			if len_args != len(listePeParam):
				logger.error("wrong number of parameters")
				raise AnaSynException("number of patameters expected for "+str(ident)+" : "+str(len_args)+
				 " | number of parameters given : "+str(len(listePeParam)))
			test = True
			i = 0
			while (test) and (i < len_args):
				if (liste_args[i].type != listePeParam[i]):
					logger.error("Type of given parameter is incorrect")
					test = False
					raise AnaSynException("Difference for parameter n° "+str(i)+" expected type : "+str(liste_args[i].type)+" given type : "+ str(listePeParam[i]))
				i = i+1
		
			listePeParam = []


			#===========================================
			lexical_analyser.acceptCharacter(")")
			# Saut vers la première ligne de l'appel fonction ou procédure avec listePeResult paramètres
			codeGenerator.append(f"traStat({addressInstruction[ident]},{listePeResult})")
			# Fin de l'appel fonction
			callName = ""
			logger.debug("parsed procedure call")
		else:
			logger.error("Expecting procedure call or affectation!")
			raise AnaSynException("Fonction 'instr' : Expecting procedure call or affectation!")
		
	else:
		logger.error("Unknown Instruction <"+ lexical_analyser.get_value() +">!")
		raise AnaSynException("Fonction 'instr' : Unknown Instruction <"+ lexical_analyser.get_value() +">!")


'''def listePe(lexical_analyser):
	expression(lexical_analyser)
	if lexical_analyser.isCharacter(","):
		lexical_analyser.acceptCharacter(",")
		return 1 + listePe(lexical_analyser)
	else:
		return 1 '''


def listePe(lexical_analyser):
	type1,_ = expression(lexical_analyser)
	listePeParam.append(type1)
	if lexical_analyser.isCharacter(","):
		lexical_analyser.acceptCharacter(",")
		# 1 paramètre + listePe paramètres
		return 1 + listePe(lexical_analyser)
	else:
		# Cas de base 1 seul paramètre
		return 1
	

# =================================
# Need of preventing semantic errors
def expression(lexical_analyser):
	global codeGenerator

	logger.debug("parsing expression: " + str(lexical_analyser.get_value()))

	type1, ident = exp1(lexical_analyser)
	#if there is an "or", exp1 has to be a boolean
	if lexical_analyser.isKeyword("or"):
		if type1 != Types.TYPE_BOOLEAN :
			logger.error("or : expected boolean")
			raise AnaSynException("Fonction 'expression' : or : expected boolean")
		lexical_analyser.acceptKeyword("or")
		type2, ident = exp1(lexical_analyser)
		if type2 != Types.TYPE_BOOLEAN :
			logger.error("or : booléen attendu")
			raise AnaSynException("Fonction 'expression' : or : expected boolean")
		codeGenerator.append("ou()")
	
	# vérification sémantique : on vérifie qu'une variable déclarée est bien initialisée 
	if ident != None and ident!=currentContext and identifierTable[currentContext][ident].initialise == False : 
		logger.error("variable is not initialized")
		raise AnaSynException("variable is not initialized")
	
	return type1, ident
		
		
def exp1(lexical_analyser):
	global codeGenerator
	
	logger.debug("parsing exp1")
	
	type1, ident = exp2(lexical_analyser)
	#if there is an "and", exp1 has to be a boolean
	if lexical_analyser.isKeyword("and"):
		if type1 != Types.TYPE_BOOLEAN :
			logger.error("and : expected boolean")
			raise AnaSynException("Fonction 'exp1' : and : expected boolean")
		lexical_analyser.acceptKeyword("and")
		type2, ident = exp2(lexical_analyser)
		codeGenerator.append("et()")
		if type2 != Types.TYPE_BOOLEAN :
			logger.error("and : expected boolean")
			raise AnaSynException("Fonction 'exp1' : and : expected boolean")

	return type1, ident
		
def exp2(lexical_analyser):
	global codeGenerator
	logger.debug("parsing exp2")
		
	type1, ident = exp3(lexical_analyser)
	if	lexical_analyser.isSymbol("<") or \
		lexical_analyser.isSymbol("<=") or \
		lexical_analyser.isSymbol(">") or \
		lexical_analyser.isSymbol(">="):
		if type1 != Types.TYPE_INTEGER :
			logger.error("comparison : expected integer")
			raise AnaSynException("Fonction 'exp2' : comparison : expected integer")
		operation = opRel(lexical_analyser)
		# Pour avoir inf(), infeg(), sup(), supeg() après exp3
		type2, ident = exp3(lexical_analyser)
		if type2 != Types.TYPE_INTEGER :
			logger.error("comparison : expected integer")
			raise AnaSynException("Fonction 'exp2' : comparison : expected integer")
		codeGenerator.append(operation)
		return Types.TYPE_BOOLEAN, ident
	elif lexical_analyser.isSymbol("=") or \
		lexical_analyser.isSymbol("/="):
		#if type1 != Types.TYPE_INTEGER :
			#logger.error("comparaison : entier attendu")
			#raise AnaSynException("L 441 - Fonction 'exp2' : comparaison : entier attendu")
		operation = opRel(lexical_analyser)
		# Pour avoir egal(), diff() après exp3
		type2, ident = exp3(lexical_analyser)
		if type1 != type2 :
			logger.error("comparison :  variables compared must by of the same type")
			raise AnaSynException("Fonction 'exp2' : comparison :  variables compared must by of the same type")
		codeGenerator.append(operation)
		return Types.TYPE_BOOLEAN, ident

	return type1, ident
	
def opRel(lexical_analyser):
	logger.debug("parsing relationnal operator: " + lexical_analyser.get_value())
		
	if	lexical_analyser.isSymbol("<"):
		lexical_analyser.acceptSymbol("<")
		return "inf()"
		
	elif lexical_analyser.isSymbol("<="):
		lexical_analyser.acceptSymbol("<=")
		return "infeg()"

	elif lexical_analyser.isSymbol(">"):
		lexical_analyser.acceptSymbol(">")
		return "sup()"

	elif lexical_analyser.isSymbol(">="):
		lexical_analyser.acceptSymbol(">=")
		return "supeg()"

	elif lexical_analyser.isSymbol("="):
		lexical_analyser.acceptSymbol("=")
		return "egal()"

	elif lexical_analyser.isSymbol("/="):
		lexical_analyser.acceptSymbol("/=")
		return "diff()"
	else:
		msg = "Fonction 'opRel' : Unknown relationnal operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def exp3(lexical_analyser):
	global codeGenerator

	logger.debug("parsing exp3")
	type1, ident = exp4(lexical_analyser)
	if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-"):
		if type1 != Types.TYPE_INTEGER :
			logger.error("expression : expected integer")
			raise AnaSynException("Fonction 'exp3' : expression : expected integer")
		operation = opAdd(lexical_analyser)
		# Pour avoir add(), sous() après exp4
		type2, ident = exp4(lexical_analyser)
		if type2 != Types.TYPE_INTEGER :
			logger.error("expression : expected integer")
			raise AnaSynException("Fonction 'exp3' : expression : expected integer")
		codeGenerator.append(operation)

	return type1, ident

def opAdd(lexical_analyser):
	logger.debug("parsing additive operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("+"):
		lexical_analyser.acceptCharacter("+")
		return "add()"
				
	elif lexical_analyser.isCharacter("-"):
		lexical_analyser.acceptCharacter("-")
		return "sous()"
				
	else:
		msg = "Fonction 'opAdd' : Unknown additive operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def exp4(lexical_analyser):
	global codeGenerator

	logger.debug("parsing exp4")
		
	type1, ident = prim(lexical_analyser)
	if lexical_analyser.isCharacter("*") or lexical_analyser.isCharacter("/"):
		if type1 != Types.TYPE_INTEGER :
			logger.error("operation : expected integer")
			raise AnaSynException("Fonction 'exp4' : operation : expected integer")
		operation = opMult(lexical_analyser)
		# Pour avoir mult() et div() après le prim
		type2, ident = prim(lexical_analyser)
		if type2 != Types.TYPE_INTEGER :
			logger.error("operation : expected integer")
			raise AnaSynException("Fonction 'exp4' : operation : expected integer")
		codeGenerator.append(operation)

	return type1, ident

def opMult(lexical_analyser):
	logger.debug("parsing multiplicative operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("*"):
		lexical_analyser.acceptCharacter("*")
		return "mult()"
			 
	elif lexical_analyser.isCharacter("/"):
		lexical_analyser.acceptCharacter("/")
		return "div()"

	else:
		msg = "Fonction 'opMult' : Unknown multiplicative operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def prim(lexical_analyser):
	global codeGenerator
	logger.debug("parsing prim")
	operation = ""

	if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-") or lexical_analyser.isKeyword("not"):
		operation = opUnaire(lexical_analyser)
		# Pour avoir moins(), non() après l'exécution de elemPrim si besoin
	type1, ident = elemPrim(lexical_analyser)
	if (operation != "" and operation != None):
		# "" si on n'a pas eu de +, - ou not. None si on a eu un +
		codeGenerator.append(operation)

	if operation == "not" and type1 != Types.TYPE_BOOLEAN :
		logger.error("not : expected boolean")
		raise AnaSynException("Fonction 'prim' : not : expected boolean")
	if (operation == "+" or operation == "-") and type1 != Types.TYPE_INTEGER :
		logger.error("expression : expected boolean")
		raise AnaSynException("Fonction 'prim' : expression : expected boolean")
	
	# vérification sémantique : on vérifie qu'une variable déclarée est bien initialisée 
	if ident != None and ident!=currentContext  and identifierTable[currentContext][ident].initialise == False : 
		logger.error("variable is not initialized")
		raise AnaSynException("variable is not initialized")

	return type1, ident
	
def opUnaire(lexical_analyser):
	logger.debug("parsing unary operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("+"):
		lexical_analyser.acceptCharacter("+")
		return "add()"
		# Pas de retour dans le cas où on aurait a:= +5
				
	elif lexical_analyser.isCharacter("-"):
		lexical_analyser.acceptCharacter("-")
		return "moins()"
				
	elif lexical_analyser.isKeyword("not"):
		lexical_analyser.acceptKeyword("not")
		return "non()"
				
	else:
		msg = "Fonction 'opUnaire' : Unknown additive operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def elemPrim(lexical_analyser):
	global codeGenerator
	global currentContext
	global listePeParam
	ident = None

	#if str(lexical_analyser.get_value()) == "" : 
		#logger.error("variable is not initialized")
		#raise AnaSynException("variable is not initialized")
	global callName
	global currentParam


	logger.debug("parsing elemPrim: " + str(lexical_analyser.get_value()))
	if lexical_analyser.isCharacter("("):
		lexical_analyser.acceptCharacter("(")
		type, ident = expression(lexical_analyser)
		lexical_analyser.acceptCharacter(")")
	elif lexical_analyser.isInteger() :
		valeur(lexical_analyser)
		type = Types.TYPE_INTEGER
	elif lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
		valeur(lexical_analyser)
		type = Types.TYPE_BOOLEAN
	elif lexical_analyser.isIdentifier():
		ident = lexical_analyser.acceptIdentifier()
		if lexical_analyser.isCharacter("("):			
			# Appel d'une fonction ou d'une procédure
			lexical_analyser.acceptCharacter("(")
			codeGenerator.append("reserverBloc()")
			if not lexical_analyser.isCharacter(")"):
				# Pour avoir le nombre de paramètres
				listePeResult = listePe(lexical_analyser)
			# Saut vers la première ligne de l'appel fonction ou procédure avec listePeResult paramètres
			codeGenerator.append(f"traStat({addressInstruction[ident]},{listePeResult})")
			lexical_analyser.acceptCharacter(")")
			logger.debug("parsed procedure call")
			
			logger.debug("Call to function: " + ident)
			type = identifierTable[mainContext][ident].type

			liste_args = identifierTable[mainContext][ident].args
			
			len_args = len(identifierTable[mainContext][ident].args)
			
			if len_args != len(listePeParam):
				logger.error("wrong number of parameters")
				raise AnaSynException("number of patameters expected for "+str(ident)+" : "+str(len_args)+
				 " | number of parameters given : "+str(len(listePeParam)))
			test = True
			i = 0
			while (test) and (i < len_args):
				if (liste_args[i].type != listePeParam[i]):
					logger.error("Type of given parameter is incorrect")
					test = False
					raise AnaSynException("Difference for parameter n° "+str(i)+" expected type : "+str(liste_args[i].type)+" given type : "+ str(listePeParam[i]))
				i = i+1
		
			listePeParam = []


		else:
			adIdent = identifierTable[currentContext][ident].adresse

			# Variable
			if (currentContext != mainContext):
				args = identifierTable[mainContext][currentContext].args
				args = identifierTable[mainContext][currentContext].args
				if (len(args) > 0 and (adIdent < len(args)) and (args[adIdent].mode == Mode.MODE_INOUT)):
					#MODE INOUT
					codeGenerator.append(f"empilerParam({adIdent})")
				else:
					#MODE IN ou variable local
					codeGenerator.append(f"empilerAd({adIdent})")
			else:
				# Variable global
				codeGenerator.append(f"empiler({adIdent})")
			if (callName != ""):
				# Lors d'un appel d'une procédure, si un paramètre est en IN OUT, on ne fait pas de valeurPile()
				# Car on passe par adresse
				mode = identifierTable[currentContext][callName].args[currentParam].mode
				if (mode != Mode.MODE_INOUT):
					# Paramètre en IN dans une procédure
					codeGenerator.append("valeurPile()")
			else:
				codeGenerator.append("valeurPile()")
			logger.debug("Use of an identifier as an expression: " + ident)
		# ...
			type = identifierTable[currentContext][ident].type
	else:
		logger.error("Unknown Value!")
		raise AnaSynException("Fonction 'elemPrim' : Unknown Value!")
	
	currentParam += 1
	return type, ident
	
	

def valeur(lexical_analyser):
	global codeGenerator

	if lexical_analyser.isInteger():
		entier = lexical_analyser.acceptInteger()
		codeGenerator.append(f"empiler({entier})")
		logger.debug("integer value: " + str(entier))
		return "integer"
	elif lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
		vtype = valBool(lexical_analyser)
		return vtype
	else:
		logger.error("Unknown Value! Expecting an integer or a boolean value!")
		raise AnaSynException("Fonction 'valeur' : Unknown Value ! Expecting an integer or a boolean value!")

def valBool(lexical_analyser):
	global codeGenerator
	
	if lexical_analyser.isKeyword("true"):
		lexical_analyser.acceptKeyword("true")	
		codeGenerator.append("empiler(1)")
		logger.debug("boolean true value")
	else:
		logger.debug("boolean false value")
		lexical_analyser.acceptKeyword("false")	
		codeGenerator.append("empiler(0)")
		
	return "boolean"

def es(lexical_analyser):
	global codeGenerator
	global currentContext
	global mainContext
	
	logger.debug("parsing E/S instruction: " + lexical_analyser.get_value())

	# appel à get()
	if lexical_analyser.isKeyword("get"):
		lexical_analyser.acceptKeyword("get")
		lexical_analyser.acceptCharacter("(")
		ident = lexical_analyser.acceptIdentifier()
		# Test to verify the type of the variable because get only works
		# with integers
		type_variable = identifierTable[mainContext][ident].type
		if type_variable == Types.TYPE_BOOLEAN :
			logger.error("get() does not apply to booleans")
			raise AnaSynException("Fonction 'es' : get() does not apply to booleans")
		
		lexical_analyser.acceptCharacter(")")

		# On initialise dans la table des identificateurs, pour ne pas retourner d'erreurs au niveau du get. En effet, le get permet d'initialiser la variable
		identifierTable[currentContext][ident].initialise = True 

		adIdent = identifierTable[currentContext][ident].adresse
		# Variable
		if (currentContext != mainContext):
			args = identifierTable[mainContext][currentContext].args
			if (len(args) > 0 and (adIdent < len(args)) and (args[adIdent].mode == Mode.MODE_INOUT)):
				#MODE INOUT
				codeGenerator.append(f"empilerParam({adIdent})")
			else:
				#MODE IN ou variable local
				codeGenerator.append(f"empilerAd({adIdent})")
		else:
			# Variable global
			codeGenerator.append(f"empiler({adIdent})")
		codeGenerator.append("get()")

		logger.debug("Call to get "+ident)

	# appel à put()
	elif lexical_analyser.isKeyword("put"):
		lexical_analyser.acceptKeyword("put")
		lexical_analyser.acceptCharacter("(")
		type, ident = expression(lexical_analyser)
		lexical_analyser.acceptCharacter(")")

		# Test to verify the type of the variable because put only works
		# with integer
		if type != Types.TYPE_INTEGER :
			logger.error("put() only applies to integer")
			raise AnaSynException("Fonction 'es' : wrong type given : put() only applies to integer")
		
		#if identifierTable[currentContext][ident].initialise == False : 
			#logger.error("variable is not initialized")
			#raise AnaSynException("variable is not initialized")
		
		codeGenerator.append("put()")
		logger.debug("Call to put")

	else:
		logger.error("Unknown E/S instruction!")
		raise AnaSynException("Fonction 'es' : Unknown E/S instruction!")

def boucle(lexical_analyser):
	global codeGenerator

	logger.debug("parsing while loop: ")
	lexical_analyser.acceptKeyword("while")

	futureAddress1 = len(codeGenerator)

	type, ident = expression(lexical_analyser)
	if type != Types.TYPE_BOOLEAN :
		logger.error("while : booléen attendu")
		raise AnaSynException("Fonction 'boucle' : while : booléen attendu")

	futureAddress2 = 0
	codeGenerator.append(f"tze({futureAddress2})")
	tempInstructionIndex = len(codeGenerator) - 1
	lexical_analyser.acceptKeyword("loop")
	suiteInstr(lexical_analyser)

	codeGenerator.append(f"tra({futureAddress1})")
	futureAddress2 = len(codeGenerator)
	codeGenerator[tempInstructionIndex] = f"tze({futureAddress2})"

	lexical_analyser.acceptKeyword("end")
	logger.debug("end of while loop ")

def altern(lexical_analyser):
	global codeGenerator
	
	logger.debug("parsing if: ")
	lexical_analyser.acceptKeyword("if")

	type, ident = expression(lexical_analyser)
	
	if (type != Types.TYPE_BOOLEAN):
		logger.error("Wrong condition in the alternative")
		raise AnaSynException("Fonction 'altern' : Wrong condition in the alternative")
	futureAddress1 = 0
	codeGenerator.append(f"tze({futureAddress1})")
	tempInstructionIndex1 = len(codeGenerator) - 1
	   
	lexical_analyser.acceptKeyword("then")
	suiteInstr(lexical_analyser)

	# Change s'il y a un else après
	futureAddress1 = len(codeGenerator) 
	# fString to input values of the variables
	codeGenerator[tempInstructionIndex1] = f"tze({futureAddress1})"

	if lexical_analyser.isKeyword("else"):
		lexical_analyser.acceptKeyword("else")
		futureAddress2 = 0
		codeGenerator.append(f"tra({futureAddress2})")
		tempInstructionIndex2 = len(codeGenerator) - 1

		# tze
		codeGenerator[tempInstructionIndex1] = f"tze({len(codeGenerator)})"

		suiteInstr(lexical_analyser)
		futureAddress2 = len(codeGenerator)  
		codeGenerator[tempInstructionIndex2] = f"tra({futureAddress2})"
    

	lexical_analyser.acceptKeyword("end")
	logger.debug("end of if")

def retour(lexical_analyser):
	global codeGenerator
	
	logger.debug("parsing return instruction")
	lexical_analyser.acceptKeyword("return")
	expression(lexical_analyser)
	codeGenerator.append("retourFonct()")

	

########################################################################				 	
def main():
	 
	parser = argparse.ArgumentParser(description='Do the syntactical analysis of a NNP program.')
	parser.add_argument('inputfile', type=str, nargs=1, help='name of the input source file')
	parser.add_argument('-o', '--outputfile', dest='outputfile', action='store', \
				default="", help='name of the output file (default: stdout)')
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
	parser.add_argument('-d', '--debug', action='store_const', const=logging.DEBUG, \
				default=logging.INFO, help='show debugging info on output')
	parser.add_argument('-p', '--pseudo-code', action='store_const', const=True, default=False, \
				help='enables output of pseudo-code instead of assembly code')
	parser.add_argument('--show-ident-table', action='store_true', \
				help='shows the final identifiers table')
	args = parser.parse_args()

	filename = args.inputfile[0]
	f = None
	try:
		f = open(filename, 'r')
	except:
		print("Error: can\'t open input file!")
		return
		
	outputFilename = args.outputfile
	
	  # create logger      
	LOGGING_LEVEL = args.debug
	logger.setLevel(LOGGING_LEVEL)
	ch = logging.StreamHandler()
	ch.setLevel(LOGGING_LEVEL)
	#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(CustomFormatter.CustomFormatter())
	logger.addHandler(ch)

	

	if args.pseudo_code:
		True#
	else:
		False#

	lexical_analyser = analex.LexicalAnalyser()
	
	lineIndex = 0
	for line in f:
		line = line.rstrip('\r\n')
		lexical_analyser.analyse_line(lineIndex, line)
		lineIndex = lineIndex + 1
	f.close()

	# launch the analysis of the program
	lexical_analyser.init_analyser()
	try:
		program(lexical_analyser)
	except AnaSynException as inst:
		exception_type, exception_object, exception_traceback = sys.exc_info()
		print("Compilation failed.")
		while (exception_traceback.tb_next!=None):
			exception_traceback = exception_traceback.tb_next
		print("l.",exception_traceback.tb_lineno," - ",inst)
		return 
	
	if args.show_ident_table :
			print("------ IDENTIFIER TABLE ------")
			for (context,dict) in identifierTable.items():
				print("%s :"%(context))
				for (key,value) in dict.items():
					print("\t%s : %s"%(key,value))
			#print(str(identifierTable))
			print("------ END OF IDENTIFIER TABLE ------")

	if outputFilename != "":
			try:
					output_file = open(outputFilename, 'w')
					# output_file.write('\n'.join(codeGenerator))
			except:
					print("Error: can\'t open output file!")
					return
	else:
			output_file = sys.stdout

	# Outputs the generated code to a file
	for instr in codeGenerator :
		output_file.write("%s\n" % instr)
		
	if outputFilename != "":
			output_file.close() 

########################################################################				 

if __name__ == "__main__":
	main() 
