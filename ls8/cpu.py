"""CPU functionality."""
import os
import sys

SP = 0x07
END = 0x04
SET_IR = 0x04
HEAD = 0xf4
SINGLE_BYTE = 0xff
SINGLE_BIT = 0x01
CMP_CLEAR = 0b11111000
EQ = 0x01
GT = 0x02
LT = 0x04

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
ADD = 0b10100000
CALL = 0b01010000
RET = 0b00010001
ST = 0b10000100
CMP = 0b10100111

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = HEAD
        self.pc = 0
        self.fl = 0

        self.ops = {}
        self.ops[LDI] = self.handle_LDI
        self.ops[PRN] = self.handle_PRN
        self.ops[HLT] = self.handle_HLT
        self.ops[PUSH] = self.handle_PUSH
        self.ops[POP] = self.handle_POP
        self.ops[MUL] = self.handle_MUL
        self.ops[ADD] = self.handle_ADD
        self.ops[CMP] = self.handle_CMP
        self.ops[CALL] = self.handle_CALL
        self.ops[RET] = self.handle_RET
        self.ops[ST] = self.handle_ST

    def load(self):
        """Load a program into memory."""
        address = 0

        with open(os.path.join(sys.path[0], sys.argv[1]), 'r') as program:
            for line in program:
                split = line.split('#')
                instruction = split[0].strip()
                if instruction != '':
                    self.ram[address] = int(instruction, 2)
                    address += 1
        
        self.reg[END] = address

    def ram_read(self, mar):
        if mar < len(self.ram):
            return self.ram[mar]
        else:
            sys.exit(1)

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'CMP':
            self.fl &= CMP_CLEAR
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl |= LT
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl |= GT
            else:
                self.fl |= EQ
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

    def handle_LDI(self, *operands):
        self.reg[operands[0]] = operands[1]
    
    def handle_PRN(self, *operands):
        print(self.reg[operands[0]])
    
    def handle_HLT(self, *operands):
        sys.exit(0)
    
    def handle_MUL(self, *operands):
        self.alu('MUL', *operands)

    def handle_ADD(self, *operands):
        self.alu('ADD', *operands)

    def handle_CMP(self, *operands):
        self.alu('CMP', *operands)

    def handle_PUSH(self, *operands):
        if (self.reg[SP]-1) >= self.reg[SET_IR]:
            self.reg[SP] -= 1
            self.ram_write(self.reg[SP], self.reg[operands[0]])
        else:
            sys.exit(3)

    def handle_POP(self, *operands):
        self.reg[operands[0]] = self.ram_read(self.reg[SP])
        if self.reg[SP] < HEAD:
            self.reg[SP] += 1

    def handle_CALL(self, *operands):
        self.reg[SP] -= 1
        self.ram_write(self.pc + 2, self.reg[SP])
        self.pc = self.reg[operands[0]]

    def handle_RET(self, *operands):
        self.pc = self.ram_read(self.reg[SP])
        self.reg[SP] += 1

    def handle_ST(self, *operands):
        self.ram_write(self, self.reg[operands[1]], self.reg[operands[0]])

    def move_to_next_instruction(self, ir):
        pc_set = ir >> SET_IR
        pc_set = pc_set & 0x01
        if not pc_set:
            self.pc += (ir >> 0x06) + 1

    def run(self):
        """Run the CPU."""
        running = True
        
        while running:
            ir = self.ram_read(self.pc)
            op_a = self.ram_read(self.pc + 1)
            op_b = self.ram_read(self.pc + 2)
            self.trace()
            if ir in self.ops:
                # self.trace()
                self.ops[ir](op_a, op_b)
                self.move_to_next_instruction(ir)
            else:
                print('Error: unknown instruction ' + str(ir) + ' at ' + str(self.pc))
                sys.exit(1)
        running = False
