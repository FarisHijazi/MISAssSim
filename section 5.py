 #Checking if it belongs to ALUI (Opcode 32 - 35)
    elif(args[0] == "add"  or args[0] == "and"  or args[0] == "or"   or args[0] == "xor" 
      or args[0] == "nadd" or args[0] == "cand" or args[0] == "cor"  or args[0] == "xnor"
      or args[0] == "sub"  or args[0] == "andc" or args[0] == "orc" 
      or args[0] == "eq"   or args[0] == "ne"   or args[0] == "lt"   or args[0] == "ge" 
      or args[0] == "ltu"  or args[0] == "geu"  or args[0] == "min"  or args[0] == "max" 
      or args[0] == "gt"   or args[0] == "le"   or args[0] == "gtu"  or args[0] == "leu"):
        if(len(args)!=5) :
            raise Exception(' Incorrect Number of arguments')
        opcode, ra, rb, func, imm = asmtointALUI(args,opcode, ra, rb, rc, rd, func, imm, p)



		
#Checking if it belongs to RET (Opcode 36)
    elif(args[0] == "retadd" or args[0] == "retnadd"  or args[0] == "retand"   or args[0] == "retcand"
      or args[0] == "retor"  or args[0] == "retcor"   or args[0] == "retxor"   or args[0] == "retset"
      or args[0] == "reteq"  or args[0] == "retne"    or args[0] == "retlt"    or args[0] == "retge"
      or args[0] == "retltu" or args[0] == "retgeu"   or args[0] == "retmin"   or args[0] == "retmax" ):
        if(len(args)!=4) :
            raise Exception(' Incorrect Number of arguments')
        opcode, ra, rb, func, imm = asmtointRET(args,opcode, ra, rb, rc, rd, func, imm, p)
		
		
		
#Checking if it belongs to NOP (Opcode 0)         ############## REVIEW , I have done nothing with this NOP
    elif(args[0] == "nop" ):
        if(len(args)!=2) :
            raise Exception(' Incorrect Number of arguments')
        opcode, imm = asmtointNOP(args,opcode, ra, rb, rc, rd, func, imm, p)		
		
		
		
		
#Checking if it belongs to SHIFT (Opcode 37)
    elif(args[0] == "shlr" or args[0] == "salr"  or args[0] == "ror"   or args[0] == "mul"
      or args[0] == "div"  or args[0] == "mod"   or args[0] == "divu"  or args[0] == "modu"
      or args[0] == "shl"  or args[0] == "shr"   or args[0] == "sar"   or args[0] == "rol"
      or args[0] == "extr" or args[0] == "extru" or args[0] == "ext"   or args[0] == "extu"
      or args[0] == "insz" ):
        if(len(args)!=4) :
            raise Exception(' Incorrect Number of arguments')
        opcode, ra, rb, func, imm, p = asmtointSHIFT(args,opcode, ra, rb, rc, rd, func, imm, p)		




 #Checking if it belongs to ALU (Opcode 40)
    elif(args[0] == "add" or args[0] == "nadd" or args[0] == "and"   or args[0] == "cand" 
	  or args[0] == "or"  or args[0] == "cor"  or args[0] == "xor"   or args[0] == "xnor" 
      or args[0] == "eq"  or args[0] == "ne"   or args[0] == "lt"    or args[0] == "ge" 
	  or args[0] == "ltu" or args[0] == "geu"  or args[0] == "min"   or args[0] == "max" 
	  or args[0] == "shl" or args[0] == "shr"  or args[0] == "sar"   or args[0] == "ror" 
	  or args[0] == "mul"
	  or args[0] == "div" or args[0] == "mod"  or args[0] == "divu"  or args[0] == "modu"
	  or args[0] == "adds" 
	  or args[0] == "nadds" 
	  or args[0] == "sub" or args[0] == "andc" or args[0] == "orc"   or args[0] == "gt" 
	  or args[0] == "le"  or args[0] == "gtu"  or args[0] == "leu" ):
        if(len(args)!=4) :
            raise Exception(' Incorrect Number of arguments')
        opcode, ra, rb, func, x, rd, n = asmtointALU(args,opcode, ra, rb, rc, rd, func, imm, p)
		
		
		
		
		
		
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################



