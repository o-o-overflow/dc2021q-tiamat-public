import unittest
import subprocess
import os
import sys
import archr
import time

def base_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

class CompilerTest(unittest.TestCase):
    base_path = "//service/src/chal_builder"

    def build_binary(self, relative_test_fpath):
        with archr.targets.DockerImageTarget("cj/builder") as t:
            t.add_volume("/cooonj", "/cooonj")
            t.build()

            t.start(
                labels=[f"cjbuilder"],
            )
            base_test_fpath = f"{CompilerTest.base_path}/{relative_test_fpath}"
            binary_path = f"{base_test_fpath}.cjmips"

            compilecmd = ["bash", "-c",
                          "export PATH=$PATH:/opt/riscv/bin:/opt/sparc/bin && source /root/venv/bin/activate && cd /cooonj/service/src/chal_builder/ && "
                          f"python -m compiler {base_test_fpath}.cjasm -o {binary_path}"]

            p = t.run_command(compilecmd)

            stdout, stderr = p.communicate()
            print(stdout.decode('ascii'))
            print(stderr.decode('ascii'))

            return binary_path

    def test_writes(self):

        relative_test_fpath = f"/tests/test_writes"
        testbin = self.build_binary(relative_test_fpath)

        cmd = ["/cooonj/service/qemooo", testbin]

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = p.communicate()
        print(stdout.decode('ascii'))
        print(stderr.decode('ascii'))

        self.assertTrue(stdout.find(b"9AsparcBC") > -1, "SPARC failed to run")
        self.assertTrue(stdout.find(b"12riscv34") > -1, "RISCV failed to run")
        self.assertTrue(stdout.find(b"56arm78") > -1, "SPARC failed to run")

    def test_read_write(self):
        relative_test_fpath = f"/tests/test_read_write"
        testbin = self.build_binary(relative_test_fpath)

        cmd = ["/cooonj/service/qemooo", testbin]

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        inp = b"AABBCCDDEEF\n"
        stdout, stderr = p.communicate(input=inp)
        # print(stdout.decode('ascii'))
        # print(stderr.decode('ascii'))
        self.assertTrue(stdout.find(inp) > -1, "inp was not found in output")




if __name__ == '__main__':
    unittest.main()
