#There was some messup with svn committing. Hence ungraded. Re-sending it anyway.

import sys
import re
from pathlib import Path

class JackTokenizer(object):
    '''Removes all comments and white space from the input stream and
    breaks it into Jack-language tokens, as specified by the Jack
    grammar.'''
    
    def __init__(self,inputFile):
        '''Constructor - Opens inputFile and gets ready to tokenize it.'''
        self._file = open(inputFile)
        self._text = self._file.read()
        self._tokens = []
        self._counter = -1
        self.token = ''
        self._keywords=['class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']
        self._symbols= ['{','}','(',')','.',',',';','+','-','*','/','&','|','<','>','=','~','[',']']
        self._Tokenize()
        self._xmlStyle = {"<":"&lt;", ">":"&gt;", '"':"&quot;", "&":"&amp;"}
        self._writeSimpleTokenFile(inputFile)
         

    def _Tokenize(self):
        self._text = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,self._text)
        self._text = re.sub(re.compile("//.*?\n" ) ,"" ,self._text)
        pattern = '|'.join(self._keywords)+'|"[^"]*"|\w+'+'|'+'|\\'.join(self._symbols)
        self._tokens = re.findall(pattern,self._text)

    def _writeSimpleTokenFile(self,inputFile):
        fname = inputFile.replace('.jack','T.xml')
        foutT = open(fname,'w')
        foutT.write('<tokens>\n')
        for i in self._tokens:
            if i in self._keywords:
                foutT.write('<keyword> '+i+' </keyword>\n')
            elif i in self._symbols:
                if i in self._xmlStyle:
                    i = self._xmlStyle[i]
                foutT.write('<symbol> '+i+' </symbol>\n')
            elif i[0] =='"' and i[-1] =='"':
                foutT.write('<stringConstant> '+i[1:-1] +' </stringConstant>\n')
            elif i.isdigit():
                foutT.write('<integerConstant> '+i+' </integerConstant>\n')
            elif i[0].isdigit() == False:
                foutT.write('<identifier> '+i+' </identifier>\n')
            else:
                print("Invalid Token")
                sys.exit(0)
        foutT.write('</tokens>\n')
        foutT.close()
                
    
    def hasMoreTokens(self):
        '''JT.hasMoreTokens() -> bool

        Returns True if there are more tokens left, False otherwise.'''
        return self._counter<len(self._tokens)
         
    
    
    def advance(self):
        '''JT.advance() -> None

        Gets the next token from the input and makes it the current
        token. Should only be called if hasmoreTokens() is
        True. Initially there is no current token
        '''
        if self.hasMoreTokens():
            self._counter+=1
            self.token = self._tokens[self._counter]
         

    def tokenType(self):
        '''JT.tokenType() -> str

        Returns the type of the current token which is one of:
        KEYWORD
        SYMBOL
        IDENTIFIER
        INT_CONST
        STRING_CONST
        '''
        if self.token in self._keywords:
            return 'KEYWORD'
        elif self.token in self._symbols:
            return 'SYMBOL'
        elif self.token.isdigit():
            return 'INT_CONST'
        elif ('"' == self.token[0] and '"' == self.token[-1]):
            return 'STRING_CONST'
        else:
            return 'IDENTIFIER'
    
    def keyWord(self):
        '''JT.keyWord() -> str

        Returns the keyword which is the current token. Should be
        called only when tokentype() is KEYWORD. Return value is one of:
        CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT,
        BOOLEAN, CHAR, VOID, VAR, STATIC, 'FIELD, LET,
        DO, IF, ELSE, WHILE, RETURN, TRUE, FALSE,
        NULL, THIS
        '''
        if self.tokenType() == 'KEYWORD':
            return self.token
         
    
    def symbol(self):
        '''JT.symbol() -> str

        Returns the character which is the current token. Should be
        called only when tokentype() is SYMBOL.
        '''
        if self.tokenType() == 'SYMBOL':
            return self.token
         
    
    def identifier(self):
        '''JT.identifier() -> str

        Returns the identifier which is the current token. Should be
        called only when tokenType() is IDENTIFIER.
        '''
        if self.tokenType() == 'IDENTIFIER':
            return self.token
         
    
    def intVal(self):
        '''JT.intVal() -> int

        Returns the integer value of the current token. Should be
        called only when tokenType() is INT_CONST.
        '''
        if self.tokenType() == 'INT_CONST':
            return int(self.token)
         
    
    def stringVal(self):
        '''JT.stringVal() -> str

        Returns the string value of the current token, without double
        quotes. Should be called only when TokenType() is
        STRING_CONST.
        '''
        if self.tokenType() == 'STRING_CONST':
            return self.token[1:-1]
         

