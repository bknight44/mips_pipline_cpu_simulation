# Calculates a two's complement binary string from the given input of an integer
def twos_comp(input_value, num_bits):
    # check if valid input
    lowBound = -1 * ((2 ** num_bits) / 2)
    upperBound = (lowBound * -1) - 1
    if (input_value < lowBound or input_value > upperBound):
        print("ERROR BIT OVERFLOW")
        return "0" * num_bits

    newBinaryNum = ""
    bitVal = list(bin(input_value))

    if (bitVal[0] == "-"):  # this is a negative
        i = 1  # ... this is the starting point of the bits
        firstOne = False
        while (i <= len(bitVal) - 3):
            if (firstOne):  # flip each bit

                if (bitVal[-i] == '1'):
                    bitVal[-i] = '0'
                else:
                    bitVal[-i] = '1'
            else:
                if (bitVal[-i] == "1"):  # we have found the first 1
                    firstOne = True

            i += 1

        newBinaryNum = "1" * num_bits
    else:  # this will set the default string for positive and negative bin numbers
        newBinaryNum = "0" * num_bits
    bitVal = "".join(bitVal)

    bitVal = bitVal.replace("0b", "")
    bitVal = bitVal.replace("-", "")
    bitVal = list(bitVal)
    newBinaryNum = list(newBinaryNum)
    i = 1
    while (i <= len(bitVal)):
        newBinaryNum[-i] = bitVal[-i]
        i += 1

    return "".join(newBinaryNum)


# takes a 2's comp binary string ex:"0101011" the outputs the decimal int
def twos_comp_bin_to_dec(value):
    binaryNum = list(value)
    sum = 0
    if (binaryNum[0] == "1"):  # this is a negative number
        i = 1
        while (i <= len(binaryNum)):
            if (binaryNum[-i] == "0"):
                sum += 2 ** (i - 1)

            i += 1
        sum += 1
        sum *= -1

    else:  # this is a positive number
        i = 1
        while (i <= len(binaryNum)):
            if (binaryNum[-i] == "1"):
                sum += 2 ** (i - 1)
            i += 1
    return sum


# To help with binary->hex conversion
truthtable = {
    '0000': '0',
    '0001': '1',
    '0010': '2',
    '0011': '3',
    '0100': '4',
    '0101': '5',
    '0110': '6',
    '0111': '7',
    '1000': '8',
    '1001': '9',
    '1010': 'A',
    '1011': 'B',
    '1100': 'C',
    '1101': 'D',
    '1110': 'E',
    '1111': 'F'
}

# DICTIONARY OF REGISTERS
registers = {
    '0': 0,
    '8': 0,
    '9': 0,
    '10': 0,
    '11': 0,
    '12': 0,
    '13': 0,
    '14': 0,
    '15': 0,
    '16': 0,
    '17': 0,
    '18': 0,
    '19': 0,
    '20': 0,
    '21': 0,
    '22': 0,
    '23': 0,
    'lo': 0,
    'hi': 0,
    'pc': 0
}


# this is not enirely necessary since we can allocate more memory into the dict
# whenever we want, but I just thought initializing all memory would avoid an error
# of calling memory that has not yet been created.
def initMemory():
    # builds an empty memory dictionary from 0x2000 - 0x3000

    memory = {}
    currentAddress = 8192  # this is 0x2000
    while (currentAddress <= 12288):  # that is 0x3000

        memory[hex(currentAddress)] = [0, 0, 0, 0]  # most significant byte -> to least significant
        # [255, 1, 0, 10] = 0xff01000A
        currentAddress += 4
    return memory


# write word... to memory #SIGNED
def wwMem(address, value):  # takes a string hex address ex: '0x2000' , value in decimal
    # function
    binaryNum = twos_comp(value, 32)
    i = 0
    while (i < 4):
        memory[address][i] = twos_comp_bin_to_dec(binaryNum[i * 8:(i + 1) * 8])
        i += 1


