import json

with open("entrada.json", "r") as arquivo:
    dados = json.load(arquivo)

instrucoes = dados["text"]

for instrucao in instrucoes:
    numero = int(instrucao, 16)
    binario = format(numero, "032b")

    opcode = int(binario[0:6], 2)

    #TIPO R
    if opcode == 0:
        rs    = int(binario[6:11], 2)
        rt    = int(binario[11:16], 2)
        rd    = int(binario[16:21], 2)
        shamt = int(binario[21:26], 2)
        funct = int(binario[26:32], 2)

        if funct == 32:
            assembly = f"add ${rd}, ${rs}, ${rt}"
        elif funct == 33:
            assembly = f"addu ${rd}, ${rs}, ${rt}"
        elif funct == 36:
            assembly = f"and ${rd}, ${rs}, ${rt}"
        elif funct == 26:
            assembly = f"div ${rs}, ${rt}"
        elif funct == 27:
            assembly = f"divu ${rs}, ${rt}"
        elif funct == 8:
            assembly = f"jr ${rs}"
        elif funct == 16:
            assembly = f"mfhi ${rd}"
        elif funct == 18:
            assembly = f"mflo ${rd}"
        elif funct == 24:
            assembly = f"mult ${rs}, ${rt}"
        elif funct == 25:
            assembly = f"multu ${rs}, ${rt}"
        elif funct == 39:
            assembly = f"nor ${rd}, ${rs}, ${rt}"
        elif funct == 37:
            assembly = f"or ${rd}, ${rs}, ${rt}"
        elif funct == 0:
            assembly = f"sll ${rd}, ${rt}, {shamt}"
        elif funct == 4:
            assembly = f"sllv ${rd}, ${rt}, ${rs}"
        elif funct == 42:
            assembly = f"slt ${rd}, ${rs}, ${rt}"
        elif funct == 3:
            ssembly = f"sra ${rd}, ${rt}, {shamt}"
        elif funct == 7:
            assembly = f"srav ${rd}, ${rt}, ${rs}"
        elif funct == 2:
            assembly = f"srl ${rd}, ${rt}, {shamt}"
        elif funct == 6:
            assembly = f"srlv ${rd}, ${rt}, ${rs}"
        elif funct == 34:
            assembly = f"sub ${rd}, ${rs}, ${rt}"
        elif funct == 35:
            assembly = f"subu ${rd}, ${rs}, ${rt}"
        elif funct == 38:
            assembly = f"xor ${rd}, ${rs}, ${rt}"
        elif funct == 12:
            assembly = "syscall"
        
    #TIPO J
    elif opcode == 2:

        target = int(binario[6:32], 2)

        assembly = f"j {target}"

    elif opcode == 3:

        target = int(binario[6:32], 2)

        texto = f"jal {target}"
        
    #TIPO I
    else:
        rs = int(binario[6:11], 2)
        rt = int(binario[11:16], 2)
        imm_binario = binario[16:32]

        #ver se os números sao negativos no imM
        if imm_binario[0] == "1":
            imm = int(imm_binario, 2) - 2**16
        else:
            imm = int(imm_binario, 2)