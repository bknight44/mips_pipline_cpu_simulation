

#from asmToMachinecode import *
from pipeConverter import *
from instructionExec import *


dynamicInstructionCount = 0 
ALUOutMCount = 0 
ResultWCount = 0 
SrcAECount = 0 
SrcBECount = 0 
WriteDataECount = 0 
EqualDCount = 0
ForwardADCount = 0 
ForwardBDCount = 0
FlushStallCount = 0 
DataStallCount = 0

#the 4th parameter in the dictionary will be a number 0-2
#0 represents no regWrite. 1 -> rd, 2 -> rt
#the 3rd parameter is the list of dependecies that the instruction needs
#instructions needed still:  addu, slt, sub
func_dictionary = {
    '000000011000': (mult, 'mult',['s', 't'], 0),
    '000000011001': (multu, 'multu', ['s', 't'], 0),
    '000000010000': (mfhi, 'mfhi', [], 1),
    '000000010010': (mflo, 'mflo', [], 1),
    '000000100101': (OR, 'or', ['s','t'], 1),
    '001101': (ori, 'ori', ['s'], 2),
    '000000000010': (srl, 'srl', ['t'], 1),
    '100011': (lw, 'lw', ['s'], 2),
    '101011': (sw, 'sw', ['s', 't'], 0),
    '000000100000': (add, 'add', ['s', 't'], 1),
    '000000100001': (addu, 'addu',  ['s', 't'], 1),
    '001000': (addi, 'addi', ['s'], 2),
    '001111': (lui, 'lui', ['t'], 0),
    '000000100110': (xor, 'xor', ['s', 't'], 1),
    '000101': (bne, 'bne', ['s', 't'], 0),
    '000100': (beq, 'beq', ['s', 't'], 0),
    '101000': (sb, 'sb', ['s', 't'], 0),
    '100000': (lb, 'lb', ['s'], 2),
    '000000000000': (sll, 'sll', ['t'], 1),
    '000000101011': (sltu, 'sltu', ['s', 't'], 1),
    '000000101010': (slt, 'slt', ['s', 't'], 1),
    '000000100010': (sub, 'sub', ['s', 't'], 1),
    '000000100100': (AND, 'and', ['s', 't'], 1),
    '000010': (j, 'j', [], 0),
    '000000111111': (hash, 'hash', ['s', 't'], 1)
}


class Bubble: 
    #this class is to contain all information needed for a bubble
    #in the pipeline

    def __init__(self, inst1Name, inst2Name, bubbleT):
        self.isBubble = True #will be checked by the function running the pipelineQueue
        self.bubbleType = bubbleT #0 -> stall, 1 -> flush
        #now we need to save why this bubble happened
        self.hazardInst1 = inst1Name #this will be the instruction name that had the hazard
        self.regConflicts = [] #if there were register conflicts
        
        self.hazardInst2 = inst2Name #another string name of instruction
        self.regStoreConflict = None #will contain the int of register being stored
        
        self.branchTaken = None #a string of the instruction that is the branch
    def printDiagonostics(self):
        #this function helps the main diagnositics function out
        #it will print everything about this bubble
        if(self.bubbleType == 0):
            print("The bubble is because of a stall.")
            print("This was caused by the hazard " + self.hazardInst1 + " and " + self.hazardInst2)
            print("registers: ", end='')
            for r in self.regConflicts:
                print("$" + str(r) + " ", end='')
            print(" in " + self.hazardInst1 + " needed data from $" + str(self.regStoreConflict) + " in " + self.hazardInst2)
            
        else:
            print("The bubble is because of a flush.")
            print("Caused by taking the branch: " + self.branchTaken)

