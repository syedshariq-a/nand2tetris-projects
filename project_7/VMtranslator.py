# I TESTED THE FUNCTIONS USING SIMPLE NAMES.IT THROWS ERRORS IN YOUR FUNCTION.on print line 228.

import sys
from pathlib import Path

class Parser(object):
    '''Parses a single vm file to provide convenient access to the
    contained commands and their components.
    '''

    def __init__(self, fname):
        '''Opens the input file at fname and get ready to parse it.
        '''
        self._file = open(fname,'r')
        self._lines = self._file.read().split('\n')
        self._currline = -1
        self._current = ''
        pass
    
    def __str__(self):
        '''Leave as is.'''
        return 'Parser object'

    def hasMoreCommands(self):
        '''P.hasMoreCommands() -> bool

        Returns True if there are commands in the input, False
        otherwise.
        '''
        return self._currline<len(self._lines)-1
        pass

    def advance(self):
        '''P.advance() -> None

        Makes the next command the current command. Should be called
        only if hasMoreCommands() is True.
        '''
        self._current = self._lines[self._currline+1]
        self._currline+=1
        
        pass

    def commandType(self):
        '''P.commandType() -> str

        Returns the type of the current VM command: one of
        C_ARITHMETIC
        C_PUSH, C_POP
        C_LABEL
        C_GOTO
        C_IF
        C_FUNCTION
        C_RETURN
        C_CALL
        '''
        if 'push' in self._current.split(' ')[0]:
            return 'C_PUSH'
        if 'pop' in self._current.split(' ')[0]:
            return 'C_POP'
        if self._current.split(' ')[0] in ['add','sub','neg','eq','gt','lt','and','or','not']:
            return 'C_ARITHMETIC'
        
        pass

    def arg0(self):
        if self.commandType() == 'C_PUSH' or self.commandType() == 'C_POP':
            return self._current.split(' ')[0]
    def arg1(self):
        '''P.arg1() -> string

        Returns the first argument of the current command. In the case
        of C_ARTIHMETIC, the command itself (e.g. sub, add) is
        returned. Should not be called if the current command is
        C_RETURN.
        '''
        if self.commandType() == 'C_PUSH' or self.commandType() == 'C_POP':
            return self._current.split(' ')[1]
        if self.commandType() == 'C_ARITHMETIC':
            return self._current.split(' ')[0]
            
        pass

    def arg2(self):
        '''P.arg2() -> int

        Returns the second argument of the current command. Should be
        called only if the current command is any of
        C_PUSH
        C_POP
        C_FUNCTION
        C_CALL
        '''
        if self.commandType() == 'C_PUSH' or self.commandType() == 'C_POP':
            return int(self._current.split(' ')[2])
        if self.commandType() == 'C_FUNCTION':
            return int(self._current.split(' ')[2])
        if self.commandType() == 'C_CALL':
            return int(self._current.split(' ')[2])
        
        pass
    
