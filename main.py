import json

with open("entrada.json", "r") as arquivo:
    dados = json.load(arquivo)

instrucoes = dados["text"]

# Registradores
regs = {f"${i}": 0 for i in range(32)}

regs["pc"] = 0
regs["hi"] = 0
regs["lo"] = 0

# Configuração inicial
if "config" in dados and "regs" in dados["config"]:
    for reg, valor in dados["config"]["regs"].items():
        regs[reg] = valor

resultados = []

# Execução
for instrucao in instrucoes:

    numero = int(instrucao, 16)
    binario = format(numero, "032b")

    opcode = int(binario[0:6], 2)

    regs["pc"] += 4

    # Tipo R
    if opcode == 0:

        rs = int(binario[6:11], 2)
        rt = int(binario[11:16], 2)
        rd = int(binario[16:21], 2)
        shamt = int(binario[21:26], 2)
        funct = int(binario[26:32], 2)

        # ADD
        if funct == 32:

            assembly = f"add ${rd}, ${rs}, ${rt}"

            regs[f"${rd}"] = (
                regs[f"${rs}"] +
                regs[f"${rt}"]
            )

        # ADDU
        elif funct == 33:

            assembly = f"addu ${rd}, ${rs}, ${rt}"

            regs[f"${rd}"] = (
                regs[f"${rs}"] +
                regs[f"${rt}"]
            )

        # AND
        elif funct == 36:

            assembly = f"and ${rd}, ${rs}, ${rt}"

            regs[f"${rd}"] = (
                regs[f"${rs}"] &
                regs[f"${rt}"]
            )

        # DIV
        elif funct == 26:

            assembly = f"div ${rs}, ${rt}"

            val_rs = regs[f"${rs}"]
            val_rt = regs[f"${rt}"]

            if val_rt != 0:
                regs["lo"] = val_rs // val_rt
                regs["hi"] = val_rs % val_rt

        # DIVU
        elif funct == 27:

            assembly = f"divu ${rs}, ${rt}"

            val_rs = regs[f"${rs}"] & 0xFFFFFFFF
            val_rt = regs[f"${rt}"] & 0xFFFFFFFF

            if val_rt != 0:
                regs["lo"] = val_rs // val_rt
                regs["hi"] = val_rs % val_rt

        # JR
        elif funct == 8:

            assembly = f"jr ${rs}"

        # MFHI
        elif funct == 16:

            assembly = f"mfhi ${rd}"

            regs[f"${rd}"] = regs["hi"]

        # MFLO
        elif funct == 18:

            assembly = f"mflo ${rd}"

            regs[f"${rd}"] = regs["lo"]

        # MULT
        elif funct == 24:

            assembly = f"mult ${rs}, ${rt}"

            resultado_mult = (
                regs[f"${rs}"] *
                regs[f"${rt}"]
            )

            regs["lo"] = resultado_mult & 0xFFFFFFFF
            regs["hi"] = (resultado_mult >> 32) & 0xFFFFFFFF

        # MULTU
        elif funct == 25:

            assembly = f"multu ${rs}, ${rt}"

            val_rs = regs[f"${rs}"] & 0xFFFFFFFF
            val_rt = regs[f"${rt}"] & 0xFFFFFFFF

            resultado_mult = val_rs * val_rt

            regs["lo"] = resultado_mult & 0xFFFFFFFF
            regs["hi"] = (resultado_mult >> 32) & 0xFFFFFFFF

        # NOR
        elif funct == 39:

            assembly = f"nor ${rd}, ${rs}, ${rt}"

            regs[f"${rd}"] = ~(
                regs[f"${rs}"] |
                regs[f"${rt}"]
            )

        # OR
        elif funct == 37:

            assembly = f"or ${rd}, ${rs}, ${rt}"

            regs[f"${rd}"] = (
                regs[f"${rs}"] |
                regs[f"${rt}"]
            )

        # SLL
        elif funct == 0:

            assembly = f"sll ${rd}, ${rt}, {shamt}"

            regs[f"${rd}"] = (
                regs[f"${rt}"] << shamt
            )

        # SLLV
        elif funct == 4:

            assembly = f"sllv ${rd}, ${rt}, ${rs}"

            deslocamento = regs[f"${rs}"] & 0x1F

            regs[f"${rd}"] = (
                regs[f"${rt}"] << deslocamento
            )

        # SLT
        elif funct == 42:

            assembly = f"slt ${rd}, ${rs}, ${rt}"

            if regs[f"${rs}"] < regs[f"${rt}"]:
                regs[f"${rd}"] = 1
            else:
                regs[f"${rd}"] = 0

        # SRA
        elif funct == 3:

            assembly = f"sra ${rd}, ${rt}, {shamt}"

            regs[f"${rd}"] = (
                regs[f"${rt}"] >> shamt
            )

        # SRAV
        elif funct == 7:

            assembly = f"srav ${rd}, ${rt}, ${rs}"

            deslocamento = regs[f"${rs}"] & 0x1F

            regs[f"${rd}"] = (
                regs[f"${rt}"] >> deslocamento
            )

        # SRL
        elif funct == 2:

            assembly = f"srl ${rd}, ${rt}, {shamt}"

            valor = regs[f"${rt}"] & 0xFFFFFFFF

            regs[f"${rd}"] = valor >> shamt

        # SRLV
        elif funct == 6:

            assembly = f"srlv ${rd}, ${rt}, ${rs}"

            deslocamento = regs[f"${rs}"] & 0x1F

            valor = regs[f"${rt}"] & 0xFFFFFFFF

            regs[f"${rd}"] = (
                valor >> deslocamento
            )

        # SUB
        elif funct == 34:

            assembly = f"sub ${rd}, ${rs}, ${rt}"

            regs[f"${rd}"] = (
                regs[f"${rs}"] -
                regs[f"${rt}"]
            )

        # SUBU
        elif funct == 35:

            assembly = f"subu ${rd}, ${rs}, ${rt}"

            regs[f"${rd}"] = (
                regs[f"${rs}"] -
                regs[f"${rt}"]
            )

        # XOR
        elif funct == 38:

            assembly = f"xor ${rd}, ${rs}, ${rt}"

            regs[f"${rd}"] = (
                regs[f"${rs}"] ^
                regs[f"${rt}"]
            )

        # SYSCALL
        elif funct == 12:

            assembly = "syscall"

        else:

            assembly = (
                f"instrução desconhecida "
                f"(funct {funct})"
            )

    # Tipo J
    elif opcode == 2:

        target = int(binario[6:32], 2)

        assembly = f"j {target}"

    elif opcode == 3:

        target = int(binario[6:32], 2)

        assembly = f"jal {target}"

    # Tipo I
    else:

        rs = int(binario[6:11], 2)
        rt = int(binario[11:16], 2)

        imm_binario = binario[16:32]

        # Imediato com sinal
        if imm_binario[0] == "1":

            imm_com_sinal = (
                int(imm_binario, 2) -
                (2 ** 16)
            )

        else:

            imm_com_sinal = int(
                imm_binario,
                2
            )

        # Imediato sem sinal
        imm_sem_sinal = int(
            imm_binario,
            2
        )

        # ADDI
        if opcode == 8:

            assembly = (
                f"addi ${rt}, ${rs}, "
                f"{imm_com_sinal}"
            )

            regs[f"${rt}"] = (
                regs[f"${rs}"] +
                imm_com_sinal
            )

        # ADDIU
        elif opcode == 9:

            assembly = (
                f"addiu ${rt}, ${rs}, "
                f"{imm_com_sinal}"
            )

            regs[f"${rt}"] = (
                regs[f"${rs}"] +
                imm_com_sinal
            )

        # SLTI
        elif opcode == 10:

            assembly = (
                f"slti ${rt}, ${rs}, "
                f"{imm_com_sinal}"
            )

            if regs[f"${rs}"] < imm_com_sinal:
                regs[f"${rt}"] = 1
            else:
                regs[f"${rt}"] = 0

        # ANDI
        elif opcode == 12:

            assembly = (
                f"andi ${rt}, ${rs}, "
                f"{imm_sem_sinal}"
            )

            regs[f"${rt}"] = (
                regs[f"${rs}"] &
                imm_sem_sinal
            )

        # ORI
        elif opcode == 13:

            assembly = (
                f"ori ${rt}, ${rs}, "
                f"{imm_sem_sinal}"
            )

            regs[f"${rt}"] = (
                regs[f"${rs}"] |
                imm_sem_sinal
            )

        # XORI
        elif opcode == 14:

            assembly = (
                f"xori ${rt}, ${rs}, "
                f"{imm_sem_sinal}"
            )

            regs[f"${rt}"] = (
                regs[f"${rs}"] ^
                imm_sem_sinal
            )

        # LUI
        elif opcode == 15:

            assembly = (
                f"lui ${rt}, "
                f"{imm_sem_sinal}"
            )

            regs[f"${rt}"] = (
                imm_sem_sinal << 16
            )

        # BEQ
        elif opcode == 4:

            assembly = (
                f"beq ${rs}, ${rt}, "
                f"{imm_com_sinal}"
            )

        # BNE
        elif opcode == 5:

            assembly = (
                f"bne ${rs}, ${rt}, "
                f"{imm_com_sinal}"
            )

        # LW
        elif opcode == 35:

            assembly = (
                f"lw ${rt}, "
                f"{imm_com_sinal}(${rs})"
            )

        # SW
        elif opcode == 43:

            assembly = (
                f"sw ${rt}, "
                f"{imm_com_sinal}(${rs})"
            )

        else:

            assembly = (
                f"instrução desconhecida "
                f"(opcode {opcode})"
            )

    # $0 permanece zero
    regs["$0"] = 0

    # Registradores diferentes de zero
    regs_saida = {}

    for reg, valor in regs.items():

        if valor != 0:
            regs_saida[reg] = valor

    resultado = {
        "hex": instrucao,
        "text": assembly,
        "regs": regs_saida,
        "mem": {},
        "stdout": ""
    }

    resultados.append(resultado)

    print(
        f"{instrucao} -> {assembly}"
    )

# Salvar saída
with open("saida.json", "w") as arquivo:

    json.dump(
        resultados,
        arquivo,
        indent=4
    )

print("\nExecução finalizada!")
print("Arquivo saida.json criado com sucesso.")