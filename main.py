import json

def to_32bit_signed(val):
    val = val & 0xFFFFFFFF
    if val >= 0x80000000:
        val -= 0x100000000
    return val

# Gerenciador de memória orientado a bytes (Little-Endian)
memoria_global = {}

def read_byte(addr):
    return memoria_global.get(addr & 0xFFFFFFFF, 0)

def write_byte(addr, val):
    addr = addr & 0xFFFFFFFF
    v = val & 0xFF
    if v != 0:
        memoria_global[addr] = v
    elif addr in memoria_global:
        del memoria_global[addr]

def read_word(addr):
    b0 = read_byte(addr)
    b1 = read_byte(addr + 1)
    b2 = read_byte(addr + 2)
    b3 = read_byte(addr + 3)
    return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)

def write_word(addr, val):
    val = val & 0xFFFFFFFF
    write_byte(addr, val & 0xFF)
    write_byte(addr + 1, (val >> 8) & 0xFF)
    write_byte(addr + 2, (val >> 16) & 0xFF)
    write_byte(addr + 3, (val >> 24) & 0xFF)

# Carrega o arquivo de entrada JSON
with open("entrada.json", "r") as arquivo:
    dados = json.load(arquivo)

instrucoes = dados.get("text", [])
config = dados.get("config", {})
config_regs = config.get("regs", {})
config_mem = config.get("mem", {})

# Iniciar registradores, PC, HI e LO
regs = [0] * 32
regs[28] = 0x10008000  # $gp
regs[29] = 0x7FFFEFFC  # $sp
pc = 0x00400000        # Valor padrão do PC
hi = 0
lo = 0

# Inicializa registradores vindos do config
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

# Inicializa memória vinda do config
for mem_addr_str, val in config_mem.items():
    m_addr = int(mem_addr_str, 16) if str(mem_addr_str).startswith("0x") else int(mem_addr_str)
    v = int(val, 16) if isinstance(val, str) and str(val).startswith("0x") else int(val)
    if v > 255 or v < 0:
        write_word(m_addr, v)
    else:
        write_byte(m_addr, v)

start_pc = pc
resultados = []