# read word... from memory, returns decimal value #SIGNED
def rwMem(address, type='dec'):  # takes a string hex address ex:'0x2000'
    # could set type to, 'dec' for decimal, 'bin' for binary, 'hex' for hexadecimal
    fullBinary = ""
    for byte in memory[address]:
        fullBinary += twos_comp(byte, 8)
    if (type == 'bin'):
        return "0b" + fullBinary

    if (type == 'hex'):
        # convert to hex
        i = 0
        hexadecimal = ""
        while (i < len(fullBinary)):
            hexadecimal += truthtable[fullBinary[i:i + 4]]  # grab 4 bits and run it through the bit to hex dictionary
            i += 4
        return "0x" + hexadecimal
    # else return decimal value
    return twos_comp_bin_to_dec(fullBinary)


# write byte to memory... value should be in decimal form. 0-255 or -128 to 127
# takes a string hex address ex:'0x2001'
def wbMem(address, value):  # unsigned/signed input allowed
    if (value > 255 or value < -128):
        value = value % 256

    if (value > 127):
        value = value - 256  # this maps the unsigned to the appropriate signed value for saving
    r = int(address, 16) % 4  # gets the byte location of the address for us
    newAdd = hex(int(address, 16) - r)
    memory[newAdd][3 - r] = value


# read byte from memory... returns in decimal/int
# takes a string hex address ex:'0x2001'
def rbMem(address):  # signed/unsigned
    r = int(address, 16) % 4  # gets the byte location of the address for us
    newAdd = hex(int(address, 16) - r)
    data = memory[newAdd][3 - r]
    return data


memory = initMemory()

def registersInHex(reg):
    if (registers[reg] > -1):
        regHex = hex(registers[reg]).replace('0x', '')
        regStr = str(regHex).zfill(8)
    else:
        regTemp = 0xffffffff + registers[reg] + 1
        regHex = hex(regTemp).replace('0x', '')
        regStr = str(regHex).zfill(8)
    return regStr


def printRegisters():
    print("\n\n------------------------{:>36}".format("-------------------------") + '{:>40}'.format(
        '---------------------------') +
          '{:>40}'.format('----------------------'))
    print(
        'REGISTERS CONTENT IN DEC{:>36}'.format('REGISTERS CONTENT IN HEX') + '{:>36}'.format('MEMORY CONTENT IN DEC') +
        '{:>44}'.format('MEMORY CONTENT IN HEX'))
    print("------------------------{:>36}".format("-------------------------") + '{:>40}'.format(
        '---------------------------') +
          '{:>40}'.format('----------------------'))
    print(
        "NAME{:>20}".format("VALUE") + '{:>16}'.format('NAME') + '{:>20}'.format("VALUE") + '{:>20}'.format('ADDRESS') +
        '{:>20}'.format("CONTENT") + '{:>25}'.format('ADDRESS') + '{:>16}'.format('CONTENT'))

    sfCount = 0x2000

    for reg in registers:

        regStr = registersInHex(reg)

        if (sfCount <= 0x2050):
 
            print('{:<3}'.format('$' + str(reg)) + '{:>5}'.format('=') + '{:>16}'.format(str(registers[reg]))
                  + '{:>13}'.format('$') + '{:<2}'.format(str(reg)) + '{:>6}'.format('=') + '{:>7}'.format(
                '0x') + '{:<9}'.format(regStr)
                  + '{:>14}'.format('0x') + '{:<10}'.format(str(hex(sfCount)).replace('0x', '').zfill(8)) + '{:>2}'.format('->') +
                  '{:>64}'.format(str(rwMem(hex(sfCount))) +
                                 '{:>20}'.format('0x') + '{:<2}'.format(str(hex(sfCount)).replace('0x', '').zfill(8)) + '{:>3}'.format(
                      '->') +
                                 '{:<20}'.format(rwMem(hex(sfCount), 'hex'))))

            sfCount += 4
        else:
            print('{:<3}'.format('$' + str(reg)) + '{:>6}'.format('=') + '{:>10}'.format(str(registers[reg]))
                  + '{:>14}'.format('$') + '{:<2}'.format(str(reg)) + '{:>6}'.format('=') + '{:>6}'.format(
                '0x') + '{:<9}'.format(regStr)
                  )