class pipeline:
    #this will store a data type of each stage in the pipeline cpu
    #for each instruction. This class can then be acccessed by the main program
    #as the instruction goes through the cpu stages
    
    def __init__(self, F, D, E, M, W, machineCode, asmInstruction):
        self.allStages = [F, D, E, M, W] #will make accesing them easier
        
        self.isBubble = False #will be checked by the function running the pipelineQueue
        self.machineCode = machineCode
        self.fullInstruction = asmInstruction #this is a string of the asm instruction... only used for printing
        self.instructionName = ""
        self.instructionBin = ""
        #define each register. not every instruction will use this
        self.rs = None
        self.rt = None
        self.rd = None
        self.imm = None
        self.rh = None
        
        #this is the registers that (this) particular instruction updates
        #it will be searched by other instructions entering the pipline to
        #check for hazards
        self.updates = None
        
        #this is a list of what this instruction needs... we will use this
        #when checking for hazards
        self.needs = None
        self.readInMachineCode()
        
    def printHazards(self, stage): #input the number for the stage the instruction is at 0 - 4
        #will print information about the hazards that are being solved
        #note, this should only be NO STALL hazards... as the bubble class should
        self.allStages[stage].output()

    def readInMachineCode(self):
        if(self.machineCode[:6] == "000000"): #trying to get first 6 digits
            hash = self.machineCode[:6] + self.machineCode[-6:] #add first 6 and last 6
        else:
            hash = self.machineCode[:6] #if it does not have a longer code
        self.instructionBin = hash
        self.instructionName = func_dictionary[hash][1]
        #collect possible data registers
        self.rs = int(self.machineCode[6:11], 2)
        self.rt = int(self.machineCode[11:16], 2)
        self.rd = int(self.machineCode[16:21], 2)
        if self.machineCode[16] == '1':  # check the immediate for negative numbers and convert if needed
            self.imm = -((int(self.machineCode[16:32], 2) ^ 0xFFFF) + 1)
        else:
            self.imm = int(self.machineCode[16:], 2)
        self.rh = int(self.machineCode[21:26], 2)
            
    def __hazardsOneAway(self, rs, rt, other): #other is the object of the instruction with the colision
        global ALUOutMCount
        global ResultWCount
        global DataStallCount
        #lw and a compute need a hazard on resultW.. no stall
        #lw and branch create a stall of 2
        #compute and compute use ALUOutM ... no stall
        #compute and branch use ALUOutM... stall 1
        inst1 = self.instructionName
        inst2 = other.instructionName
        if(inst2 == "lw" or inst2 == "lb"):
            if(inst1[0] == 'b'): #some branch
                self.allStages[1].addHazard(rs, rt, 2) #send a stall of 2
                self.allStages[1].addBubble(rs, rt, self, other)
                DataStallCount += 2
                
            elif(inst1 == "sw" or inst1 == "sb"):
                self.allStages[2].addHazard(rs, rt, 1, True) #let the class know that it is a store word
                self.allStages[2].addBubble(rs, rt, self, other)
                DataStallCount += 1
            else:
                self.allStages[2].addHazard(rs, rt, 1, False) #let the class know that it is a store word
                self.allStages[2].addBubble(rs, rt, self, other)
                DataStallCount += 1
            other.allStages[4].ResultW = 1 #set the fowarding path for the other instruction
            ResultWCount += 1
        else:
            if(inst1[0] == 'b'): #some branch
                self.allStages[1].addHazard(rs, rt, 1) #send a stall of 1
                self.allStages[1].addBubble(rs, rt, self, other)
                DataStallCount += 1
            elif(inst1 == "sw" or inst1 == "sb"):
                self.allStages[2].addHazard(rs, rt, 0, True) #let the class know that it is a store word


            else:
                #it's another compute comand
                self.allStages[2].addHazard(rs, rt, 0, False)

            #for each case    
            other.allStages[3].ALUOutM = 1 #set the fowarding path for the other instruction
            ALUOutMCount += 1
    
    def __hazardsTwoAway(self, rs, rt, other): #other is the object of the instruction with the colision
        global ALUOutMCount
        global ResultWCount
        global DataStallCount
        #lw and branch create a stall of 1
        #lw and a compute need a hazard on resultW.. no stall
        #compute and compute use resultW ... no stall
        #compute and branch will pass back on ALUOutM. no stall
        inst1 = self.instructionName
        inst2 = other.instructionName
        if(inst2 == "lw" or inst2 == "lb"):
            if(inst1[0] == 'b'): #some branch
                self.allStages[1].addHazard(rs, rt, 1) #send a stall of 2
                self.allStages[1].addBubble(rs, rt, self, other)
                DataStallCount += 1
            elif(inst1 == "sw" or inst1 == "sb"):
                self.allStages[2].addHazard(rs, rt, 0, True) #let the class know that it is a store word

            else:
                self.allStages[2].addHazard(rs, rt, 0, False) #let the class know that it is a store word
            other.allStages[4].ResultW = 1 #set the fowarding path for the other instruction
            ResultWCount += 1
        else:
            if(inst1[0] == 'b'): #some branch
                self.allStages[1].addHazard(rs, rt, 0) #send a stall of 1
                other.allStages[3].ALUOutM = 1 #set the fowarding path for the other instruction
                ALUOutMCount += 1
            
            elif(inst1 == "sw" or inst1 == "sb"):
                self.allStages[2].addHazard(rs, rt, 0, True) #let the class know that it is a store word
                other.allStages[4].ResultW = 1 #set the fowarding path for the other instruction
                ResultWCount += 1
            else:
                #it's another compute comand
                self.allStages[2].addHazard(rs, rt, 0, False)
                other.allStages[4].ResultW = 1 #set the fowarding path for the other instruction
                ResultWCount += 1
            
    
        
        
    def __hazardsThreeAway(self, rs, rt, other): #other is the object of the instruction with the colision
        global ResultWCount
        #lw will need to pass resultW to a branch. No stall though
        #compute and branch will pass back on resultW. no stall
        inst1 = self.instructionName
        inst2 = other.instructionName
        if(inst2 == "lw" or inst2 == "lb"):
            if(inst1[0] == 'b'): #some branch
                self.allStages[1].addHazard(rs, rt, 0)
                other.allStages[4].ResultW = 1 #set the fowarding path for the other instruction
                ResultWCount += 1
            else:
                print("We should never reach this point line 182")
                exit()
        else:
            if(inst1[0] == 'b'): #some branch
                self.allStages[1].addHazard(rs, rt, 0) 
                other.allStages[4].ResultW = 1 #set the fowarding path for the other instruction
                ResultWCount += 1
            else:
                print("We should never reach this point line 189")
                exit()

        
    
    def findHazards(self, stages):
        #queue is the "pipelineQueue" queue
        #loop through and check ahead for hazards
        stageCount = 0
        for stage in stages[0:3]: #only need to look ahead 3...only branch needs 3
            if(stage == None):
                stageCount += 1
                continue #there won't be hazards
                
            if(stage.isBubble):
                stageCount += 1
                continue #there is no instruction in this stage... just a bubble
                
            regWrite = func_dictionary[stage.instructionBin][3] #gets the regWritten to  
            
            #check if instruction is a branch only then do we check the 3rd stage
            if(self.instructionName[0] != 'b' and stageCount == 2):
                break #we are done if the instruction is not a branch
            
            if(regWrite == 0):
                stageCount += 1
                continue #there will be no hazard. next stage
            elif(regWrite == 1):
                regWrite = stage.rd #reset regWrite to rd... this is
                #now the value of the register... like $0-$25
            
            elif(regWrite == 2):
                regWrite = stage.rt #same as the one above^^^
  
            neededList = func_dictionary[self.instructionBin][2] #list of needed registers
            if(len(neededList) == 0): #again no need to go further
                stageCount += 1
                continue #no dependencies, skip stage
            
            for reg in neededList:
                hazardOnRs = False
                hazardOnRt = False
                if(reg == 's'):
                    regNum = self.rs
                    hazardOnRs = True
                elif(reg == 't'):
                    regNum = self.rt
                    hazardOnRt = True
                else:
                    continue
                if(regNum == regWrite):
                    #we found a data hazard
                    #Now label it with either ALUOutM or a ResultW
                    
                    if(stageCount == 0):
                        self.__hazardsOneAway(hazardOnRs, hazardOnRt, stage)
                        return #amazingly if we find a data hazard here, we are done
                        
                    elif(stageCount == 1):
                        self.__hazardsTwoAway(hazardOnRs, hazardOnRt, stage)
                        return #amazingly if we find a data hazard here, we are done
                    
                    elif(stageCount == 2):
                        self.__hazardsThreeAway(hazardOnRs, hazardOnRt, stage)
                        return #amazingly if we find a data hazard here, we are done
                        
                    else:
                        print("Error should never get here line 244")
                        exit()
            stageCount += 1