def asmtointALUI(args,opcode, ra, rb, rc, rd, func, imm, p):
    rb  = int(args[1][1:])
    ra  = int(args[2][1:])
	imm = int(args[3])
	
	
	# Opcode 32
    if  (args[0] == "add"):
		opcode = 32
		func   = 0
	elif(args[0] == "nadd"):
        opcode = 32
		func   = 1	
	elif(args[0] == "and"):
        opcode = 32
		func   = 2		
	elif(args[0] == "cand"):
        opcode = 32
		func   = 3	
		
		
	# Opcode 33	
	elif(args[0] == "or"):
        opcode = 33
		func   = 4	
	elif(args[0] == "cor"):
        opcode = 33
		func   = 5		
	elif(args[0] == "xor"):
        opcode = 33
		func   = 6	
	elif(args[0] == "set"):
        opcode = 33
		func   = 7	
		imm = int(args[2])
		
		
	# Opcode 34
	elif(args[0] == "eq"):
        opcode = 34
		func   = 8	
	elif(args[0] == "ne"):
        opcode = 34
		func   = 9		
	elif(args[0] == "lt"):
        opcode = 34
		func   = 10	
	elif(args[0] == "ge"):
        opcode = 34
		func   = 11	
		
		
	# Opcode 35
	elif(args[0] == "ltu"):
        opcode = 35
		func   = 12	
	elif(args[0] == "geu"):
        opcode = 35
		func   = 13		
	elif(args[0] == "min"):
        opcode = 35
		func   = 14	
	elif(args[0] == "max"):
        opcode = 35
		func   = 15		
		
		
	# Pseudo-Instructions for ALUI
	elif(args[0] == "sub"):  # uses add , -Imm   
        opcode = 32
		func   = 0
		imm    = - Imm
	elif(args[0] == "andc"): # uses add , ~Imm
        opcode = 32
		func   = 0		
		imm    = - Imm
	elif(args[0] == "orc"):  # uses or ,  ~Imm
        opcode = 33
		func   = 4	
		imm    = - Imm
	elif(args[0] == "xnor"): # uses xor , ~Imm
        opcode = 33
		func   = 6		
		imm    = - Imm
	elif(args[0] == "mov"):  # uses or ,  Imm = 0
        opcode = 33
		func   = 4
		imm    = 0
	elif(args[0] == "neg"): # uses nadd , Imm = 0
        opcode = 32
		func   = 1		
		imm    = 0
	elif(args[0] == "not"):  # uses cor ,  Imm = 0
        opcode = 33
		func   = 5
		imm    = 0		
		
		
	# Compare Pseudo-Instructions for ALUI
	elif(args[0] == "gt"):   # uses ge  , Imm = Imm + 1
        opcode = 32
		func   = 0
		imm    = imm + 1
	elif(args[0] == "le"):   # uses lt  , Imm = Imm + 1
        opcode = 32
		func   = 0		
		imm    = imm + 1
	elif(args[0] == "gtu"):  # uses geu , Imm = Imm + 1
        opcode = 33
		func   = 4	
		imm    = imm + 1
	elif(args[0] == "leu"):  # uses ltu , Imm = Imm + 1
        opcode = 33
		func   = 4	
		imm    = imm + 1	
		
		
		
	return opcode, ra, rb, func, imm
	
	
	
	
	
	
def asmtointRET(args,opcode, ra, rb, rc, rd, func, imm, p):  
    ra     = int(args[1][1:])
    rb     = int(args[2][1:])
	imm    = int(args[3])
	opcode = 36
	
	
	if  (args[0] == "retadd"):
		func   = 0
	elif(args[0] == "retnadd"):
		func   = 1	
	elif(args[0] == "retand"):
		func   = 2		
	elif(args[0] == "retcand"):
		func   = 3	
	elif(args[0] == "retor"):
		func   = 4	
	elif(args[0] == "retcor"):
		func   = 5		
	elif(args[0] == "retxor"):
		func   = 6	
	elif(args[0] == "retset"):
		func   = 7	
		imm = int(args[2])
	elif(args[0] == "reteq"):
		func   = 8	
	elif(args[0] == "retne"):
		func   = 9		
	elif(args[0] == "retlt"):
		func   = 10	
	elif(args[0] == "retge"):
		func   = 11	
	elif(args[0] == "retltu"):
		func   = 12	
	elif(args[0] == "retgeu"):
		func   = 13		
	elif(args[0] == "retmin"):
		func   = 14	
	elif(args[0] == "retmax"):
		func   = 15		
		
		
		
	return opcode, ra, rb, func, imm	
	
	
	
	
	
	
