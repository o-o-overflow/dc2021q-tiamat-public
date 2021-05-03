import os
import re
import subprocess

from . import *

class GCCCompiler:

    def __init__(self, arch, base_addr=0x100d0):
        self.arch = arch
        self.arch_gcc = self.get_arch_gcc(arch)
        self.arch_linker = self.get_arch_linker(arch)
        self.disasm_rex = self.get_disasm_rex(arch)
        self.asm_header = self.get_asm_header(arch)
        self.base_address = base_addr

    @staticmethod
    def get_asm_header(arch):


        if arch == SPARC:
            padding = "_padding:\n" + "nop; " * 31
            return f"""
    .section	".text"
    .global		_start
{padding}
_start:
"""
        if arch == RISCV:
            padding = "_padding:\n" + "nop; " * 31
            return f"""
	.text 
	.globl  _start
{padding}
_start:
"""
        if arch == MIPS:
            return f"""
.text
.globl __start
__start:             
"""
        if arch == ARM:
            padding = "_padding:\n" + "nop; " * 31
            return f"""
.section .text
.global  _start
.arm
{padding}
_start:             
"""

    @staticmethod
    def get_arch_gcc(arch):
        if arch == SPARC:
            return "sparc-unknown-linux-gnu-gcc"
        if arch == RISCV:
            return "riscv32-unknown-linux-gnu-gcc"
        if arch == MIPS:
            return "mipsel-linux-gnu-gcc"
        if arch == ARM:
            return "arm-linux-gnueabi-gcc"
        print(arch)
        assert False

    @staticmethod
    def get_arch_linker(arch):
        if arch == SPARC:
            return "sparc-unknown-linux-gnu-ld"
        if arch == RISCV:
            return "riscv32-unknown-linux-gnu-ld"
        if arch == MIPS:
            return "mipsel-linux-gnu-ld"
        if arch == ARM:
            return "arm-linux-gnueabi-ld"

    @staticmethod
    def get_disasm_rex(arch):
        if arch == RISCV or arch == MIPS:
            return rb"[ ]*[0-9a-f]+:[ ]*([0-9a-f]+)[ ]+([a-zA-Z0-9\-_\.\,\(\)\[\]\<\>\+ ;#]+)"
        if arch == SPARC:
            return rb"[ ]*[0-9a-f]+:[ ]*([0-9a-f]{2} [0-9a-f]{2} [0-9a-f]{2} [0-9a-f]{2})[ ]+([a-zA-Z0-9\%\-_\.\,\(\)\[\]\<\>\+ ]+)"
        if arch == ARM:
            return rb"[ ]*[0-9a-f]+:[ ]*([0-9a-f]+)[ ]+([a-zA-Z0-9\-_\.\,\(\)\[\]\<\>\+# @;]+)"

    def get_asm(self, obj_fpath, offset):
        cmd = ["objdump", "--disassemble-zeroes", "-D", obj_fpath]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output, err = p.communicate()

        if p.returncode != 0:
            print(f"{cmd=}")
            print(output.decode('latin-1'))
            print(err.decode('latin-1'))
            print("\n\n")
            raise Exception("Error with objdump")

        code_started = False
        #print(output.decode('latin-1'))
        start_rex = re.compile(rb"000100[0-9a-f]{2} <_+start>:")
        current_line = 0
        ret_asm = []
        saved_nop = None
        outlist = output.split(b"\n")
        start_point = 0
        # wait for _start in objdump output, then ignore NOPs until found, if none found return nop
        for i in range(0, len(outlist)):
            outline = outlist[i]
            if start_rex.match(outline):
                start_point = i + 1
                break

        target_start = self.base_address + offset * 4
        address_start = 0
        for i in range(start_point + offset, len(outlist)):
            outline = outlist[i].decode('latin-1').strip()
            if outline.startswith(f"{target_start:x}:"):
                address_start = i
                break
        assert address_start != 0

        # loop assumes instructions of interest start at offset and that offset matches incoming asm not necessarily outgoing
        for i in range(address_start, len(outlist)):
            outline = outlist[i]

            outline = outline.replace(b"\t", b" ")

            match = re.search(self.disasm_rex, outline)

            if match:
                # assuming little endian, but flipping b/c objdump displays little endian decoded
                vals = match.group(1).decode("latin-1").replace(" ", "")
                byteval = bytearray.fromhex(vals)
                byteval = int.to_bytes(int.from_bytes(byteval, "little"), length=(len(byteval)), byteorder="big", signed=False)

                if match.group(2).upper().startswith(b"NOP") and ret_asm:
                    break

                ret_asm.append((byteval, match.group(2)))

                if match.group(2).upper().startswith(b"NOP"): # only get 1 output nop at a time.
                    break

        return ret_asm

    def write_asm(self, asm, offset):
        asm_fpath = os.path.join("/tmp", f"{self.arch}-{offset}-asm")
        with open(asm_fpath + ".s", "w") as wf:
            wf.write(asm)
        return asm_fpath

    def remove_nops(self, nops_to_remove, asm, offset):
        data_section = asm.find("datasection")
        new_end_of_asm = data_section - (nops_to_remove*5)
        #print(f"{data_section=}, {new_end_of_asm=}")
        # the plus 1 keeps the \n at the end of the last removed nop
        asm = asm[:new_end_of_asm+1] + asm[data_section:]
        return asm

    def get_insns(self, asm, offset):
        asm_fpath = self.write_asm(asm, offset)
        sparc_cmd = [self.arch_gcc, "-c", f"{asm_fpath}.s", "-o", f"{asm_fpath}.o"]

        if self.arch == RISCV:
            sparc_cmd.append("-march=rv32i")

        p = subprocess.Popen(sparc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        if p.returncode != 0:
            print(output.decode('latin-1'))
            print(err.decode('latin-1'))
            raise Exception("Error with compile")

        sparc_cmd = [self.arch_linker, f"{asm_fpath}.o", "--Ttext-segment=0x10000" ]
        if self.arch == MIPS:
            sparc_cmd.extend(["-static", "-nostartfiles", "-nostdlib"])
        sparc_cmd.extend(["-o", f"{asm_fpath}.bin"])
        p = subprocess.Popen(sparc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        if p.returncode != 0:
            print(output.decode('latin-1'))
            print(err.decode('latin-1'))
            raise Exception("Error with link")

        asm_insns = self.get_asm(f"{asm_fpath}.bin", offset)
        return asm_insns

    def compile(self, asm, offset):
        mach = 0
        asm = f"{self.asm_header}{asm}"
        asm_insns = self.get_insns(asm, offset)
        # when greater than 1 it changes the offsets and we need to reduce the nops
        if len(asm_insns) > 1:
            nops_to_remove = len(asm_insns) - 1 # -1 for len and -1 for insn to ignore

            asm = self.remove_nops(nops_to_remove, asm, offset)
            asm_insns = self.get_insns(asm, offset)

        ret_bytes = []
        ret_disas = []

        for asm_pair in asm_insns:
            if self.arch == SPARC: # sparc is MSB (BE) by default, we will eventually make it the other way around methinks
                obyte = int.to_bytes(int.from_bytes(asm_pair[0], "little"), length=(len(asm_pair[0])),
                               byteorder="big", signed=False)
            else:
                obyte = int.to_bytes(int.from_bytes(asm_pair[0], "little"), length=(len(asm_pair[0])),
                                     byteorder="big", signed=False)
            ret_bytes.append(obyte)

            disas = f"#{offset} {self.base_address+(offset*4):06x}\t{self.arch}\t0x{obyte.hex():8s}\t{asm_pair[1].decode('latin-1')}"
            ret_disas.append(disas + "\n")


        return ret_bytes, ret_disas