class CodeWriter(object):
    '''Translates VM commands into Hack assembly code.'''
    
    def __init__(self, fname):
        '''Opens the output file at fname and gets ready to write to it.'''
        self._fout = open(fname,'w')
        self._currvm = ''
        self._seg = {'local':'LCL','argument':'ARG','this':'THIS','that':'THAT','temp':'5'}
        self._count = 0
        pass
    
    def __str__(self):
        '''Leave as is.'''
        return 'CodeWriter object.'

    def setFileName(self, fname):
        '''CW.setFileName(str) -> None

        Informs the code writer that the translation of the VM file at
        fname is to be started.
        '''
        self._currvm = fname[:-3]
        pass
    
    def writeArithmetic(self, command):
        '''CW.writeArithmetic(str) -> None

        Writes to the output file the assmebly code that is the
        translation of the given arithmetic command.
        '''
        arith = {'add':'A=A-1\nM=M+D\n',
                       'sub':'A=A-1\nM=M-D\n',
                       'gt':'A=A-1\nD=M-D\nM=-1\n@TRUE.'+str(self._count)+'\nD;JGT\n@SP\nA=M-1\nM=0\n(TRUE.'+str(self._count)+')\n',
                       'eq':'A=A-1\nD=M-D\nM=-1\n@TRUE.'+str(self._count)+'\nD;JEQ\n@SP\nA=M-1\nM=0\n(TRUE.'+str(self._count)+')\n',
                       'lt':'A=A-1\nD=M-D\nM=-1\n@TRUE.'+str(self._count)+'\nD;JLT\n@SP\nA=M-1\nM=0\n(TRUE.'+str(self._count)+')\n',
                       'not':'M=!D\n@SP\nM=M+1\n',
                       'neg':'M=-D\n@SP\nM=M+1\n',
                       'and':'A=A-1\nM=M&D\n',
                       'or':'A=A-1\nM=M|D\n'}
        self._fout.write('//'+command+'\n')
        self._fout.write('@SP\nAM=M-1\nD=M\n')
        if command in arith:
            self._fout.write(arith[command])
            if command in ['gt','eq','lt']:
                self._count+=1

    def writePushPop(self, command,segment,argument):
        '''CW.writePushPop(str) -> None

        Writes to the output file the assmebly code that is the
        translation of the given command, where command is either
        C_PUSH or C_POP.
        '''
        self._fout.write('//'+command+' '+segment+' '+str(argument)+'\n')
        if command == 'push':
            if segment == 'constant':
                self._fout.write('@'+str(argument)+'\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
            elif segment in self._seg:
                self._fout.write('@'+str(argument)+'\nD=A\n@'+self._seg[segment]+'\nAD=D+M\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
            elif segment == 'static':
                self._fout.write('@'+self._currvm+'.'+str(argument)+'\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
            elif segment == 'pointer' and (argument==0):
                self._fout.write('@THIS\n'+'\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
            elif segment == 'pointer' and argument==1:
                self._fout.write('@THAT\n'+'\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        if command == 'pop':
            if segment in self._seg:
                self._fout.write('@'+self._seg[segment]+'\nD=M\n@'+str(argument)+'\nD=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n')
            elif segment == 'static':
                self._fout.write('@SP\nAM=M-1\nD=M\n@'+self._currvm+'.'+str(argument)+'\nM=D\n')
            elif segment == 'pointer' and argument==0:
                self._fout.write('@SP\nAM=M-1\nD=M\n@THIS\nM=D\n')
            elif segment == 'pointer' and argument==1:
                self._fout.write('@SP\nAM=M-1\nD=M\n@THAT\nM=D\n')
        pass
    def writeInit(self):
        self._fout.write('@256\nD=A\n@SP\nM=D')
        pass
    def writeLabel(self,label):
        self._fout.write('('+label+')')
        pass
    def writeGoto(self,label):
        self._fout.write('@'+label+'\n0;JMP')
        pass
    def writeIf(self,label):
        self._fout.write('@'+label+'\nD;JEQ')
        pass
    def writeCall(self,functionName,numArgs):
        a = ['push return-address','push LCL','push ARG','push THIS','push THAT','ARG=SP-n-5','LCL=SP','goto f']
        self._fout.write('@')
        pass
    def writeReturn(self):
        b= ['FRAME = LCL','RET = *(FRAME-5)','*ARG = pop()','SP=ARG+1','THAT = *(FRAME-1)','THIS = *(FRAME-2)','ARG = *(FRAME-3)','LCL = *(FRAME-4)','goto RET']
        pass
    def writeFunction(self,functionName,numLocals):
        c = []
        pass

    def close(self):
        '''CW.close() -> None

        Close the output file.
        '''
        self._fout.write('(END)\n@END\n0;JMP')
        self._fout.close()
        pass

def printUsage():
    '''printUsage() -> None
    
    Prints infomration on how to call this file.
    '''
    print("Usage: VMtranslator source")
    print("source is one of")
    print("\ta .vm file\n\ta directory containing .vm files")

def getFileNames():
    '''getFileNames() -> tuple

    Returns a tuple contianing the name of the output ASM file and a
    list of names of the VM files to operate on, as per the call to
    the program from command line.
    '''
    if len(sys.argv) != 2:
        printUsage()
        print('Invalid call:', end=' ')
        for x in sys.argv:
            print(x, end=' ')
        print()
        sys.exit()  # End program.
    p = Path(sys.argv[1])
    fname = str(p)
    if p.is_dir():
        while fname[-1] == '/':
            fname = fname[:-1]
        asmFname = fname + '.asm'
        vmFiles = list(p.glob('*.vm'))
    elif fname[-3:] == '.vm' and p.exists():    
        asmFname = fname[:-3]+'.asm'
        vmFiles = [p]
    else:
        printUsage()
        print('Invalid file:', fname,'\nAborting!')
        sys.exit() # End program.
    vmFiles = [str(f) for f in vmFiles]
    return (asmFname, vmFiles)

def main():
    asmFname, vmFiles = getFileNames()
    # asmFname now contains the name of the file to output to.
    # vmFiles is a list contianing the names of VM files to be translated.
    d = CodeWriter(asmFname)
    for file in vmFiles:
        z = Parser(file)
        d.setFileName(file)
        while z.hasMoreCommands():
            z.advance()
            if z.commandType() == 'C_ARITHMETIC':
                d.writeArithmetic(z.arg1())
            if z.commandType() == 'C_PUSH' or z.commandType() == 'C_POP':
                d.writePushPop(z.arg0(),z.arg1(),z.arg2())   
    d.close()
    
if __name__ == "__main__":
    # Leave as is.
    main()