class pipelineQueue:
    #this is the structure of the actual pipeline flow
    #it will contain the "pipeline" data for 5 instructions
    def __init__(self):
        #initially all stages are empty
        
        self.stageNames = ["Fetch", "Decode", "Execute", "Memory", "Write"]
        self.stages = [None, None, None, None, None]
        self.dataDump = [] #after going through the pipeline put instruction in here
    
    def diagnositics(self):
        #print the contents of the pipeline
        print("Pipeline contents:")
        noBubbles = True
        i = 0 
        while(i < 5):
            if(self.stages[i] != None):
                if(self.stages[i].isBubble):
                    print(self.stageNames[i] + ": Bubble" )
                    noBubbles = False
                else:
                    print(self.stageNames[i] + ": " + self.stages[i].fullInstruction)
            else:
                print(self.stageNames[i] + ": Empty" )
            i += 1
        print("")#add a space
        
        if(noBubbles):
            print("Currently no bubbles in the pipeline")
        else:
            print("Current bubble information in the pipeline:")
            #print out bubble information
            i = 0 
            while(i < 5):
                if(self.stages[i].isBubble):
                    self.stages[i].printDiagonostics()
                i += 1
        
        i = 0 
        while(i < 5):
            print(self.stageNames[i] + " stage hazards:")
            if(self.stages[i] != None):
                if(self.stages[i].isBubble):
                    print("\tNone, stage has a bubble")
                else:
                    self.stages[i].printHazards(i)
            else: 
                print("\tNone, stage is empty")
            print("")
            i += 1
        
        
    def push(self, machineCode, asmInstruction):#returns true if item pushed
        global dynamicInstructionCount
        global FlushStallCount
        pushed = False
        firstBubble = False
        if(machineCode == None):#program is done... we just need to cycle till end of the pipeline
            runInstruction = self.stages[3]
            i = 3 
            while(i >= 0):
                self.stages[i+1] = self.stages[i]
                i -= 1 
            self.stages[0] = None
            pushed = True
        else:
            F = Fetch();D = Decode();E = Execute();M = Memory();W = Write()
            newInstruction = pipeline(F, D, E, M, W, machineCode, asmInstruction)
            newInstruction.findHazards(self.stages)#this needs to be run before adding to the queue
            
            #add new instruction, dump old one
            runInstruction = self.stages[3]
            activeStall = False
            firstStall = True
            i = 3 
            while(i >= 0):
                if(self.stages[i] == None and (not activeStall)): # we can't iterate over a none later
                    self.stages[i+1] = self.stages[i]
                    i -= 1 
                    continue
                if(self.stages[i].isBubble and (not activeStall) ): # we can't check a bubbles stall later
                    self.stages[i+1] = self.stages[i]
                    i -= 1 
                    continue
                if((self.stages[i].allStages[i].stall == 0) and (not activeStall)): #only move instruction ahead if the stall count is 0
                    self.stages[i+1] = self.stages[i]
                else:
                    if(firstStall):
                        #we need to add a buble in front of instruction
                        firstStall = False
                        activeStall = True
                        #insert bubble
                        firstBubble = True
                        self.stages[i+1] = self.stages[i].allStages[i].bubble
                        self.stages[i].allStages[i].stall -= 1
                    #if(self.stages[i].allStages[i].stall > 0): #from any active stage that has a stall set. reduce that
                    #    self.stages[i].allStages[i].stall -= 1
                    
                    
                i -= 1
            
            if(not activeStall):
                self.stages[0] = newInstruction
                pushed = True
            
        
        #FINAL STAGE INSTRUCTION EXECUTION        
        #execute the last instruction in the pipeline
        if(runInstruction != None):#we dont run a branch instruction at the end                 we check this because we might have already run the instruct
            if(not runInstruction.isBubble and runInstruction.instructionName[0] != 'b' and runInstruction.allStages[3].ALUOutM == 0): 
                #print("running last "  + runInstruction.instructionName +  " instruction")
                #normal instruction
                function = func_dictionary[runInstruction.instructionBin][0] #obtain instruction function
                function(runInstruction)#hand the function the last instruction in the pipeline
                dynamicInstructionCount += 1
            #if it was a bubble we dont need to run it
        
        
        #EARLY STAGE INSTRUCTION EXECUTION  
        #now we potentially need to run an instruction early if there is a hazard... really only affects branch
        if(self.stages[3] != None):
            if(not self.stages[3].isBubble):#obviously we will not run a bubble
                if(self.stages[3].allStages[3].ALUOutM == 1): #run this instruction at this stage in case there is a branch that needs it
                    if(self.stages[3].instructionName[0] != 'b'): #branches have already been run
                        #print("running: " + self.stages[3].instructionName + " early")
                        #normal instruction
                        function = func_dictionary[self.stages[3].instructionBin][0] #obtain instruction function
                        function(self.stages[3])#hand the function the last instruction in the pipeline
                        dynamicInstructionCount += 1
        
        
        #BRANCH STAGE INSTRUCTION EXECUTION  
        if(self.stages[1] != None):
            if(not self.stages[1].isBubble):#we would not check a bubble for a branch
                if(self.stages[1].instructionName[0] == 'b'): #there is a branch waiting to be run
                    if(self.stages[1].allStages[1].stall == 0):#only execute if we are not waiting for the stall to be over
                        #print("running: " + self.stages[1].instructionName + " early")
                        function = func_dictionary[self.stages[1].instructionBin][0] #obtain instruction function
                        branching = function(self.stages[1])#run branch function
                        dynamicInstructionCount += 1
                        if(branching):#flush fetch
                            newBubble = Bubble(self.stages[1].instructionName, self.stages[1].instructionName , 1)
                            newBubble.branchTaken = self.stages[1].fullInstruction
                            registers['pc'] -= 4
                            if(firstBubble):
                                registers['pc'] -= 4
   
                            self.stages[0] = newBubble #insert bubble into pipeline
                            FlushStallCount += 1
                            pushed = True #since a branch executed, the main loop can start from the next line
                    
                
        #pipeline has now been updated
        return pushed
            

