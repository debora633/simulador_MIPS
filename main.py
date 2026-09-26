import json

#valor no intervalo de 32 bits
def to_32bit_signed(val):
    val = val & 0xFFFFFFFF
    if val >= 0x80000000:
        val -= 0x100000000
    return val

#ler o arquivo de entrada
with open("entrada.json", "r") as arquivo:
    dados = json.load(arquivo)

#pegar as instruções em hexadecimal
instrucoes = dados.get("text", [])

#inicio registradores + regs do MARS
regs = [0] * 32
regs[28] = 0x10008000  
regs[29] = 0x7FFFEFFC   
pc = 0x00400000        
hi = 0
lo = 0

#sobrescrever valores iniciais com os valores de 'config.regs'
config_regs = dados.get("config", {}).get("regs", {})

#carregar valores iniciaisl dos registradores
for reg_key, val in config_regs.items():
    v = int(val, 16) if isinstance(val, str) and val.startswith("0x") else int(val)
    key_clean = reg_key.replace("$", "").lower()

    if key_clean.isdigit():
        idx = int(key_clean)
        if 0 < idx < 32:
            regs[idx] = to_32bit_signed(v)
    elif key_clean == "pc":
        pc = v
    elif key_clean == "hi":
        hi = to_32bit_signed(v)
    elif key_clean == "lo":
        lo = to_32bit_signed(v)

resultados = []