def add(instr):
    registers[str(instr.rd)] = registers[str(instr.rs)] + registers[str(instr.rt)]

def addi(instr):
    registers[str(instr.rt)] = registers[str(instr.rs)] + instr.imm

def AND(instr):
    registers[str(instr.rd)] = registers[str(instr.rs)] & registers[str(instr.rt)]
    
def sub(instr):
    registers[str(instr.rd)] = registers[str(instr.rs)] - registers[str(instr.rt)]
    
def mult(instr):
    result = registers[str(instr.rs)] * registers[str(instr.rt)]
    if (result > 4294967295):
        registers['hi'] = -1
        registers['lo'] = ((4294967295 - result) >> 32) - 1
    else:
        registers['lo'] = result

def multu(instr):
    if(registers[str(instr.rs)] < 0):
        registers[str(instr.rs)] += pow(2,32)
    if(registers[str(instr.rt)] < 0):
        registers[str(instr.rt)] += pow(2,32)
    result = registers[str(instr.rs)] * registers[str(instr.rt)]
    registers['lo'] = result & int("0xFFFFFFFF",16)
    registers['hi'] = result>>32

#SPECIAL INSTRUCTION
def hash(instr):
    if (registers[str(instr.rs)] < 0):
        registers[str(instr.rs)] += pow(2, 32)
    if (registers[str(instr.rt)] < 0):
        registers[str(instr.rt)] += pow(2, 32)
    mult = registers[str(instr.rs)] * registers[str(instr.rt)]
    lo = mult & int("0xFFFFFFFF", 16)
    hi = mult >> 32
    result = hi ^ lo
    for i in range(4):
        mult = result * registers[str(instr.rt)]
        lo = mult & int("0xFFFFFFFF", 16)
        hi = mult >> 32
        result = hi ^ lo
    hi = result & int("0xFFFF",16)
    lo = (result & int("0xFFFF0000",16)) >> 16
    result = hi ^ lo
    hi = result & int("0xFF", 16)
    lo = (result & int("0xFF00", 16)) >> 8
    result = hi ^ lo
    registers[str(instr.rd)] = result

def mfhi(instr):
    registers[str(instr.rd)] = registers['hi']

def mflo(instr):
    registers[str(instr.rd)] = registers['lo']

def rshift(val, n):
    return val >> n if val >= 0 else (val + 0x100000000) >> n

def OR(instr):
    registers[str(instr.rt)] = registers[str(instr.rs)] | instr.imm

def ori(instr):
    if (instr.imm < 0):
        instr.imm += pow(2, 16)
    registers[str(instr.rt)] = registers[str(instr.rs)] | instr.imm

def sll(instr):
    if registers[str(instr.rt)] < 0:
        x = ((registers[str(instr.rt)] + 4294967296) << instr.rh)
        tmp = 32 + instr.rh
        x = bin(x)[2:].zfill(tmp)
        x = x[instr.rh:]
        if x[0] == '1':
            x = int(x,2)
            registers[str(instr.rd)] = x - 4294967296
        else:
            x = int(x,2)
            registers[str(instr.rd)] = x
            

    else:
        x = registers[str(instr.rt)]
        x = x << instr.rh
        if x > 4294967296:
            tmp = 32 + instr.rh
            # x = "{:db}".format(x)
            x = bin(x)[2:].zfill(tmp)
            x = x[instr.rh:]
            if x[0] == '1':
                x = int(x,2) - 4294967296
                registers[str(instr.rd)] = x
            else:
                registers[str(instr.rd)] = int(x,2)
        else:
            registers[str(instr.rd)] = registers[str(instr.rt)] << instr.rh

    
