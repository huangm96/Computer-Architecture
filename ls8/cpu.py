"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
PRA = 0b01001000

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Set up the branch table
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE
        self.branchtable[PRA] = self.handle_PRA
        
        
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0  # program counter
        self.sp = 7  # stack pointer
        self.fl = 0b00000000
        
    def ram_read(self, mar):
        print(self.reg[mar])
        return self.reg[mar]

    def ram_write(self, mar, mdr):
        self.reg[mar] = mdr

    def load(self):
        """Load a program into memory."""
        try:
            address = 0
            with open(sys.argv[1]) as f:
                # Read all the lines
                for line in f:
                    comment_split = line.strip().split("#")
                    # Cast the number from string to ints
                    value = comment_split[0].strip()
                    self.ram[address] = int(value,2)
                    address += 1
            print(self.ram)
        except FileNotFoundError:
            print("File not Found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            result = self.reg[reg_a] * self.reg[reg_b]
            self.reg[reg_a] = result
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_LDI(self):
        self.ram_write(self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def handle_PRN(self):
        self.ram_read(self.ram[self.pc + 1])
        self.pc += 2


    def handle_ADD(self):
        self.alu("ADD", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def handle_MUL(self):
        self.alu("MUL", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def handle_PUSH(self):
        # Grab the register argument.
        val = self.reg[self.ram[self.pc + 1]]
        # Copy the value in the given register to the address pointed to by SP.
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = val
        self.pc += 2
        

    def handle_POP(self):
        # Graph the value from the top of the stack
        val = self.ram[self.reg[self.sp]]
        # Copy the value from the address pointed to by SP to the given register.
        self.reg[self.ram[self.pc + 1]] = val
        self.reg[self.sp] += 1
        self.pc += 2
        return val

    def handle_CALL(self):
        # The address of the instruction directly after CALL is pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
        val = self.pc + 2
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = val

        # The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.
        self.pc = self.reg[self.ram[self.pc+1]]

    def handle_RET(self):
        # Return from subroutine.
        # Pop the value from the top of the stack and store it in the PC.
        self.pc = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1
        
    def handle_CMP(self):
        # Compare the values in two registers.
        # FL bits: 00000LGE
        val1 = self.reg[self.ram[self.pc + 1]]
        val2 = self.reg[self.ram[self.pc+2]]
        # If they are equal, set the Equal E flag to 1, otherwise set it to 0.
        if val1 == val2:
            self.fl = 0b00000001
        # If registerA is less than registerB, set the Less-than L flag to 1, otherwise set it to 0.
        elif val1 < val2:
            self.fl = 0b00000100
        # If registerA is greater than registerB, set the Greater-than G flag to 1, otherwise set it to 0.
        else:
            self.fl = 0b00000010
        self.pc += 3

    def handle_JMP(self):
        # Jump to the address stored in the given register.
        # Set the PC to the address stored in the given register.
        self.pc = self.reg[self.ram[self.pc+1]]

    def handle_JEQ(self):
        # If equal flag is set (true), jump to the address stored in the given register.
        if self.fl == 0b00000001:
            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    def handle_JNE(self):
        # If E flag is clear (false, 0), jump to the address stored in the given register.
        if self.fl != 0b00000001:
            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2
    def handle_PRA(self):
        # Print alpha character value stored in the given register.
            print("alpha character", self.reg[self.ram[self.pc + 1]])

        # Print to the console the ASCII character corresponding to the value in the register.
            print("ASCII", chr(self.reg[self.ram[self.pc + 1]]))
            self.pc += 2
            
    def run(self):
        while True:
            IR = self.ram[self.pc]
            if IR == HLT:
                print(self.ram)
                exit(2)
            self.branchtable[IR]()

