import sys
import os.path

class Parser(object):
    '''Parses a HACK assembly file.'''
    def __init__(self, fname):
        '''Constructor - opens the input file and gets ready to parse it.'''
        if os.path.isfile(fname):
            self._file = open(fname,'r')
            self._lines = self._file.read().split('\n')
            self._currline = -1
            self._current = ''
            self._currenttype = ''
            self.cleanup()
        else:
            print('file does not exist!')
        pass
    def cleanup(self): ## Removes all comments. Doesn't take into account multi line comments though.
        for i in range(len(self._lines)):
            self._lines[i] = str(self._lines[i]).split('//')[0]
            self._lines[i] = str(self._lines[i]).strip()
        while '' in self._lines:
            self._lines.remove('')
        
                
    def __str__(self):
        return 'Parser object'
        
    def hasMoreCommands(self):
        '''P.hasMoreCommands() -> bool

        Returns True if there are commands left to parse, False otherwise.
        '''
        return self._currline<len(self._lines)-1
        

    def advance(self):
        '''P.advance() -> None

        Makes the next command the current command. Should be called
        only if hasMoreCommands() is True. Initially there is no
        current command.
        '''
            
        self._current = self._lines[self._currline+1]
        self._current = self._current.replace('\n','')
        self._currline+=1
        
        pass

    def commandType(self):
        '''P.commandType() -> str

        Returns the type of the current command: one of
        A_COMMAND
        L_COMMAND
        C_COMMAND
        '''
        a = self._current

        if a[0] == '@': ## a[0] == '@' and a[1::].isnumeric() for @234 format.
            return 'A_COMMAND'
        if a[0] == '(' and a[1:-1:] not in ['(',')'] and a[-1]==')':
            return 'L_COMMAND'
        else:
            return 'C_COMMAND'
        pass
        
    def symbol(self):
        '''P.symbol() -> str

        Returns the symbol or decimal Xxx of the current
        command. Should be called only when commandType() is A_COMMAND
        or L_COMMAND.
        '''
        if self.commandType() == 'A_COMMAND':
            return self._current[1:]

        if self.commandType() == 'L_COMMAND':
            return self._current[1:-1]
        pass
    
    def dest(self): ## Alternate way is to just do everything before '=' but them if someone types DAM instead of AMD my program wouldn't detect that's why I used this approach.
        '''P.dest() -> str

        Returns the dest mnemonic (8 possibilities) in the current
        command. Should be called only when commandType() is
        C_COMMAND.
        '''
        a = ['0','0','0'] ##a = ['A','D','M'] 
        if '=' in self._current:
            if 'A' in self._current[:self._current.find('=')]:
                a[0]='1'
            if 'D' in self._current[:self._current.find('=')]:
                a[1]='1'
            if 'M' in self._current[:self._current.find('=')]:
                a[2]='1'
        d = {'110': 'AD', '011': 'MD', '100': 'A', '001': 'M', '101': 'AM', '111': 'AMD', '000': 'null', '010': 'D'}
        return d[''.join(a)]
        
    
    def comp(self):
        '''P.comp() -> str

        Returns the comp mnemonic (28 possibilities) in the current
        command. Should be called only when commandType() is
        C_COMMAND.
        '''
        cmd = self._current
        if '=' in self._current:
            cmd = self._current.split('=')[1]
            return cmd
        if ';' in cmd:
            comp = cmd.split(';')[0]
            return comp
        else:
            return 'null'
        
        
    def jump(self):
        '''P.jump() -> str

        Returns the jump mnemonic (8 possibilities) in the current
        command. Should be called only when commandType() is
        C_COMMAND.
        '''
        x = self._current
        if self.commandType() == 'C_COMMAND':
            if ';' in x:
                if x[x.find(';')+1:] in ['JMP','JNE','JEQ','JGT','JGE','JLT','JLE']:
                    return x[x.find(';')+1:]
            return 'null'
    
class Code(object):
    '''Gives binary codes for mnemonics as per the HACK machine language.'''

    def __init__(self):
        '''Constructor - initializes built-in codes.''' ## if they aren't to be used more than one time why initialize them under init and take up more memory for the object?
        self._d = {'A':'100','D':'010','M':'001','AM':'101','AD':'110','MD':'011','AMD':'111','null':'000'}
        pass

    def __str__(self):
        return 'Code object'

    def dest(self, mnemonic):
        '''C.dest(str) -> str

        Returns the binary code of the dest mnemonic.
        
        >>> C.dest('A')
        '100'
        '''
        
        return self._d[mnemonic]
    
    def comp(self, mnemonic):
        '''C.comp(str) -> str

        Returns the binary code of the comp mnemonic.
        
        >>> C.comp('D-M')
        '1010011'
        '''
        comp = {'0':  '0101010','1':  '0111111','-1': '0111010','D':  '0001100', '!D': '0001101','-D': '0001111','D-1':'0001110','D+1':'0011111','null':'0000000', #non A/M
                'A':  '0110000','!A': '0110001','-A': '0110011','A+1':'0110111','A-1':'0110010','D+A':'0000010','A+D':'0000010','D-A':'0010011', ## A ones
                'A-D':'0000111','D&A':'0000000','D|A':'0010101','A&D':'0000000','A|D':'0010101',
                'M'  :'1110000','!M' :'1110001','-M' :'1110011','M+1':'1110111','M-1':'1110010','M+D':'1000010','D+M':'1000010','D-M':'1010011', ## M ones
                'M-D':'1000111','D&M':'1000000','D|M':'1010101','M&D':'1000000','M|D':'1010101'}
        return comp[mnemonic]
    
    def jump(self, mnemonic):
        '''C.jump(str) -> str

        Returns the binary code of the jump mnemonic.
        
        >>> C.jump('JGE')
        '011'
        '''
        j = {'JLT':'100','JEQ':'010','JGT':'001','JNE':'101','JLE':'110','JGE':'011','JMP':'111','null':'000'};
        return j[mnemonic]
        