#okay, so one stage might need to send its data back to 2 different stages
#so, the class will keep track of what it is sending back and what it is taking
#example: Write stage will just know that it is sending ALUOutM
#meanwhile execution stage receves it on SRCBE. and decode stage recieves it on EqualD
noHaz = "\tNo Hazards" #string used multiple times
class Fetch:
    #contain instructions for fetch cycle
    def __init__(self):
        self.flushed = 0 #will be set to 1 if this gets flushed. Can check later
        self.stall = 0 #tells the pipeline to wait x times 
        self.bubble = None
        #to explain a bubble in the pipeline
        
    def output(self):
        if(self.flushed == 1):
            print("\tstage is going to be flushed")
        else:
            print(noHaz)
            
class Decode:
    def __init__(self):
        self.ForwardAD = 0
        self.ForwardBD = 0
        self.EqualD = 0
        self.bubble = None
        self.stall = 0 #tells the pipeline to wait x times 
    
    def addBubble(self, rs, rt, inst1, inst2):
        if(rs):
            reg = inst1.rs
        elif(rt):
            reg = inst1.rt
        else:
            print("Error line 388")
            exit()
            
        if(self.bubble == None): #create class
            self.bubble = Bubble(inst1.instructionName, inst2.instructionName , 0)
            regInt = func_dictionary[inst2.instructionBin][3]
            if(regInt == 1):
                self.bubble.regStoreConflict = inst2.rd
            elif(regInt == 2):
                self.bubble.regStoreConflict = inst2.rt
            
            else:
                print("Error... should not reach line 400")
                exit()
        
        #either way we run this line
        #just append the other register conflict
        self.bubble.regConflicts.append(reg)
        
            
        
    def addHazard(self, rs, rt, stallCount):
        global ForwardADCount
        global ForwardBDCount
        global EqualDCount
        self.stall = stallCount #we need to add a stall in here
        if(rs):
            self.ForwardAD = 1 #update execute forward
            self.EqualD = 1
            ForwardADCount += 1 
            EqualDCount += 1
        elif(rt):
            self.ForwardBD = 1
            self.EqualD = 1
            ForwardBDCount += 1 
            EqualDCount += 1
        
    def output(self):
        if(self.ForwardAD == 1):
            print("\tForwardAD activated")
        elif(self.ForwardBD == 1):
            print("\tForwardBD activated")
        else:
            print(noHaz)
        