class CompilationEngine(object):
    '''Effects the actual compilation output. Gets its input from a
    JackTokenizer and emits its parsed structure into an output file.
    '''

    def __init__(self,inputFile,outputFile):
        '''Constructor - Creates a new compilation engine with inputFile and
        outputFile. The next method called must be compileClass().
        '''
        self.fout = open(outputFile,'w')
        self.tokenizer = JackTokenizer(inputFile)
        self.indent = 1
        self._className=''
        self._statements={'let': 'letStatement>', 'if': 'ifStatement>', 'do':'doStatement>', 'while': 'whileStatement>', 'return': 'returnStatement>'}
         

        
    def _writeIdentifier(self):
        self.fout.write('  '*self.indent + '<identifier> '+self.tokenizer.identifier()+' </identifier>\n')
        self.tokenizer.advance()
    def _writeKeyword(self):     
        self.fout.write('  '*self.indent + '<keyword> '+ self.tokenizer.keyWord()+ ' </keyword>\n')
        self.tokenizer.advance()

    def _writeString(self):
        self.fout.write('  '*self.indent+'<stringConstant> '+ self.tokenizer.stringVal()+ ' </stringConstant>\n')
        self.tokenizer.advance()
    def _writeInt(self):
        self.fout.write('  '*self.indent + '<integerConstant> '+ str(self.tokenizer.intVal())+ ' </integerConstant>\n')
        self.tokenizer.advance()
    def _writeSymbol(self):
        self.fout.write('  '*self.indent + '<symbol> '+ self.tokenizer.symbol()+ ' </symbol>\n')
        self.tokenizer.advance()
    def _raiseError(self,x):
        print(x)
        sys.exit(0)
        #raise SyntaxError(x) I would prefer this but not using it since people tend to dislike exceptions.
    def compileClass(self):
        '''CE.compileClass() -> None

        Compiles a complete class.'''
        self.tokenizer.advance()

        ## class
        if self.tokenizer.token == 'class':
            self.fout.write('<class>\n')
            self._writeKeyword()
        else:
            self._raiseError("Keyword 'class' not found. ")

        if self.tokenizer.tokenType() == 'IDENTIFIER':
            self._writeIdentifier()
        else:
            self._raiseError("Class name not found. ")
        ## {
        self._checkSymbol('{')
        ## varDec
        while self.tokenizer.token in ['static', 'field']:
            self.fout.write('  '*self.indent+'<classVarDec>'+ '\n')
            self.indent+=1
            self._writeKeyword()
            self.compileClassVarDec()
            self.indent-=1
            self.fout.write('  '*self.indent+'</classVarDec>' + '\n')
        ## Subroutine
        while self.tokenizer.token in ['constructor', 'function', 'method']:
            self.fout.write('  '*self.indent+'<subroutineDec>\n')
            self.indent+=1
            self.compileSubroutine()
            self.indent-=1
            self.fout.write('  '*self.indent+'</subroutineDec>\n')
        ## }
        if self.tokenizer.token == '}':
           self.fout.write('  '*self.indent + '<symbol> '+ self.tokenizer.symbol()+ ' </symbol>\n')
           self.fout.write('</class>\n')
        else:
            self._raiseError("Symbol } not found. ")

    
    
    def compileClassVarDec(self):
        '''CE.compileClassVarDec() -> None
        
        Compiles a static declaration or a field declaration.
        '''

        #type
        if self.tokenizer.token in ['int', 'char', 'boolean']:
            self._writeKeyword()
        elif self.tokenizer.tokenType() == 'IDENTIFIER':
            self._writeIdentifier()
        else:
            self._raiseError("Valid variable type not found")
        #varName
        if self.tokenizer.tokenType() == 'IDENTIFIER':
            self._writeIdentifier()
        else:
            self._raiseError("Identifier varName not found")

        while self.tokenizer.token == ',':
            self._writeSymbol()
            if self.tokenizer.tokenType() == 'IDENTIFIER':
                self._writeIdentifier()
            else:
                self._raiseError("Identifier varName not found")
        # terminator
        self._checkSymbol(';')
        
    def compileSubroutine(self):
        '''CE.compileSubroutine() -> None

        Compiles a complete method, function, or constructor.
        '''
        ## method / function / constructor
        if self.tokenizer.token in ['function','constructor','method']:
            self._writeKeyword()
        ## return type
        if self.tokenizer.token in ['int', 'char', 'boolean','void']:
            self._writeKeyword()
        ## subroutine name
        elif self.tokenizer.tokenType() == 'IDENTIFIER':
            self._writeIdentifier()
        else:
            self._raiseError('subroutineName not defined')
        if self.tokenizer.tokenType() == 'IDENTIFIER':
            self._writeIdentifier()
        else:
            self._raiseError('subroutineName not defined')

        # (
        self._checkSymbol('(')
        self.compileParameterList()
        # )
        self._checkSymbol(')')
          
        ## THE BODY
        self.fout.write('  '*self.indent+'<subroutineBody>\n')
        self.indent+=1
        self._checkSymbol('{')
        # varDecs
        while self.tokenizer.token == 'var':
            self.fout.write('  '*self.indent+'<varDec>\n')
            self.indent+=1
            self.compileVarDec()
            self.indent-=1
            self.fout.write('  '*self.indent+'</varDec>\n')

        self.compileStatements()
        self._checkSymbol('}')
        self.indent-=1
        self.fout.write('  '*self.indent+'</subroutineBody>\n')
        
    def compileParameterList(self):
        '''CE.compileParameterList() -> None

        Compiles a (possible empty) parameter list not including the
        enclosing "()".
        '''
        self.fout.write('  '*self.indent + '<parameterList>\n')
        self.indent+=1

        #type
        if self.tokenizer.token == ')':
            self.indent-=1
            self.fout.write('  '*self.indent+'</parameterList>\n')
            return
        if self.tokenizer.token in ['int', 'char', 'boolean']:
            self._writeKeyword()
        elif self.tokenizer.tokenType() == 'IDENTIFIER':
            self._writeIdentifier()
        else:
            self._raiseError("Valid variable type not found")

        # WHILE A VALID TYPE
        while self.tokenizer.token in ['int', 'char', 'boolean'] or self.tokenizer.tokenType() == 'IDENTIFIER':
            if self.tokenizer.tokenType() == "IDENTIFIER":
                self._writeIdentifier()
            else:
                self._raiseError("Valid variable name not found")
            # deal with the next paramater
            if self.tokenizer.token == ',':
                self._writeSymbol()
                if self.tokenizer.token in ['int', 'char', 'boolean']:
                    self._writeKeyword()
                elif self.tokenizer.tokenType() == 'IDENTIFIER':
                    self._writeIdentifier()
            # Anything else found
            else:
                break
        
        self.indent-=1
        self.fout.write('  '*self.indent+'</parameterList>\n')
        
         

    def compileVarDec(self):
        '''CE.compileVarDec() -> None

        Compiles a var declaration.
        '''
        self._writeKeyword()
        #type
        if self.tokenizer.token in ['int', 'char', 'boolean']:
            self._writeKeyword()
        elif self.tokenizer.tokenType() == 'IDENTIFIER':
            self._writeIdentifier()
        else:
            self._raiseError("Valid variable type not found")
        while self.tokenizer.tokenType()== "IDENTIFIER":
            self._writeIdentifier()
            if self.tokenizer.token == ',':
                self._writeSymbol()
            else:
                break
        self._checkSymbol(';')
            
    def compileStatements(self):
        '''CE.compileStatements() -> None

        Compiles a sequence of statement not including the enclosing "{}".
        '''
        self.fout.write('  '*self.indent + '<statements>\n')
        self.indent+=1

        while self.tokenizer.token in self._statements:
            statement = self.tokenizer.token
            self.fout.write('  '*self.indent + '<' + self._statements[statement] +'\n')
            self.indent+=1
            if self.tokenizer.token == 'let':
                self.compileLet()
            elif self.tokenizer.token == 'do':
                self.compileDo()
            elif self.tokenizer.token == 'if':
                self.compileIf()
            elif self.tokenizer.token == 'while':
                self.compileWhile()
            elif self.tokenizer.token == 'return':
                self.compileReturn()
            self.indent-=1
            self.fout.write('  '*self.indent + '</' +self._statements[statement]+'\n')

        self.indent-=1    
        self.fout.write('  '*self.indent + '</statements>\n')
        
        

    def compileDo(self):
        '''CE.compileDo() -> None

        Compiles a do statement.
        '''
        self._writeKeyword()
        if self.tokenizer.tokenType() == "IDENTIFIER":
            self._writeIdentifier()
        else:
            self._raiseError("Valid identifier name not found")
        self._compileSubroutineCall()
        self._checkSymbol(';')

    def compileLet(self):
        '''CE.compileLet() -> None

        Compiles a let statement.
        '''
        self._writeKeyword()
        if self.tokenizer.tokenType() == "IDENTIFIER":
            self._writeIdentifier()
        else:
            self._raiseError("Valid identifier name not found")
        if self.tokenizer.token == '[': #array
            self._writeSymbol()
            self.compileExpression()
            self._checkSymbol(']')

        self._checkSymbol('=')
        
        self.compileExpression()
        
        self._checkSymbol(';')
        
    def _checkSymbol(self,sym):
        if self.tokenizer.token==sym:
            self._writeSymbol()
        else:
            self._raiseError("Symbol {} not found. ".format(sym))

    def compileWhile(self):
        '''CE.compileWhile() -> None

        Compiles a while statement.
        '''
        self._writeKeyword()
        self._checkSymbol('(')
        self.compileExpression()
        self._checkSymbol(')')
        self._checkSymbol('{')
        self.compileStatements()
        self._checkSymbol('}')
    
    def compileReturn(self):
        '''CE.compileReturn() -> None

        Compiles a return statement.
        '''
        if self.tokenizer.token == 'return':
            self._writeKeyword()
        else:
            self.raiseError("return statement not found")
        if self.tokenizer.token == ';':
            self._writeSymbol()
        else:
            self.compileExpression()
            self._checkSymbol(';')
            
    
    def compileIf(self):
        '''CE.compileIf() -> None

        Compiles an if statement possibly with a trailing else clause.
        '''
        self._writeKeyword()
        self._checkSymbol('(')
        self.compileExpression()
        self._checkSymbol(')')
        self._checkSymbol('{')
        self.compileStatements()
        self._checkSymbol('}')

        #else
        if self.tokenizer.token == 'else': 
            self._writeKeyword()
            self._checkSymbol('{')
            self.compileStatements()
            self._checkSymbol('}')
        
    
    def compileExpression(self):
        '''CE.compileExpression() -> None
        
        Compiles an expression.
        '''
        
        if self.tokenizer.token in [")", ';']:
            return
        self.fout.write('  '*self.indent+'<expression>\n')
        self.indent+=1
        self.compileTerm()
        while self.tokenizer.token in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            self._writeSymbol()
            self.compileTerm()
        self.indent-=1
        self.fout.write('  '*self.indent+'</expression>\n')


    def compileTerm(self):
        '''CE.compileTerm() -> None

        Compiles a term. Uses lookahead to decide between alternative
        parsing rules. If the current token is an indentifier, a
        look=ahead token of "[", "(", or "." distinguish between a
        variable, array, and subroutine call. Any other token is not
        part of this term and should not be advanced over.
        '''
        self.fout.write('  '*self.indent+'<term>\n')
        self.indent+=1
        _term = 0
        
        if self.tokenizer.intVal()!=None:
            self._writeInt()
            _term = 1
        elif self.tokenizer.stringVal()!=None:
            self._writeString()
            _term = 1
        elif self.tokenizer.keyWord() in ['true', 'false', 'null', 'this']:
            self._writeKeyword()
            _term = 1
        elif self.tokenizer.tokenType()== "IDENTIFIER":
            _term = 1
            self._writeIdentifier()
            if self.tokenizer.token in ['(','.']:
                self._compileSubroutineCall()
            else:
               if self.tokenizer.token == '[':
                   _term = 0
                   self._writeSymbol()
                   self.compileExpression()
                   if self.tokenizer.token == ']':
                       _term = 1
                       self._writeSymbol()
                   else:
                      self._raiseError("Symbol ']' not found") 
        elif self.tokenizer.token== "(":
           self._writeSymbol()
           self.compileExpression()
           if self.tokenizer.token == ')':
              self._writeSymbol()
              _term=1
           else:
              self._raiseError("Symbol ')' not found")  
        elif self.tokenizer.token in ['-','~']:
           self._writeSymbol()
           self.compileTerm()

        self.indent-=1
        self.fout.write('  '*self.indent+'</term>\n')		 
            
         

    def compileExpressionList(self):
        '''CE.compileExpressionList() -> None

        Compiles a (possibly empty) comma separated list of expressions.
        '''
        self.fout.write('  '*self.indent+'<expressionList>\n')
        self.indent+=1
        self.compileExpression()
        while self.tokenizer.token == ',':
            self._writeSymbol()
            self.compileExpression()
        self.indent-=1
        self.fout.write('  '*self.indent+'</expressionList>\n')
    def _compileSubroutineCall(self):
        if self.tokenizer.token ==  "(":
            self._writeSymbol()
            self.compileExpressionList()
            self._checkSymbol(')')
                
        elif self.tokenizer.token == '.':
            self._writeSymbol()
            if self.tokenizer.tokenType() == "IDENTIFIER":
                self._writeIdentifier()
                if self.tokenizer.token == '(':
                    self._writeSymbol()
                    self.compileExpressionList()
                    self._checkSymbol(')')

