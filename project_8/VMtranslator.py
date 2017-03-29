import sys
import os
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
        currentCommand = self._current.split(' ')[0]
        if 'push' in self._current.split(' ')[0]:
            return 'C_PUSH'
        elif 'pop' in self._current.split(' ')[0]:
            return 'C_POP'
        elif self._current.split(' ')[0] in ['add','sub','neg','eq','gt','lt','and','or','not']:
            return 'C_ARITHMETIC'
        elif 'if-goto' in currentCommand:
            return 'C_IF'
        elif 'goto' in currentCommand:
            return 'C_GOTO'
        elif 'return' in currentCommand:
            return 'C_RETURN'
        elif 'call' in currentCommand:
            return 'C_CALL'
        elif 'function' in currentCommand:
            return 'C_FUNCTION'
        elif 'label' in currentCommand:
            return 'C_LABEL'
            
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
        if self.commandType() in ['C_PUSH', 'C_POP','C_LABEL','C_GOTO','C_IF','C_FUNCTION','C_CALL']:
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
        if self.commandType() in ['C_PUSH','C_POP','C_FUNCTION','C_CALL']:
            return int(self._current.split(' ')[2])
        
        pass
    
class CodeWriter(object):
    '''Translates VM commands into Hack assembly code.'''
    
    def __init__(self, fname):
        '''Opens the output file at fname and gets ready to write to it.'''
        self._fout = open(fname,'w')
        self._currvm = ''
        self._seg = {'local':'LCL','argument':'ARG','this':'THIS','that':'THAT'}
        self._seg2 = {'temp':5,'pointer':3}
        self._funcName = 'none'
        self._count = 0
        self._retcount = 0
        pass
    
    def __str__(self):
        '''Leave as is.'''
        return 'CodeWriter object.'

    def setFileName(self, fname):
        '''CW.setFileName(str) -> None

        Informs the code writer that the translation of the VM file at
        fname is to be started.
        '''
        fname = fname.split('\\')[-1]
        self._currvm = fname[:-3]
        pass

    def PushFromD(self):
        return '@SP\nAM=M+1\nA=A-1\nM=D\n'
    def PopToD(self):
        return '@SP\nAM=M-1\nD=M\n'
        
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
            elif segment == 'pointer' or segment == 'temp':
                self._fout.write('@R'+str(self._seg2[segment]+argument)+'\nD=M\n'+self.PushFromD())
        if command == 'pop':
            if segment in self._seg:
                self._fout.write('@'+self._seg[segment]+'\nD=M\n@'+str(argument)+'\nD=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n')
            elif segment == 'static':
                self._fout.write('@SP\nAM=M-1\nD=M\n@'+self._currvm+'.'+str(argument)+'\nM=D\n')
            elif segment == 'pointer' or segment == 'temp':
                self._fout.write(self.PopToD()+'@R'+str(self._seg2[segment]+argument)+'\nM=D\n')
                
    def writeInit(self):
        '''
        Writes to the output file the assembly code that is the translation of the bootstrap code for the file. It initializes SP to 256 and turns over the control to Sys.init
        '''
        self._fout.write('@256\nD=A\n@SP\nM=D\n')
        self.writeCall('Sys.init',0)
        pass
    def writeLabel(self,label):
        
        '''
        Writes to the output file the assembly code that is the translation of a given label command.
        '''
        self._fout.write('('+self._funcName+'$'+label+')\n')
        pass
    def writeGoto(self,label):
        '''
        Writes to the output file the assembly code that is the translation of a given if command.
        '''
        self._fout.write('@'+self._funcName+'$'+label+'\n0;JMP\n')
        
        pass
    def writeIf(self,label):
        '''
        Writes to the output file the assembly code that is the translation of a given if-goto command.
        '''
        self._fout.write('{}@{}${}\nD;JNE\n'.format(self.PopToD(),self._funcName,label))
        pass
    def writeCall(self,functionName,numArgs):
        '''
        Writes to the output file the assembly code that is the translation of a given call command.
        '''
        self._funcName = functionName
        self._retcount+=1
        self._fout.write('@return-address.'+str(self._retcount)+'\nD=A\n'+self.PushFromD())
        self._fout.write('@LCL\nD=M\n'+self.PushFromD())
        self._fout.write('@ARG\nD=M\n'+self.PushFromD())
        self._fout.write('@THIS\nD=M\n'+self.PushFromD())
        self._fout.write('@THAT\nD=M\n'+self.PushFromD())
        self._fout.write('@SP\nD=M\n@5\nD=D-A\n@'+str(numArgs)+'\nD=D-A\n@ARG\nM=D\n')
        self._fout.write('@SP\nD=M\n@LCL\nM=D\n')
        self._fout.write('@'+functionName+'\n0;JMP\n')
        self._fout.write('(return-address.'+str(self._retcount)+')\n')
        
        pass
    def writeReturn(self):
        '''
        Writes to the output file the assembly code that is the translation of a given return command.
        '''
        
        FRAME = 'R13'
        RET = 'R14'
        self._fout.write('@LCL\nD=M\n@'+FRAME+'\nM=D\n')
        self._fout.write('@'+FRAME+'\nD=M\n@5\nA=D-A\nD=M\n@'+RET+'\nM=D\n')
        self._fout.write(self.PopToD()+'@ARG\nA=M\nM=D\n')## *ARG = POP()
        self._fout.write('@ARG\nD=M\n@SP\nM=D+1\n') ##SP=ARG+1
        self._fout.write('@'+FRAME+'\nD=M\n@'+'1'+'\nA=D-A\nD=M\n@THAT\nM=D\n') ##THAT FRAME -1
        self._fout.write('@'+FRAME+'\nD=M\n@'+'2'+'\nA=D-A\nD=M\n@THIS\nM=D\n') #THIS FRAME -2
        self._fout.write('@'+FRAME+'\nD=M\n@'+'3'+'\nA=D-A\nD=M\n@ARG\nM=D\n') #ARG FRAME -3
        self._fout.write('@'+FRAME+'\nD=M\n@'+'4'+'\nA=D-A\nD=M\n@LCL\nM=D\n') #LCL FRAME -4
        self._fout.write('@'+RET+'\nA=M\n0;JMP\n')
        
        pass
    def writeFunction(self,functionName,numLocals):
        '''
        Writes to the output file the assembly code that is the translation of a given function command.
        '''
        self._fout.write('('+functionName+')\n')
        for i in range(numLocals):
            self.writePushPop('push','constant','0')
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
    '''
    The main functions which carrries out all the functionality.
    '''
    asmFname, vmFiles = getFileNames()
    d = CodeWriter(asmFname)
    for file in vmFiles:
        z = Parser(file)
        d.setFileName(file)
        if 'Sys.vm' in vmFiles:
            d.writeInit()
        while z.hasMoreCommands():
            z.advance()
            if z.commandType() == 'C_ARITHMETIC':
                d.writeArithmetic(z.arg1())
            if z.commandType() == 'C_PUSH' or z.commandType() == 'C_POP':
                d.writePushPop(z.arg0(),z.arg1(),z.arg2())
            if z.commandType() == 'C_FUNCTION':
                d.writeFunction(z.arg1(),z.arg2())
            if z.commandType() == 'C_CALL':
                d.writeCall(z.arg1(),z.arg2())
            if z.commandType() == 'C_RETURN':
                d.writeReturn()
            if z.commandType() == 'C_LABEL':
                d.writeLabel(z.arg1())
            if z.commandType() == 'C_IF':
                d.writeIf(z.arg1())
            if z.commandType() == 'C_GOTO':
                d.writeGoto(z.arg1())
    d.close()
    
    pass
    
if __name__ == "__main__":
    # Leave as is.
    main()