#execução das instruções
for instrucao in instrucoes:
    numero = int(instrucao, 16)
    binario = format(numero, "032b")
    opcode = int(binario[0:6], 2)
    
    assembly = ""

    # TIPO R
    if opcode == 0:
        rs    = int(binario[6:11], 2)
        rt    = int(binario[11:16], 2)
        rd    = int(binario[16:21], 2)
        shamt = int(binario[21:26], 2)
        funct = int(binario[26:32], 2)

        if funct == 32:    # add
            assembly = f"add ${rd}, ${rs}, ${rt}"
            if rd != 0: regs[rd] = to_32bit_signed(regs[rs] + regs[rt])
        elif funct == 33:  # addu
            assembly = f"addu ${rd}, ${rs}, ${rt}"
            if rd != 0: regs[rd] = to_32bit_signed(regs[rs] + regs[rt])
        elif funct == 34:  # sub
            assembly = f"sub ${rd}, ${rs}, ${rt}"
            if rd != 0: regs[rd] = to_32bit_signed(regs[rs] - regs[rt])
        elif funct == 35:  # subu
            assembly = f"subu ${rd}, ${rs}, ${rt}"
            if rd != 0: regs[rd] = to_32bit_signed(regs[rs] - regs[rt])
        elif funct == 36:  # and
            assembly = f"and ${rd}, ${rs}, ${rt}"
            if rd != 0: regs[rd] = regs[rs] & regs[rt]
        elif funct == 37:  # or
            assembly = f"or ${rd}, ${rs}, ${rt}"
            if rd != 0: regs[rd] = regs[rs] | regs[rt]
        elif funct == 38:  # xor
            assembly = f"xor ${rd}, ${rs}, ${rt}"
            if rd != 0: regs[rd] = regs[rs] ^ regs[rt]
        elif funct == 39:  # nor
            assembly = f"nor ${rd}, ${rs}, ${rt}"
            if rd != 0: regs[rd] = to_32bit_signed(~(regs[rs] | regs[rt]))
        elif funct == 42:  # slt
            assembly = f"slt ${rd}, ${rs}, ${rt}"
            if rd != 0: regs[rd] = 1 if regs[rs] < regs[rt] else 0
        elif funct == 0:   # sll
            assembly = f"sll ${rd}, ${rt}, {shamt}"
            if rd != 0: regs[rd] = to_32bit_signed(regs[rt] << shamt)
        elif funct == 2:   # srl
            assembly = f"srl ${rd}, ${rt}, {shamt}"
            u_rt = regs[rt] & 0xFFFFFFFF
            if rd != 0: regs[rd] = to_32bit_signed(u_rt >> shamt)
        elif funct == 3:   # sra
            assembly = f"sra ${rd}, ${rt}, {shamt}"
            if rd != 0: regs[rd] = to_32bit_signed(regs[rt] >> shamt)
        elif funct == 4:   # sllv
            assembly = f"sllv ${rd}, ${rt}, ${rs}"
            shift = regs[rs] & 0x1F
            if rd != 0: regs[rd] = to_32bit_signed(regs[rt] << shift)
        elif funct == 6:   # srlv
            assembly = f"srlv ${rd}, ${rt}, ${rs}"
            shift = regs[rs] & 0x1F
            u_rt = regs[rt] & 0xFFFFFFFF
            if rd != 0: regs[rd] = to_32bit_signed(u_rt >> shift)
        elif funct == 7:   # srav
            assembly = f"srav ${rd}, ${rt}, ${rs}"
            shift = regs[rs] & 0x1F
            if rd != 0: regs[rd] = to_32bit_signed(regs[rt] >> shift)
        elif funct == 16:  # mfhi
            assembly = f"mfhi ${rd}"
            if rd != 0: regs[rd] = hi
        elif funct == 18:  # mflo
            assembly = f"mflo ${rd}"
            if rd != 0: regs[rd] = lo
        elif funct == 24:  # mult
            assembly = f"mult ${rs}, ${rt}"
            prod = regs[rs] * regs[rt]
            lo = to_32bit_signed(prod & 0xFFFFFFFF)
            hi = to_32bit_signed((prod >> 32) & 0xFFFFFFFF)
        elif funct == 25:  # multu
            assembly = f"multu ${rs}, ${rt}"
            u_rs = regs[rs] & 0xFFFFFFFF
            u_rt = regs[rt] & 0xFFFFFFFF
            prod = u_rs * u_rt
            lo = to_32bit_signed(prod & 0xFFFFFFFF)
            hi = to_32bit_signed((prod >> 32) & 0xFFFFFFFF)
        elif funct == 26:  # div
            assembly = f"div ${rs}, ${rt}"
            if regs[rt] != 0:
                lo = to_32bit_signed(int(regs[rs] / regs[rt]))
                hi = to_32bit_signed(regs[rs] - (lo * regs[rt]))
        elif funct == 27:  # divu
            assembly = f"divu ${rs}, ${rt}"
            u_rs = regs[rs] & 0xFFFFFFFF
            u_rt = regs[rt] & 0xFFFFFFFF
            if u_rt != 0:
                lo = to_32bit_signed(u_rs // u_rt)
                hi = to_32bit_signed(u_rs % u_rt)
        elif funct == 8:
            assembly = f"jr ${rs}"
        elif funct == 12:
            assembly = "syscall"
        else:
            assembly = f"instrução desconhecida (funct {funct})"

    # TIPO J
    elif opcode == 2:
        target = int(binario[6:32], 2)
        assembly = f"j {target}"
    elif opcode == 3:
        target = int(binario[6:32], 2)
        assembly = f"jal {target}"

    # TIPO I
    else:
        rs = int(binario[6:11], 2)
        rt = int(binario[11:16], 2)
        imm_binario = binario[16:32]

        imm_com_sinal = int(imm_binario, 2) - (2 ** 16) if imm_binario[0] == "1" else int(imm_binario, 2)
        imm_sem_sinal = int(imm_binario, 2)

        if opcode == 1:
            if rt == 0:
                assembly = f"bltz ${rs}, {imm_com_sinal}"
            elif rt == 1:
                assembly = f"bgez ${rs}, {imm_com_sinal}"
        elif opcode == 4:
            assembly = f"beq ${rs}, ${rt}, {imm_com_sinal}"
        elif opcode == 5:
            assembly = f"bne ${rs}, ${rt}, {imm_com_sinal}"
        elif opcode == 6:
            assembly = f"blez ${rs}, {imm_com_sinal}"
        elif opcode == 7:
            assembly = f"bgtz ${rs}, {imm_com_sinal}"
        elif opcode == 8:      # addi
            assembly = f"addi ${rt}, ${rs}, {imm_com_sinal}"
            if rt != 0: regs[rt] = to_32bit_signed(regs[rs] + imm_com_sinal)
        elif opcode == 9:    # addiu
            assembly = f"addiu ${rt}, ${rs}, {imm_com_sinal}"
            if rt != 0: regs[rt] = to_32bit_signed(regs[rs] + imm_com_sinal)
        elif opcode == 10:   # slti
            assembly = f"slti ${rt}, ${rs}, {imm_com_sinal}"
            if rt != 0: regs[rt] = 1 if regs[rs] < imm_com_sinal else 0
        elif opcode == 12:   # andi
            assembly = f"andi ${rt}, ${rs}, {imm_sem_sinal}"
            if rt != 0: regs[rt] = regs[rs] & imm_sem_sinal
        elif opcode == 13:   # ori
            assembly = f"ori ${rt}, ${rs}, {imm_sem_sinal}"
            if rt != 0: regs[rt] = regs[rs] | imm_sem_sinal
        elif opcode == 14:   # xori
            assembly = f"xori ${rt}, ${rs}, {imm_sem_sinal}"
            if rt != 0: regs[rt] = regs[rs] ^ imm_sem_sinal
        elif opcode == 15:   # lui
            assembly = f"lui ${rt}, {imm_sem_sinal}"
            if rt != 0: regs[rt] = to_32bit_signed(imm_sem_sinal << 16)
        elif opcode == 32:
            assembly = f"lb ${rt}, {imm_com_sinal}(${rs})"
        elif opcode == 35:
            assembly = f"lw ${rt}, {imm_com_sinal}(${rs})"
        elif opcode == 36:
            assembly = f"lbu ${rt}, {imm_com_sinal}(${rs})"
        elif opcode == 40:
            assembly = f"sb ${rt}, {imm_com_sinal}(${rs})"
        elif opcode == 43:
            assembly = f"sw ${rt}, {imm_com_sinal}(${rs})"
        else:
            assembly = f"instrução desconhecida (opcode {opcode})"

    pc += 4
    regs[0] = 0

    #montagem do dicionário de registradores diferentes de 0 
    regs_dicionario = {}
    for i in range(32):
        if regs[i] != 0:
            regs_dicionario[f"${i}"] = regs[i]
    if hi != 0:
        regs_dicionario["hi"] = hi
    if lo != 0:
        regs_dicionario["lo"] = lo
    if pc != 0:
        regs_dicionario["pc"] = pc

    resultado = {
        "hex": instrucao,
        "text": assembly,
        "regs": regs_dicionario,
        "mem": {},
        "stdout": ""
    }

    resultados.append(resultado)

    print(f"{instrucao} -> {assembly}")

#saída em JSON
with open("saida.json", "w") as arquivo:
    json.dump(resultados, arquivo, indent=4)