class Execute:
    def __init__(self):
        self.SrcAE = 0
        self.SrcBE = 0
        self.bubble = None
        self.stall = 0 #tells the pipeline to wait x times 
        self.WriteDataE = 0 #note for myself... this is used as the address offset in lw sw
        #like sw $7, 0x2000($10) -> it would be used for $7
        
    def addHazard(self, rs, rt, stallCount, store): #store is a bool that is true if the inst is sw or sb
        global SrcAECount
        global SrcBECount
        global WriteDataECount
        self.stall = stallCount #we need to add a stall in here
        if(store):
            if(rs):
                self.SrcAE = 1 #update execute forward
                SrcAECount += 1
            elif(rt):
                self.WriteDataE = 1
                WriteDataECount += 1
        else:
            #its another compute comand
            if(rs):
                self.SrcAE = 1 #update execute forward
                SrcAECount += 1
            elif(rt):
                self.SrcBE = 1
                SrcBECount += 1
    
    def addBubble(self, rs, rt, inst1, inst2):
        if(rs):
            reg = inst1.rs
        elif(rt):
            reg = inst1.rt
        else:
            print("Error line 445")
            exit()
            
        if(self.bubble == None): #create class
            self.bubble = Bubble(inst1.instructionName, inst2.instructionName , 0)
            regInt = func_dictionary[inst2.instructionBin][3]
            if(regInt == 1):
                self.bubble.regStoreConflict = inst2.rd
            elif(regInt == 2):
                self.bubble.regStoreConflict = inst2.rt
            
            else:
                print("Error... should not reach line 457")
                exit()
        
        #either way we run this line
        #just append the other register conflict
        self.bubble.regConflicts.append(reg)
    
    def output(self):
        noHazard = True
        if(self.SrcAE == 1):
            print("\tSrcAE activated")
            noHazard = False
        elif(self.SrcBE == 1):
            print("\tSrcBE activated")
            noHazard = False
        if(self.WriteDataE == 1):
            print("\tWriteDataE activated")
            noHazard = False
        if(noHazard):
            print(noHaz)
        

