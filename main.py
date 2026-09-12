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

    #TIPO J
    elif opcode in (2, 3):
        target = int(binario[6:32], 2)  

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