# Laço principal de execução das instruções
while True:
    indice = (pc - start_pc) // 4
    
    # Condição de parada: PC aponta para fora da lista de instruções
    if indice < 0 or indice >= len(instrucoes):
        break
        
    instrucao = instrucoes[indice]
    numero = int(instrucao, 16)
    hex_str = f"0x{numero:08x}"
    binario = format(numero, "032b")
    opcode = int(binario[0:6], 2)
    
    assembly = ""
    stdout_text = ""
    
    # Salva o PC da instrução atual para cálculos relativos e avança 4
    pc_atual = pc
    pc += 4

    # Tipo R
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
        elif funct == 43:  # sltu
            assembly = f"sltu ${rd}, ${rs}, ${rt}"
            u_rs = regs[rs] & 0xFFFFFFFF
            u_rt = regs[rt] & 0xFFFFFFFF
            if rd != 0: regs[rd] = 1 if u_rs < u_rt else 0
        elif funct == 0:   # sll
            assembly = f"sll ${rd}, ${rt}, {shamt}"
            if rd != 0: regs[rd] = to_32bit_signed((regs[rt] & 0xFFFFFFFF) << shamt)
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
            if rd != 0: regs[rd] = to_32bit_signed((regs[rt] & 0xFFFFFFFF) << shift)
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
            u_prod = prod & 0xFFFFFFFFFFFFFFFF
            lo = to_32bit_signed(u_prod & 0xFFFFFFFF)
            hi = to_32bit_signed((u_prod >> 32) & 0xFFFFFFFF)
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
        elif funct == 8:   # jr
            assembly = f"jr ${rs}"
            pc = regs[rs]
        elif funct == 12:  # syscall
            assembly = "syscall"
            v0 = regs[2]
            if v0 == 1:    # print_int
                stdout_text = str(regs[4])
            elif v0 == 4:  # print_string
                str_bytes = []
                str_addr = regs[4] & 0xFFFFFFFF
                while True:
                    ch = read_byte(str_addr)
                    if ch == 0:
                        break
                    str_bytes.append(chr(ch))
                    str_addr += 1
                stdout_text = "".join(str_bytes)
        else:
            assembly = f"instrução desconhecida (funct {funct})"

    # Tipo J
    elif opcode == 2:      # j
        target = int(binario[6:32], 2)
        target_addr = (pc & 0xF0000000) | (target << 2)
        assembly = f"j {target_addr}"
        pc = target_addr
    elif opcode == 3:      # jal
        target = int(binario[6:32], 2)
        target_addr = (pc & 0xF0000000) | (target << 2)
        assembly = f"jal {target_addr}"
        regs[31] = pc
        pc = target_addr

    # Tipo I
    else:
        rs = int(binario[6:11], 2)
        rt = int(binario[11:16], 2)
        imm_binario = binario[16:32]

        imm_com_sinal = int(imm_binario, 2) - (2 ** 16) if imm_binario[0] == "1" else int(imm_binario, 2)
        imm_sem_sinal = int(imm_binario, 2)
        
        # Endereço base para loads/stores
        end_memoria = (regs[rs] + imm_com_sinal) & 0xFFFFFFFF

        if opcode == 1:
            if rt == 0:    # bltz
                assembly = f"bltz ${rs}, {imm_com_sinal}"
                if regs[rs] < 0: pc = pc_atual + 4 + (imm_com_sinal * 4)
            elif rt == 1:  # bgez
                assembly = f"bgez ${rs}, {imm_com_sinal}"
                if regs[rs] >= 0: pc = pc_atual + 4 + (imm_com_sinal * 4)
        elif opcode == 4:  # beq
            assembly = f"beq ${rs}, ${rt}, {imm_com_sinal}"
            if regs[rs] == regs[rt]: pc = pc_atual + 4 + (imm_com_sinal * 4)
        elif opcode == 5:  # bne
            assembly = f"bne ${rs}, ${rt}, {imm_com_sinal}"
            if regs[rs] != regs[rt]: pc = pc_atual + 4 + (imm_com_sinal * 4)
        elif opcode == 6:  # blez
            assembly = f"blez ${rs}, {imm_com_sinal}"
            if regs[rs] <= 0: pc = pc_atual + 4 + (imm_com_sinal * 4)
        elif opcode == 7:  # bgtz
            assembly = f"bgtz ${rs}, {imm_com_sinal}"
            if regs[rs] > 0: pc = pc_atual + 4 + (imm_com_sinal * 4)
        elif opcode == 8:      # addi
            assembly = f"addi ${rt}, ${rs}, {imm_com_sinal}"
            if rt != 0: regs[rt] = to_32bit_signed(regs[rs] + imm_com_sinal)
        elif opcode == 9:    # addiu
            assembly = f"addiu ${rt}, ${rs}, {imm_com_sinal}"
            if rt != 0: regs[rt] = to_32bit_signed(regs[rs] + imm_com_sinal)
        elif opcode == 10:   # slti
            assembly = f"slti ${rt}, ${rs}, {imm_com_sinal}"
            if rt != 0: regs[rt] = 1 if regs[rs] < imm_com_sinal else 0
        elif opcode == 11:   # sltiu
            assembly = f"sltiu ${rt}, ${rs}, {imm_com_sinal}"
            u_rs = regs[rs] & 0xFFFFFFFF
            u_imm = imm_com_sinal & 0xFFFFFFFF
            if rt != 0: regs[rt] = 1 if u_rs < u_imm else 0
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
            
        # LOADS e STORES
        elif opcode == 32:   # lb
            assembly = f"lb ${rt}, {imm_com_sinal}(${rs})"
            if rt != 0: 
                b = read_byte(end_memoria)
                b = b - 256 if b >= 128 else b
                regs[rt] = to_32bit_signed(b)
        elif opcode == 33:   # lh
            assembly = f"lh ${rt}, {imm_com_sinal}(${rs})"
            if rt != 0:
                b0 = read_byte(end_memoria)
                b1 = read_byte(end_memoria + 1)
                val = b0 | (b1 << 8)
                val = val - 65536 if val >= 32768 else val
                regs[rt] = to_32bit_signed(val)
        elif opcode == 35:   # lw
            assembly = f"lw ${rt}, {imm_com_sinal}(${rs})"
            if rt != 0: regs[rt] = to_32bit_signed(read_word(end_memoria))
        elif opcode == 36:   # lbu
            assembly = f"lbu ${rt}, {imm_com_sinal}(${rs})"
            if rt != 0: regs[rt] = read_byte(end_memoria) & 0xFF
        elif opcode == 37:   # lhu
            assembly = f"lhu ${rt}, {imm_com_sinal}(${rs})"
            if rt != 0:
                b0 = read_byte(end_memoria)
                b1 = read_byte(end_memoria + 1)
                regs[rt] = (b0 | (b1 << 8)) & 0xFFFF
        elif opcode == 40:   # sb
            assembly = f"sb ${rt}, {imm_com_sinal}(${rs})"
            write_byte(end_memoria, regs[rt])
        elif opcode == 41:   # sh
            assembly = f"sh ${rt}, {imm_com_sinal}(${rs})"
            write_byte(end_memoria, regs[rt] & 0xFF)
            write_byte(end_memoria + 1, (regs[rt] >> 8) & 0xFF)
        elif opcode == 43:   # sw
            assembly = f"sw ${rt}, {imm_com_sinal}(${rs})"
            write_word(end_memoria, regs[rt])
        else:
            assembly = f"instrução desconhecida (opcode {opcode})"

    # Garante que $0 é sempre 0
    regs[0] = 0

    # Monta o dicionário de registradores e memória para saída
    regs_dicionario = {}
    for i in range(32):
        if regs[i] != 0:
            regs_dicionario[f"${i}"] = regs[i]
    if hi != 0: regs_dicionario["hi"] = hi
    if lo != 0: regs_dicionario["lo"] = lo
    regs_dicionario["pc"] = pc
    
    # Dicionário de memória com endereços decimais ordenados
    mem_dicionario = {str(k): v for k, v in sorted(memoria_global.items()) if v != 0}

    resultado = {
        "hex": hex_str,
        "text": assembly,
        "regs": regs_dicionario,
        "mem": mem_dicionario,
        "stdout": stdout_text
    }

    resultados.append(resultado)
    print(f"{hex_str} -> {assembly}")

# Saída - Salva os resultados em um arquivo JSON
with open("saida.json", "w") as arquivo:
    json.dump(resultados, arquivo, indent=4)