class Memory:
    def __init__(self):
        self.ALUOutM = 0 #send back data
        self.stall = 0 #tells the pipeline to wait x times 
        self.bubble = None
    
    def output(self):
        if(self.ALUOutM == 1):
            print("\tALUOutM is sending data")
        else:
            print(noHaz)

class Write:
    def __init__(self):
        self.ResultW = 0 #send data back
        self.stall = 0 #tells the pipeline to wait x times 
        self.bubble = None
        
    def output(self):
        if(self.ResultW == 1):
            print("\tResultW is sending data")
        else:
            print(noHaz)

            
            
def pausePipeline():
    keyPress = ''
    while(keyPress!='G' or keyPress != 'g'):
        keyPress = input("Press G to step, or press E to exit: ")
        if(keyPress=='g' or keyPress=='G'):
            keyPress = ''
            break
        elif (keyPress=='E' or keyPress == 'e'):
            exit()

        

def pipeline_main():
    asmInstructions = converter()
    read_file = open("machine-code.txt", "r")

    reader = read_file.readlines()

    for items in range(reader.count('\n')):
        reader.remove('\n')

    instructionsCopy = []
    cycleCount = 0
    line = reader[0]
    asm = asmInstructions[0]
    print("reader: " + str(len(reader)))
    print("asm: " + str(len(asmInstructions)))
    
    print("Welcome to ECE366 Advanced MIPS  pipeline Simulator.  Please choose the mode of running: ")
    debugMode = True if int(input(" 1 = Debug Mode         2 = Normal Execution \n")) == 1 else False

    pipe = pipelineQueue()
    finish = 6 #this is because the pipeline needs to run all the way through
    while registers['pc'] / 4 < len(reader) or (finish > 0):
        if(finish == 6):
            line = line.replace("\n", "")
            line = line.replace(" ", "")

            instructionsCopy.append(line)
            sent = pipe.push(line, asm)#try to send instruction
        else:
            sent = pipe.push(None, "")#try to send instruction
        
        if(sent):
            
            registers['pc'] += 4
            
            if registers['pc'] / 4 != len(reader) and (finish == 6):
                
                index = (int)(registers['pc'] / 4)
                line = reader[index]
                if(index < len(asmInstructions)):
                    asm = asmInstructions[index]
                
            else:
                finish -= 1
            #print("finish: " + str(finish))
        #print("PC: " + str(registers['pc']))
        cycleCount += 1
        if (debugMode and (finish > 0)):
            print("Debug Mode cycle #" + str(cycleCount) + "\n")
            #print(asmInstructions)
            #print(reader)
            pipe.diagnositics()
            printRegisters() 
            print("-------------------------------------------------------------------")
            pausePipeline() #let them click through
    cycleCount -= 1            

    printRegisters() 
    print("Total Dynamic instrucions: ", dynamicInstructionCount)
    print("Total cycle count: ", cycleCount)
    
    print("Stall total due to branching: ", FlushStallCount)
    print("Stall total due to data hazards: ", DataStallCount)
    print("ALUOutM used: " + str(ALUOutMCount) + " times.")
    print("ResultW used: " + str(ResultWCount) + " times.")
    print("SrcAE used: " + str(SrcAECount) + " times.")
    print("SrcBE used: " + str(SrcBECount) + " times.")
    print("WriteDataE used: " + str(WriteDataECount) + " times.")
    print("EqualD used: " + str(EqualDCount) + " times.")
    print("ForwardAD used: " + str(ForwardADCount) + " times.")
    print("ForwardBD used: " + str(ForwardBDCount) + " times.")

def main():
    pipeline_main()

if __name__ == "__main__":
    main()