def asmtointSHIFT(args,opcode, ra, rb, rc, rd, func, imm, p):
    rb     = int(args[1][1:])
    ra     = int(args[2][1:])
	opcode = 37
	
	
    if  (args[0] == "shlr"):
		func   = 0
		imm_L  = int(args[3])
	    imm_R  = int(args[4])
	elif(args[0] == "shlr"): 
		func   = 1	
		imm_L  = int(args[3])
	    imm_R  = int(args[4])
	elif(args[0] == "salr"):
		func   = 2
		imm_L  = int(args[3])
	    imm_R  = int(args[4])
	elif(args[0] == "ror"):        # only 3 args, Imm_R is the 3rd arg
		func   = 3	
		imm_R  = int(args[3])  
	elif(args[0] == "mul"):        # only 3 args, Imm   is the 3rd arg
		func   = 8	
		imm    = int(args[3])
	elif(args[0] == "div"):        # only 3 args, Imm   is the 3rd arg
		func   = 12	
		imm    = int(args[3])
	elif(args[0] == "mod"):        # only 3 args, Imm   is the 3rd arg
		func   = 13		
		imm    = int(args[3])
	elif(args[0] == "divu"):       # only 3 args, Imm   is the 3rd arg
		func   = 14	
		imm    = int(args[3])
	elif(args[0] == "modu"):       # only 3 args, Imm   is the 3rd arg
		func   = 15	
        imm    = int(args[3])		
		
		
	# Pseudo-Instructions for SHIFT	      
	elif(args[0] == "shl"):   # uses shlr, Imm_R = 0
		func   = 0
		imm_L  = int(args[3])
	elif(args[0] == "shr"):   # uses shlr, Imm_L = 0
		func   = 0
	    imm_R  = int(args[3])
	elif(args[0] == "sar"):   # uses salr, Imm_L = 0
		func   = 2	
	    imm_R  = int(args[3])
	elif(args[0] == "rol"):   # uses ror,  Imm_R = 64 - Imm_R
		func   = 3	
		imm_R  = int(args[3])  		
	elif(args[0] == "extr"):  # uses salr, Imm_L = 64 - Imm_L - p,  Imm_R = 64 - Imm_L
		func   = 2	
		imm_L  = int(args[3])
	    p      = int(args[4])		
	elif(args[0] == "extru"): # uses shlr, Imm_L = 64 - Imm_L - p
		func   = 0
		imm_L  = int(args[3])
	    p      = int(args[4])		
	elif(args[0] == "ext"):   # uses salr, Imm_L = 64 - Imm_L,  Imm_R = 64 - Imm_L
		func   = 2	
		imm_L  = int(args[3])
	elif(args[0] == "extu"):  # uses shlr, Imm_L = 3rd arg
		func   = 0	
		imm_L  = int(args[3])		
	elif(args[0] == "insz"):  # uses salr, Imm_L = 3rd arg
		func   = 2	
        imm_L  = int(args[3])
	    p      = int(args[4])			
		
		
	return opcode, ra, rb, func, imm, p		