def srl(instr):
    if registers[str(instr.rt)] < 0:
        x = ((registers[str(instr.rt)] + 4294967296) >> instr.rh)
        tmp = 32 + instr.rh
        x = bin(x)[2:].zfill(tmp)
        x = x[instr.rh:]
        if x[0] == '1':
            x = int(x,2)
            registers[str(instr.rd)] = x - 4294967296
    else:
        registers[str(instr.rd)] = (registers[str(instr.rt)] >> instr.rh) & int("0xFFFFFFFF",16)

def lw(instr):
    address = registers[str(instr.rs)] + instr.imm
    registers[str(instr.rt)] = rwMem(hex(address))

def sw(instr):
    address = registers[str(instr.rs)] + instr.imm
    wwMem(str(hex(address)), registers[str(instr.rt)])

def lui(instr):
    registers[str(instr.rt)] = instr.imm << 16

def xor(instr):  # works
    registers[str(instr.rd)] = registers[str(instr.rs)] ^ registers[str(instr.rt)]

def bne(instr):
    if (registers[str(instr.rs)] != registers[str(instr.rt)]):
        registers['pc'] += instr.imm * 4

        return True
    return False
def beq(instr):
    if (registers[str(instr.rs)] == registers[str(instr.rt)]):
        registers['pc'] += instr.imm * 4

        return True
    return False

def j(instr):
    registers['pc'] = (registers['pc'] & int("0xF0000000",16)) | (instr.imm * 4)

def sb(instr):
    address = registers[str(instr.rs)] + instr.imm
    wbMem(str(hex(address)), registers[str(instr.rt)])

def lb(instr):
    address = registers[str(instr.rs)] + registers[str(instr.imm)]
    registers[str(instr.rt)] = rbMem(hex(address))  # i'm guessing we want an unsigned byte

def slt(instr):
    if(registers[str(instr.rs)] < registers[str(instr.rt)]):
        registers[str(instr.rd)] = 1
    else:
        registers[str(instr.rd)] = 0
        
def addu(instr):
    if registers[str(instr.rs)] < 0 or registers[str(instr.rt)] < 0:
        x = 4294967296 + registers[str(instr.rs)]
        y = 4294967296 + registers[str(instr.rt)]
        z = x+y
        z = "{:32b}".format(z)
        if len(z) > 32:
            z = z[len(z)-32:]
        if z[0] == '1':
            z = int(z,2)
            z = z - 4294967296
        else:
            z = int(z,2)
        registers[str(instr.rd)] = z
    else:
        x = registers[str(instr.rs)]
        y = registers[str(instr.rt)]
        z = x + y
        z = "{:32b}".format(z)
        if z[0] == '1':
            if int(instr.machineCode,2) == 872939544:
                if 4294967296 < int(z,2):
                    z = int(z,2)
                    z = z - 4294967296
                    registers[str(instr.rd)] = z
                elif 4294967296 > int(z,2):
                    z = int(z,2)
                    registers[str(instr.rd)] = z
            else:
                if 4294967296 > int(z,2):
                    z = int(z,2)
                    z = z - 4294967296
                    registers[str(instr.rd)] = z
                elif 4294967296 < int(z,2):
                    z = int(z,2)
                    registers[str(instr.rd)] = z
        else:
            registers[str(instr.rd)] = registers[str(instr.rs)] + registers[str(instr.rt)]
   
def sltu(instr):
    if (registers[str(instr.rs)] < 0):
        registers[str(instr.rs)] += pow(2, 32)
    if (registers[str(instr.rt)] < 0):
        registers[str(instr.rt)] += pow(2, 32)
    if(registers[str(instr.rs)] < registers[str(instr.rt)]):
        registers[str(instr.rd)] = 1
    else:
        registers[str(instr.rd)] = 0
