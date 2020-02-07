
def saveJumpLabel(asm, labelIndex, labelName):
    lineCount = 0
    for line in asm:
        line = line.replace(" ", "")
        if (line.count(":")):
            labelName.append(line[0:line.index(":")])  # append the label name
            labelIndex.append(lineCount)  # append the label's index
            asm[lineCount] = line[line.index(":") + 1:]
        lineCount += 1
    for item in range(asm.count('\n')):  # Remove all empty lines '\n'
        asm.remove('\n')


def digits(i, bits):
    s = bin(i & int("1" * bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(s)
def hex_converter():
    f = open("machine-hex-code.txt", "w+")
    h = open("machine-code.txt", "r")
    asm = h.readlines()
    for item in range(asm.count('\n')):  # Remove all empty lines '\n'
        asm.remove('\n')
    for line in asm:
        line = line.replace("\n", "")  # Removes extra chars
        line = line.replace("$", "")
        line = line.replace(" ", "")
        line = line.replace("zero", "0")  # assembly can also use both $zero and $0
        hexIndex = line.find("0x")
        hexin = hex(int(line,2))
        f.write(str(hexin) + str('\n'))
def converter():
    instructionAsm = []
    labelIndex = []
    labelName = []
    f = open("machine-code.txt", "w+")
    h = open("mips-file.txt", "r")
    asm = h.readlines()
    line_count = 0
    for item in range(asm.count('\n')): # Remove all empty lines '\n'
        asm.remove('\n')

    saveJumpLabel(asm,labelIndex,labelName) # Save all jump's destinations
    
    for line in asm:
        line = line.replace("\n","") # Removes extra chars
        instructionAsm.append(line)
        line = line.replace("$","")
        line = line.replace(" ","")
        line = line.replace("(",",") # For lb and sb lw sw
        line = line.replace(")","") # For lb sb and lw sw
        line = line.replace("zero","0") # assembly can also use both $zero and $0
        line = line.split('#',1)[0]

        if(line[0:5] == "multu"): # MULTU
            line = line.replace("multu","")
            line = line.split(",")
            rs = format(int(line[0]),'05b')
            rt = format(int(line[1]),'05b')
            final = str('000000') + str(rs) + str(rt) + str('0000000000011001')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:4] == "addi"): # ADDI
            line = line.replace("addi","")
            line = line.split(",")
            if line[2].isdigit():
                imm = format(int(line[2]),'016b')
            else:
                imm = int(line[2],16) if (int(line[2],16) >= 0) else (65536 + int((line[2]),16))
                imm = format(int(imm),'016b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[0]),'05b')
            final = str('001000') + str(rs) + str(rt) + str(imm)
            f.write(final + '\n')
            line_count += 1

        elif(line[0:4] == "mflo"): # MFLO
            line = line.replace("mflo","")
            line = line.split(",")
            rd = format(int(line[0]), '05b')
            final = str('0000000000000000') + str(rd) + str('00000010010')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:2] == "lb"): # LB
            line = line.replace("lb","")
            line = line.split(",")
            rt = format(int(line[0]), '05b')
            if line[1].isdigit():
                imm = format(int(line[1]), '016b')
            else:
                imm = int(line[1],16) if (int(line[1],16) >= 0) else (65536 + int((line[1]),16))
                imm = format(int(imm),'016b')
            rs = format(int(line[2]), '05b')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:4] == "mfhi"): # MFHI
            line = line.replace("mfhi","")
            line = line.split(",")
            rd = format(int(line[0]), '05b')
            final = str('0000000000000000') + str(rd) + str('00000010000')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:3] == "srl"): # SRL
            line = line.replace("srl","") 
            line = line.split(",")
            if (line[0] == ''):
                rd = format(int(line[1]), '05b')
                rt = format(int(line[2]), '05b')
                h = format(int(line[3]), '05b')
            else:
                rd = format(int(line[0]), '05b')
                rt = format(int(line[1]), '05b')
                h = format(int(line[2]), '05b') 
            final = str('000000') + str('00000') + str(rt) + str(rd) + str(h) + str('000010')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:3] == "sll"): # SLL
            line = line.replace("sll","") 
            line = line.split(",")
            rd = format(int(line[0]), '05b')
            rt = format(int(line[1]), '05b')
            h = format(int(line[2]), '05b') 
            final = str('000000') + str('00000') + str(rt) + str(rd) + str(h) + str('000000')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:2] == "lw"): # LW
            line = line.replace("lw","")
            line = line.split(",")
            rt = format(int(line[0]), '05b')
            if line[1].isdigit():
                imm = format(int(line[1]), '016b')
            else:
                imm = int(line[1],16) if (int(line[1],16) >= 0) else (65536 + int((line[1]),16))
                imm = format(int(imm),'016b')
            rs = format(int(line[2]), '05b')
            final = str('100011') + str(rs) + str(rt) + str(imm)
            f.write(final + '\n')
            line_count += 1

        elif(line[0:2] == "lb"): # LB
            line = line.replace("lb","")
            line = line.split(",")
            rt = format(int(line[0]), '05b')
            if line[1].isdigit():
                imm = format(int(line[1]), '016b')
            else:
                imm = int(line[1],16) if (int(line[1],16) >= 0) else (65536 + int((line[1]),16))
                imm = format(int(imm),'016b')
            rs = format(int(line[2]), '05b')
            final = str('100000') + str(rs) + str(rt) + str(imm)
            f.write(final + '\n')
            line_count += 1

        elif(line[0:3] == "lui"): # LUI
            line = line.replace("lui","")
            line = line.split(",")
            rt = format(int(line[0]), '05b')
            if line[1].isdigit():
                imm = format(int(line[1]), '016b')
            else:
                imm = int(line[1],16) if (int(line[1],16) >= 0) else (65536 + int((line[1]),16))
                imm = format(int(imm),'016b')
            final = str('00111100000') + str(rt) + str(imm)
            f.write(final + '\n')
            line_count += 1

        elif(line[0:2] == "sw"): # SW
            line = line.replace("sw","")
            line = line.split(",")
            rt = format(int(line[0]), '05b')
            if line[1].isdigit():
                imm = format(int(line[1]), '016b')
            else:
                imm = int(line[1],16) if (int(line[1],16) >= 0) else (65536 + int((line[1]),16))
                imm = format(int(imm),'016b')
            rs = format(int(line[2]), '05b')
            final = str('101011') + str(rs) + str(rt) + str(imm)
            f.write(final + '\n') 
            line_count += 1  

        elif(line[0:2] == "sb"): # SB
            line = line.replace("sb","")
            line = line.split(",")
            rt = format(int(line[0]), '05b')
            if line[1].isdigit():
                imm = format(int(line[1]), '016b')
            else:
                imm = int(line[1],16) if (int(line[1],16) >= 0) else (65536 + int((line[1]),16))
                imm = format(int(imm),'016b')
            rs = format(int(line[2]), '05b')
            final = str('101000') + str(rs) + str(rt) + str(imm)
            f.write(final + '\n') 
            line_count += 1     

        elif(line[0:3] == "beq"): # BEQ
            line = line.replace("beq","")
            line = line.split(",")
            rs = format(int(line[0]),'05b')
            rt = format(int(line[1]),'05b')
            if (line[2].isdigit()):
                immBinary = format(int(line[2]), '016b')
            else:
                for i in range(len(labelName)):
                    if (labelName[i] == line[2]):

                        x = labelIndex[i] - line_count - i - 1
                        if (x < 0):
                            x = x+65536
                            x = bin(x)
                            x = x[2:]
                            immBinary = x
                        else:
                            immBinary = format(x, '016b')

            final = str('000100') + str(rs) + str(rt) + str(immBinary)
            f.write(final + '\n')
            line_count += 1

        elif(line[0:3] == "bne"): # BNE
            line = line.replace("bne","")
            line = line.split(",")
            # for i in range(len(labelName)):
            #     if (labelName[i] == line[2]):
            #         x = int(labelIndex[i]) - len(labelIndex) 
            #         immLocate = format(x, '016b')
            # lineCountBinary = format(line_count, '016b')
            # imm = int(immLocate, 2) - int(lineCountBinary, 2) - 2
            rs = format(int(line[0]),'05b')
            rt = format(int(line[1]),'05b')
            # if (imm < 0):
            #     imm = imm -1
            #     immBinary = bin(imm^0b1111111111111111) [3:]

            # else:
            #     immBinary = format(imm, '016b')
            if (line[2].isdigit()):
                immBinary = format(int(line[2]), '016b')
            # else:
            #     for i in range(len(labelName)):
            #         if (labelName[i] == line[2]):
            #             x = labelIndex[i] - line_count - len(labelName)
            #             if (x < 0):
            #                 x = bin(x^0b1111111111111111)
            #                 x = x[3:]
            #                 immBinary = x
            #             else:
            #                 immBinary = '{:016b}'.format(x)
            else:
                for i in range(len(labelName)):
                    if (labelName[i] == line[2]):

                        x = labelIndex[i] - line_count - i - 1
                        if (x < 0):
                            x = x+65536
                            x = bin(x)
                            x = x[2:]
                            immBinary = x
                        else:
                            immBinary = format(x, '016b')

            final = str('000101') + str(rs) + str(rt) + str(immBinary)
            f.write(final + '\n')
            line_count += 1

        elif(line[0:4] == "sltu"): # SLTU
            line = line.replace("sltu","")
            line = line.split(",")
            rd = format(int(line[0]),'05b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[2]),'05b')
            final = str('000000') + str(rs) + str(rt) + str(rd) + str('00000101011')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:3] == "slt"): # SLT
            line = line.replace("slt","")
            line = line.split(",")
            rd = format(int(line[0]),'05b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[2]),'05b')
            final = str('000000') + str(rs) + str(rt) + str(rd) + str('00000101010')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:3] == "ori"): # ORI
            line = line.replace("ori","")
            line = line.split(",")
            if line[2].isdigit():
                imm = format(int(line[2]),'016b')
            else:
                imm = int(line[2],16) if (int(line[2],16) >= 0) else (65536 + int((line[2]),16))
                imm = format(int(imm),'016b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[0]),'05b')
            final = str('001101') + str(rs) + str(rt) + str(imm)
            f.write(final + '\n')
            line_count += 1

        
        elif(line[0:3] == "xor"): # XOR
            line = line.replace("xor","")
            line = line.split(",")
            rd = format(int(line[0]),'05b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[2]),'05b')
            final = str('000000') + str(rs) + str(rt) + str(rd) + str('00000100110')
            #f.write(hex(int(final,2)) + '\n')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:4] == "andi"): # ANDI
            line = line.replace("andi","")
            line = line.split(",")
            if line[2].isdigit():
                imm = format(int(line[2]),'016b')
            else:
                imm = int(line[2],16) if (int(line[2],16) >= 0) else (65536 + int((line[2]),16))
                imm = format(int(imm),'016b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[0]),'05b')
            final = str('001100') + str(rs) + str(rt) + str(imm)
            f.write(final + '\n')
            line_count += 1
            
        elif(line[0:4] == "addu"): # ADDU
            line = line.replace("addu","")
            line = line.split(",")
            rd = format(int(line[0]),'05b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[2]),'05b')
            final = str('000000') + str(rs) + str(rt) + str(rd) + str('00000100001')
            #f.write(hex(int(final,2)) + '\n')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:3] == "add"): # ADD
            line = line.replace("add","")
            line = line.split(",")
            rd = format(int(line[0]),'05b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[2]),'05b')
            final = str('000000') + str(rs) + str(rt) + str(rd) + str('00000100000')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:3] == "sub"): # SUB
            line = line.replace("sub","")
            line = line.split(",")
            rd = format(int(line[0]),'05b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[2]),'05b')
            final = str('000000') + str(rs) + str(rt) + str(rd) + str('00000100010')
            f.write(final + '\n')
            line_count += 1
        
        elif(line[0:2] == "sb"): # SB
            line = line.replace("sb","")
            line = line.split(",")
            rt = format(int(line[0]), '05b')
            if line[1].isdigit():
                imm = format(int(line[1]), '016b')
            else:
                imm = int(line[1],16) if (int(line[1],16) >= 0) else (65536 + int((line[1]),16))
                imm = format(int(imm),'016b')
            rs = format(int(line[2]), '05b')
            final = str('101000') + str(rs) + str(rt) + str(imm)
            f.write(final + '\n')
            line_count += 1

        elif(line[0:4] == "mfld"): # mfld
            line = line.replace("mfld","")
            line = line.split(",")
            rd = format(int(line[0]),'05b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[2]),'05b')
            final = str('000000') + str(rs) + str(rt) + str(rd) + str('00000111100')
            f.write(final + '\n')
            line_count += 1

        elif(line[0:3] == "and"): # AND
            line = line.replace("and","")
            line = line.split(",")
            rd = format(int(line[0]),'05b')
            rs = format(int(line[1]),'05b')
            rt = format(int(line[2]),'05b')
            final = str('000000') + str(rs) + str(rt) + str(rd) + str('00000100100')
            f.write(final + '\n')
            line_count += 1

        else:
            print("instruction Not found")
            print(line)
    f.write(str('00010000000000001111111111111111'))
    f.close()
    return instructionAsm