class SymbolTable(object):
    '''Symbol table for the HACK machine language.'''
    def __init__(self):
        '''Constructor - initializes pre-defined symbols and addresses.'''
        self._nosym = 0
        self._table = {'R0':'0',
        'R1':1,
        'R2':2,
        'R3':3,
        'R4':4,
        'R5':5,
        'R6':6,
        'R7':7,
        'R8':8,
        'R9':9,
        'R10':10,
        'R11':11,
        'R12':12,
        'R13':13,
        'R14':14,
        'R15':15,
        'SP': 0,
        'LCL':1,
        'ARG':2,
        'THIS':3,
        'THAT':4,
        'KBD':24576,
        'SCREEN':16318}
        
        
    def ___str___(self):
        return 'SymbolTable object'

    def addEntry(self, symbol, address):
        '''ST.addEntry(str, int) -> None

        Adds the pair (symbol,address) to the table.
        '''
        if not self.contains(symbol):
            self._table[symbol] = address
            self._nosym+=1
        pass
    
    def contains(self, symbol):
        '''ST.contains(str) -> bool

        Returns True if symbol is contained in the table, False otherwise.
        '''
        return symbol in self._table.keys()
        pass

    def getAddress(self, symbol):
        '''ST.getAddress(str) -> int

        Returns the address of the symbol in the table. Should be
        called when contains(symbol) is True.
        '''
        return self._table[symbol]
        pass

def main():
    '''None -> Hack file

        Returns the processed hack file of the Assembly file.
        '''
    if len(sys.argv) != 2:
        print( "Usage: Assembler.py YourFile.asm" )
    else:
        fname = sys.argv[1]
        z = Parser(fname) ## Parser
        x = pass1(z) ## SymbolTable
        fout = open(fname[:-3]+'hack','w') # fname.replace('.asm','.hack')
        pass2(z,x,fout) ## Passes the symbol table and parser.


def pass1(z): ## (Parser.object)
    ''' pass1(Parser.object) -> SymbolTable.object

        In the first pass. the program finds and identifies all the labels. then adds them to the symbol table if they aren't already in there and return the symbol table.
        
        >>> pass1(Parser.object)
        'SymbolTable.object'
        '''
    ## need to check all the LABELS whether they are in the Symbol Table. If they aren't add (LABEL,address) to the symbol table.
    x = SymbolTable()
    while z.hasMoreCommands():
        z.advance()
        if z.commandType() == 'L_COMMAND' and not x.contains(z.symbol()):
            symno = x._nosym ## no. of labels already in the table.
            x.addEntry(z.symbol(),z._currline-symno)
    return x
                
def pass2(z,x,fout): ## (Parser,SymbolTable,OutputFile)
    ''' pass2(Parser.object,SymbolTable.object,InputFile) -> output .Hack file

        In the second pass. the program finds and parses all the other commands, doing two things at once.
        Firstly assigning Memory addresses to undefined variables.
        Secondly translating the Assembly code into Machine code to output the processed .hack file.
        >>> pass2(Parser.object,SymbolTable.object,InputFile)
        'Add.hack has been written successfully!''
        '''
    z._currline = -1
    b=16
    y=Code() ## Code Object
    while z.hasMoreCommands():
        z.advance()
        code=''
        if z.commandType() == 'A_COMMAND':
            if x.contains(z.symbol()): ## Present in list.
                code = '0'+ bin(int(x.getAddress(z.symbol())))[2:].zfill(15) ## The way i used for BinaryClock format(int(bin(int(x.getAddress(z.symbol())))[2:]),'015')
            elif z.symbol().isdigit(): ## Numeric
                code = '0'+ bin(int(z.symbol()))[2:].zfill(15)    ## The way i used for BinaryClock format(int(bin(int(z.symbol()))[2:]),'015')
            elif not x.contains(z.symbol()) and not z.symbol().isdigit(): ## A variable which isn't in the list
                code='0'+bin(b)[2:].zfill(15) ## ZFILL ADDS LEADING ZEROS.
                x.addEntry(z.symbol(),b)
                b=b+1   
        elif z.commandType() == 'C_COMMAND':
            code = '111'+y.comp(z.comp())+y.dest(z.dest())+y.jump(z.jump())
        elif z.commandType() == 'L_COMMAND': ## if it's a label just skip writing the line and return to next iteration.
            continue 
        fout.write(code+'\n') ## write our code to file and go to next line.
    print(fout.name,' has been written successfully!')
    
if __name__ == "__main__":
    main()