def asmtointALU(args,opcode, ra, rb, rc, rd, func, imm, p):
    rd     = int(args[1][1:])
	ra     = int(args[2][1:])
    rb     = int(args[3][1:])
	opcode = 40
	
	
	#  x = 0
    if  (args[0] == "add"):
		func = 0
		x    = 0
	elif(args[0] == "nadd"): 
		func = 1
		x    = 0
	elif(args[0] == "and"):
		func = 2
		x    = 0
	elif(args[0] == "cand"):
		func = 3
		x    = 0
	elif(args[0] == "or"):
		func = 4
		x    = 0
	elif(args[0] == "cor"):
		func = 5
		x    = 0
	elif(args[0] == "xor"):
		func = 6
		x    = 0
	elif(args[0] == "xnor"):
		func = 7
		x    = 0
	elif(args[0] == "eq"):
		func = 8
		x    = 0
	elif(args[0] == "ne"):
		func = 9
		x    = 0
	elif(args[0] == "lt"):
		func = 10
		x    = 0
	elif(args[0] == "ge"):
		func = 11
		x    = 0
	elif(args[0] == "ltu"):
		func = 12
		x    = 0
	elif(args[0] == "geu"):
		func = 13
		x    = 0
	elif(args[0] == "min"):
		func = 14
		x    = 0
	elif(args[0] == "max"):
		func = 15
		x    = 0
		
	
	# x = 1
	elif(args[0] == "shl"):
		func = 0
		x    = 1
	elif(args[0] == "shr"):
		func = 1
		x    = 1
	elif(args[0] == "sar"):
		func = 2
		x    = 1
	elif(args[0] == "ror"):
		func = 3
		x    = 1
	elif(args[0] == "mul"):
		func = 8
		x    = 1
	elif(args[0] == "div"):
		func = 12
		x    = 1	
	elif(args[0] == "mod"):
		func = 13
		x    = 1
	elif(args[0] == "divu"):
		func = 14
		x    = 1
	elif(args[0] == "modu"):
		func = 15
		x    = 1		
			
	# x = 2	
	elif(args[0] == "adds"):
		n    = int(args[4][1:])     # n = 0 ~ 15      
		x    = 2	

	# x = 3
	elif(args[0] == "nadds"):
		n    = int(args[4][1:])     # n = 0 ~ 15         
		x    = 3		


	# Pseudo-Instructions for ALU	             
	elif(args[0] ==  "sub"):   # uses nadd, swaps ra & rb
		func   = 1
		x      = 0	
	    ra     = int(args[3])
        rb     = int(args[2])
	elif(args[0] == "andc"):   # uses cand, swaps ra & rb
		func   = 1
		x      = 0	
	    ra     = int(args[3])
        rb     = int(args[2])
	elif(args[0] ==  "orc"):   # uses cor,  swaps ra & rb
		func   = 1
		x      = 0	
	    ra     = int(args[3])
        rb     = int(args[2])
	elif(args[0] ==  "gt" ):   # uses lt,   swaps ra & rb
		func   = 1
		x      = 0	
	    ra     = int(args[3])
        rb     = int(args[2])
	elif(args[0] ==  "le" ):   # uses ge,   swaps ra & rb
		func   = 1
		x      = 0	
	    ra     = int(args[3])
        rb     = int(args[2])
	elif(args[0] ==  "gtu"):   # uses ltu,  swaps ra & rb
		func   = 1
		x      = 0	
	    ra     = int(args[3])
        rb     = int(args[2])
	elif(args[0] ==  "leu"):   # uses geu,  swaps ra & rb
		func   = 1	
		x      = 0	
	    ra     = int(args[3])	
        rb     = int(args[2])	
		
		
	return opcode, ra, rb, func, x, rd, n
		
		
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################


	def inttohex(opcode, ra, rb, rc, rd, x, func, imm, p):
    
    # start copying after this line
	    elif (opcode == 32 or opcode == 33 or opcode == 34 or
         	  opcode == 35 or opcode == 36 or opcode == 37):
        opstr = format(opcode, '06b')
        rastr = format(ra,     '05b')
        rbstr = format(rb,     '05b')
		fnstr = format(func,   '04b')
        imstr = format(imm,    '12b')
        instruction = opstr + rastr + rbstr + fnstr + imstr

	    elif (opcode == 40):
        opstr = format(opcode, '06b')
        rastr = format(ra,     '05b')
        rbstr = format(rb,     '05b')
		fnstr = format(func,   '04b')
		x_str = format(x,      '02b')
        rdstr = format(imm,    '05b')
        instruction = opstr + rastr + rbstr + fnstr + x_str + rdstr	
		
		
		
		
