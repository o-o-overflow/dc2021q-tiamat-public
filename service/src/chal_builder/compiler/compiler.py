#! /usr/bin/env python3
import os
import random
import re
import struct
import subprocess
import sys
from . import *
from . import REG_EQUIV
from .gcc_compiler import GCCCompiler



class Compiler:


    def __init__(self):
        self.base_template_fpath = os.path.join("/tmp", "auto_base_mipsel")

        self._outd = None
        self._base_start = 0

        self._asm = []
        self._data = ""
        self.auto_template_fpath = ""
        self._extra_insns = 0
        self._label_cnt = 0
        self._cjasm_lines = 0
        self.DATA_BUFF_LEN = 1000
        self.asm_dump_fpath = ""

    def get_treasure_map(self):
        endian_tracker = {SPARC: 0, RISCV: 0, ARM: 0, MIPS: 0}
        out_arch = ""
        for i in range(0, len(self._asm)):
            line = self._asm[i]
            for _ in line.get('mach', []):

                do_little_e = (endian_tracker[line['arch']] % 2) == 0
                endian_tracker[line['arch']] += 1
                ib = int.from_bytes(self.getarchbyte(line['arch'], do_little_e),"big")
                out_arch += f".byte {hex(ib)}\n"
        return out_arch

    def create_template(self, base_fpath):
        print(f"DATA BUFF LEN = {self.DATA_BUFF_LEN}")
        nops = "nop\n" * (self.DATA_BUFF_LEN)

        labex = re.compile(r"^([a-zA-z0-9\.\_\-]+:)", re.MULTILINE)

        clean_data = labex.sub(r"", self._data)

        asm_template = f"""
.text
.globl __start
__start: ## Start of code section
{nops}
.section .data
datasection:
{clean_data}
.section .tmap
{self.get_treasure_map()}
"""

        #can i strip here?

        with open(f"{base_fpath}.s","w") as wf:
            wf.write(asm_template)

        auto_template_fpath = f"{base_fpath}.mipsel"

        subprocess.check_output(f"mipsel-linux-gnu-gcc -c -s {base_fpath}.s -o {base_fpath}.o && "
                                f"mipsel-linux-gnu-ld {base_fpath}.o -static -nostartfiles -nostdlib --Ttext-segment=0x10000 -o {auto_template_fpath}", shell=True)

        return auto_template_fpath, 0xd0


    @staticmethod
    def get_base_binary(base_fpath):
        with open(base_fpath, "rb") as rf:
            outd = bytearray(rf.read())

        base_start = 0xd0
        return outd, base_start

    def register_replace(self, arch, asm):

        asm = asm.replace("@const", "@r27")
        asm = asm.replace("@sp", "@r29")
        asm = asm.replace("@heap", "@r30")
        asm = asm.replace("@zero", "@r0") if arch != ARM else asm

        reg_regex = re.compile(r"(.*)(@r[0-9]+)(.*)")

        match = reg_regex.match(asm)
        while match:
            uniform_reg = match.group(2)
            asm = asm.replace(uniform_reg, REG_EQUIV[arch][uniform_reg])
            match = reg_regex.match(asm)

        return asm


    def parse(self, asm_fpath):
        with open(asm_fpath,"r") as rf:
            rawasm = rf.read()
        self.asm_dump_fpath = asm_fpath.replace(".cjasm", ".bin.dump")

        rex_asm = re.compile(r"^(?P<arch>[SPARCIVMPsparcrivmp]+)\s+(?P<asm>[\s\x24-\x3a\x3c-\x7f\:]+)[#\!;]*.*")  # letters minus !"#; used for comments
        rex_arm_asm = re.compile(
            r"^(?P<arch>[SPARCIVMPsparcrivmp]+)\s+(?P<asm>[\s#\x24-\x3a\x3c-\x7f]+)[@;]*.*")  # letters plus # for literals and comments only allow @;
        text_area = True

        last_was_label = False
        for line in rawasm.split("\n"):

            if line.startswith(".data"):
                text_area = False
                continue
            if text_area:
                match = rex_asm.match(line)
                ex_asm = ""
                if match:
                    arch = match["arch"].upper()
                    if last_was_label:
                        self._asm[-1]["arch"] = arch
                        self._asm[-1]["asm"] = match["asm"]
                    else:
                        self._asm.append(match.groupdict())

                    last_was_label = False
                    self._asm[-1]["arch"] = arch

                    if self._asm[-1]["arch"] == ARM:
                        match = rex_arm_asm.match(line)
                        self._asm[-1]["asm"] = match["asm"]

                    self._asm[-1]["asm"] = self.register_replace(arch, self._asm[-1]["asm"])

                    self._cjasm_lines += 1
                else:
                    match = self.match_label_line(line)

                    if match:
                        self._asm.append({"asm":"","arch":"ALL","label":match["label"]})

                        self._label_cnt += 1

                        self._cjasm_lines += 1
                        last_was_label =True


            else:
                self._data += line + "\n"

        self.DATA_BUFF_LEN += self._label_cnt

        self.pad_cjasm()
        #print(self._asm)

    def pad_cjasm(self):
        archs = [SPARC, RISCV, ARM, MIPS]
        asm_ins = len(self._asm)
        for x in range(asm_ins, self.DATA_BUFF_LEN):
            arch = random.choice(archs)
            self._asm.append({"arch": arch, "asm": "nop"})
        print(f"{len(self._asm)=}")


    def match_label_line(self, line_o_asm):
        label_rex = re.compile(r"^(?P<label>[a-zA-Z0-9_]+:)\s*[#!;@]*.*")
        match = label_rex.search(line_o_asm)
        return match

    def build_pre_nops(self, start, end_goal):
        pre_asm = ""
        label_cnt = 0
        for index in range(start, end_goal):
            line = self._asm[index]
            if line.get("label", None):
                pre_asm += "" + line["label"] + " \nnop\n"
                label_cnt += 1
            else:
                pre_asm += "nop\n"

        return pre_asm, label_cnt

    def compileline(self, lineno, offset):
        line = self._asm[lineno]
        #print(f'compline() {offset=} {line["arch"]=} {line["asm"]=}')
        #asm = "nop\n" * (offset + self._extra_insns)
        pre_insr_loc = offset + self._extra_insns
        asm, label_cnt = self.build_pre_nops(0, pre_insr_loc)

        #print(self.build_pre_nops(line["arch"], offset))
        if line.get("label",None):
            asm += line["label"] + "\n"
            print(f"{line['label']}   --> {line['asm']}")
            with open(f"{self.asm_dump_fpath}", "a") as wf:
                wf.write(f"{line['label']}   --> {line['asm']}\n")

        asm += line["asm"] + "\n"
        #asm += "nop\n" * (self.DATA_BUFF_LEN-offset-1 - self._extra_insns)
        # we need to know the number of labels and add to pre_insr_loc and self.DATA_BUFF_LEN
        #print(f"{pre_insr_loc=},{self._label_cnt=}, {label_cnt=}")
        temp_asm, temp_lc = self.build_pre_nops(pre_insr_loc+1, self.DATA_BUFF_LEN)
        asm += temp_asm
        label_cnt += temp_lc
        asm += f"datasection:\n{self._data}"

        with open(f"/tmp/{line['arch']}-pre-asm-{offset}.s","w") as wf:
            wf.write(asm)

        mach = None
        disas = None
        if offset <= self._cjasm_lines:
            cc = GCCCompiler(line["arch"])
            mach, disas = cc.compile(asm, offset + self._extra_insns)

            if disas:
                self._asm[lineno]["disas"] = disas[0]
                if offset <= self._cjasm_lines:
                    print(disas[0], end="")
                    with open(f"{self.asm_dump_fpath}", "a") as wf:
                        wf.write(disas[0])

            if mach:
                self._asm[lineno]["mach"] = [mach[0]]

            if len(mach) > 1:
                for extra in range(1, len(mach)):
                    newline = {"mach": [mach[extra]], "disas": disas[extra], "arch": self._asm[lineno]["arch"]}

                    self._asm.insert(lineno+1,newline)
                    self._extra_insns += 1
                    self._asm.pop()
                    if offset <= self._cjasm_lines:
                        print(disas[extra], end="")
                        with open(f"{self.asm_dump_fpath}", "a") as wf:
                            wf.write(disas[extra])
        else:
            rand_asm_entry = random.choice(self._asm[0:self._cjasm_lines])
            while rand_asm_entry.get("mach",None) == None:
                rand_asm_entry = random.choice(self._asm[0:self._cjasm_lines])
            mach = rand_asm_entry["mach"]
            self._asm[lineno]["mach"] = mach


        return len(mach)


    def compile(self):
        offset = 0
        lineno = 0
        with open(f"{self.asm_dump_fpath}", "w") as wf:
            wf.write("# generated assembly ")

        while lineno < len(self._asm):
            # if self._asm[lineno].get("label", None): # dont compile label lines, included as pre/post and should roughly be ignored
            #     print(self._asm[lineno]["label"])
            #     continue
            lineno += self.compileline(lineno, offset)
            offset += 1

    def _asm_out(self, outdata, outd_index, insn_bytes, arch, little_endian):
        bytesout = 0
        if little_endian:
            outdata[outd_index + 0] = insn_bytes[3]
            outdata[outd_index + 1] = insn_bytes[2]
            outdata[outd_index + 2] = insn_bytes[1]
            outdata[outd_index + 3] = insn_bytes[0]
            bytesout += 4
        else:
            outdata[outd_index + 0] = insn_bytes[0]
            outdata[outd_index + 1] = insn_bytes[1]
            outdata[outd_index + 2] = insn_bytes[2]
            outdata[outd_index + 3] = insn_bytes[3]
            # if arch == RISCV:
            #     outdata[outd_index] = insn_bytes[1]
            #     outdata[outd_index + 1] = insn_bytes[0]
            #     outdata[outd_index + 2] = insn_bytes[3]
            #     outdata[outd_index + 3] = insn_bytes[2]
            # else:
            #     outdata[outd_index + 0] = insn_bytes[3]
            #     outdata[outd_index + 1] = insn_bytes[2]
            #     outdata[outd_index + 2] = insn_bytes[1]
            #     outdata[outd_index + 3] = insn_bytes[0]
            bytesout += len(insn_bytes)
        return bytesout

    def getarchbyte(self, arch, do_little_e):
        if arch == SPARC:
            #bytes([random.randint(0,255)*4 % 255])
            if do_little_e:
                return bytes([(random.randint(0, 31) * 8) + 0])
            else:
                return bytes([(random.randint(0, 31) * 8) + 1])
        if arch == RISCV:
            if do_little_e:
                return bytes([(random.randint(0, 31) * 8) + 2])
            else:
                return bytes([(random.randint(0, 31) * 8) + 3])
        if arch == ARM:
            if do_little_e:
                return bytes([(random.randint(0, 31) * 8) + 4])
            else:
                return bytes([(random.randint(0, 31) * 8) + 5])
        if arch == MIPS:
            if do_little_e:
                return bytes([(random.randint(0, 31) * 8) + 6])
            else:
                return bytes([(random.randint(0, 31) * 8) + 7])

    def write(self, outfile):

        self.auto_template_fpath, entrypoint = self.create_template(self.base_template_fpath)
        self._outd, self._base_start = Compiler.get_base_binary(self.auto_template_fpath)

        with open(self.auto_template_fpath,"rb") as rf:
            outdata = bytearray(rf.read())
        print(f"created {self.auto_template_fpath}")

        outd_index = entrypoint
        out_arch = bytearray()
        endian_tracker = {SPARC: 0, RISCV: 0, ARM: 0, MIPS: 0}

        for i in range(0, len(self._asm)):
            line = self._asm[i]
            for insn_bytes in line.get('mach', []):
                do_little_e = (endian_tracker[line['arch']] % 2) == 0

                bytes_written = self._asm_out(outdata, outd_index, insn_bytes, line['arch'], do_little_e)
                if bytes_written > 0:
                    #print(outd_index, outdata[outd_index:outd_index+bytes_written])
                    endian_tracker[line['arch']] += 1
                    out_arch += self.getarchbyte(line['arch'], do_little_e)
                    outd_index += bytes_written
        print(f"{len(self._asm)=}")
        strrex = re.compile(r'.*(.string|.ascii).*"(?P<strdata>.*)"')

        extracted_data = strrex.findall(self._data)

        padded_data = ""
        for ed in extracted_data:
            tmp = ed[1].encode('latin-1').decode('unicode-escape') + "\x00"
            padded_data += tmp

        padded_data = padded_data + "\x00" * (4 - (len(padded_data) % 4))

        for x in range(0, len(padded_data), 4):
            thestr = padded_data[x:x + 4].encode('latin-1')
            value = struct.unpack("<I", thestr)
            value = int.to_bytes(value[0], length=4, byteorder="little", signed=False)
            for byt in value:
                outdata[outd_index] = byt
                outd_index += 1
            #print(outdata[outd_index-4:outd_index])
        print(f"Writing out to {outfile}")

        with open(outfile,"wb") as wf:
            wf.write(outdata)


        os.system(f"chmod +x {outfile}")











