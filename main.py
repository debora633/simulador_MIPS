import json


# Abrir o arquivo de entrada
with open("entrada.json", "r") as arquivo:
    dados = json.load(arquivo)


#pegar as instruções em hexadecimal
instrucoes = dados["text"]

#inicio registradores 
regs = {f"${i}": 0 for i in range(32)}
regs["pc"] = 0
regs["hi"] = 0
regs["lo"] = 0

#valores iniciais em config
if "config" in dados:
    for reg, valor in dados["config"]["regs"].items():
        regs[reg] = valor

resultados = []

for instrucao in instrucoes:
    numero = int(instrucao, 16)
    binario = format(numero, "032b")

    opcode = int(binario[0:6], 2)

    regs["pc"] += 4

    #TIPO R
    if opcode == 0:
        rs    = int(binario[6:11], 2)
        rt    = int(binario[11:16], 2)
        rd    = int(binario[16:21], 2)
        shamt = int(binario[21:26], 2)
        funct = int(binario[26:32], 2)

        if funct == 32:
            assembly = f"add ${rd}, ${rs}, ${rt}"
            regs[f"${rd}"] = regs[f"${rs}"] + regs[f"${rt}"]
        elif funct == 33:
            assembly = f"addu ${rd}, ${rs}, ${rt}"
            regs[f"${rd}"] = regs[f"${rs}"] + regs[f"${rt}"] ############
        elif funct == 36:
            assembly = f"and ${rd}, ${rs}, ${rt}"
            regs[f"${rd}"] = regs[f"${rs}"] & regs[f"${rt}"]
        elif funct == 26:
            assembly = f"div ${rs}, ${rt}"
            val_rs = regs[f"${rs}"] & 0xFFFFFFFF
            val_rt = regs[f"${rt}"] & 0xFFFFFFFF

            if val_rt != 0:
                regs["lo"] = val_rs // val_rt 
                regs["hi"] = val_rs % val_rt
        elif funct == 27:
            assembly = f"divu ${rs}, ${rt}"
        elif funct == 8:
            assembly = f"jr ${rs}"
        elif funct == 16:
            assembly = f"mfhi ${rd}"
            regs[f"${rd}"] = regs["hi"]
        elif funct == 18:
            assembly = f"mflo ${rd}"
            regs[f"${rd}"] = regs["lo"]
        elif funct == 24:
            assembly = f"mult ${rs}, ${rt}"
            resultado_mult = regs[f"${rs}"] * regs[f"${rt}"]
            regs["lo"] = resultado_mult & 0xFFFFFFFF
            regs["hi"] = (resultado_mult >> 32) & 0xFFFFFFFF
        elif funct == 25:
            assembly = f"multu ${rs}, ${rt}"
            val_rs = regs[f"${rs}"] & 0xFFFFFFFF
            val_rt = regs[f"${rt}"] & 0xFFFFFFFF

            resultado_mult = val_rs * val_rt

            regs["lo"] = resultado_mult & 0xFFFFFFFF
            regs["hi"] = (resultado_mult >> 32) & 0xFFFFFFFF
        elif funct == 39:
            assembly = f"nor ${rd}, ${rs}, ${rt}"
            regs[f"${rd}"] = ~(regs[f"${rs}"] | regs[f"${rt}"]) ################
        elif funct == 37:
            assembly = f"or ${rd}, ${rs}, ${rt}"
            regs[f"${rd}"] = regs[f"${rs}"] | regs[f"${rt}"]
        elif funct == 0:
            assembly = f"sll ${rd}, ${rt}, {shamt}"
        elif funct == 4:
            assembly = f"sllv ${rd}, ${rt}, ${rs}"
        elif funct == 42:
            assembly = f"slt ${rd}, ${rs}, ${rt}"
            if regs[f"${rs}"] < regs[f"${rt}"]:
                regs[f"${rd}"] = 1
            else:
                regs[f"${rd}"] = 0
        elif funct == 3:
            assembly = f"sra ${rd}, ${rt}, {shamt}"
        elif funct == 7:
            assembly = f"srav ${rd}, ${rt}, ${rs}"
        elif funct == 2:
            assembly = f"srl ${rd}, ${rt}, {shamt}"
        elif funct == 6:
            assembly = f"srlv ${rd}, ${rt}, ${rs}"
        elif funct == 34:
            assembly = f"sub ${rd}, ${rs}, ${rt}"
            regs[f"${rd}"] = regs[f"${rs}"] - regs[f"${rt}"]
        elif funct == 35:
            assembly = f"subu ${rd}, ${rs}, ${rt}"
            regs[f"${rd}"] = regs[f"${rs}"] - regs[f"${rt}"] ###################
        elif funct == 38:
            assembly = f"xor ${rd}, ${rs}, ${rt}"
            regs[f"${rd}"] = regs[f"${rs}"] ^ regs[f"${rt}"]
        elif funct == 12:
            assembly = "syscall"

        else:
            assembly = f"instrução desconhecida (funct {funct})"

    #TIPO J
    elif opcode == 2:
        target = int(binario[6:32], 2)

        assembly = f"j {target}"

    elif opcode == 3:
        target = int(binario[6:32], 2)

        assembly = f"jal {target}"

    #TIPO I
    else:
        rs = int(binario[6:11], 2)
        rt = int(binario[11:16], 2)
        imm_binario = binario[16:32]

        #ver se os números sao negativos no imM
        if imm_binario[0] == "1":
            imm_com_sinal = int(imm_binario, 2) - (2 ** 16)
        else:
            imm_com_sinal = int(imm_binario, 2)

        imm_sem_sinal = int(imm_binario, 2)

        if opcode == 8:
            assembly = f"addi ${rt}, ${rs}, {imm_com_sinal}"

        elif opcode == 9:
            assembly = f"addiu ${rt}, ${rs}, {imm_com_sinal}"

        elif opcode == 12:
            assembly = f"andi ${rt}, ${rs}, {imm_sem_sinal}"

        elif opcode == 13:
            assembly = f"ori ${rt}, ${rs}, {imm_sem_sinal}"

        elif opcode == 14:
            assembly = f"xori ${rt}, ${rs}, {imm_sem_sinal}"

        elif opcode == 10:
            assembly = f"slti ${rt}, ${rs}, {imm_com_sinal}"

        elif opcode == 15:
            assembly = f"lui ${rt}, {imm_sem_sinal}"

        elif opcode == 4:
            assembly = f"beq ${rs}, ${rt}, {imm_com_sinal}"

        elif opcode == 5:
            assembly = f"bne ${rs}, ${rt}, {imm_com_sinal}"

        elif opcode == 35:
            assembly = f"lw ${rt}, {imm_com_sinal}(${rs})"

        elif opcode == 43:
            assembly = f"sw ${rt}, {imm_com_sinal}(${rs})"

        else:
            assembly = f"instrução desconhecida (opcode {opcode})"


    #resultado da instrução
    resultado = {
        "hex": instrucao,
        "text": assembly,
        "regs": {},
        "mem": {},
        "stdout": ""
    }

    resultados.append(resultado)

    #instrução decodificada no terminal
    print(f"{instrucao} -> {assembly}")

# Salvar no arquivo saida.json
with open("saida.json", "w") as arquivo:
    json.dump(resultados, arquivo, indent=4)