def printUsage():
    '''printUsage() -> None
    
    Prints infomration on how to invoke this program.
    '''
    print("Usage: {} dir".format(sys.argv[0]))
    print("dir is the program directory - it contains the .jack file(s) to be compiled.")

def getFileNames():
    '''getFileNames() -> list

    Returns a list containing the names of the Jack files in the given
    directory name. Prints help and exits this program gracefully if
    the program is invoked incorrectly.
    '''
    if len(sys.argv) != 2:
        printUsage()
        print('Invalid call:', str(sys.argv).translate(str.maketrans('','',"',[]")))
        sys.exit()
    p = Path(sys.argv[1])
    if not p.is_dir():
        printUsage()
        print('{} is not a directory'.format(p))
        sys.exit()
    jackFiles = list(p.glob('*.jack'))
    jackFiles = [str(f) for f in jackFiles]
    return jackFiles

def main():
    '''Compiles the Jack program in the directory whose name is supplied
    through the command line when invoking this program.
    '''
    jackFiles = getFileNames()
    vmFiles = [s.replace('.jack','.xml') for s in jackFiles]
    for i in range(len(jackFiles)):
        ce = CompilationEngine(jackFiles[i],vmFiles[i])
        ce.compileClass()
    # jackFiles contains the names of the Jack files to be compiled.
    # vmFiles contains the names of the corresponding vm files to be written to.
     

if __name__ == '__main__':
    '''Leave as is.'''
    main()
    
