// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

// Put your code here.

(START)
	@16383
	D=A
	@R0 // CURRENT PIXEL
	M=D
	@KBD
	D=M
	@TURNON
	D;JNE
	@TURNOFF
	0;JMP

(TURNON)
	@R0
	M=M+1
	AD=M
	M=-1
	@24575
	D=D-A
	@TURNON
	D;JLT
	@START
	0;JMP

(TURNOFF)
	@R0
	M=M+1
	AD=M
	M=0
	@24575
	D=D-A
	@TURNOFF
	D;JLT
	@START
	0;JMP