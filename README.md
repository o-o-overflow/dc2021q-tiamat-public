# DEFCON 2021 Quals

**IF YOU CHANGE THE PUBLIC FILES DURING THE GAME MAKE SURE TO NOTIFY EVERYONE, AND DOUBLE-CHECK THE SCOREBOARD**




# Qemu build

```
../configure --disable-system --enable-linux-user --target-list=arm-linux-user,i386-linux-user,mipsel-linux-user,riscv32-linux-user,sparc32plus-linux-user --enable-debug --disable-werror --enable-debug-info --enable-debug-tcg --enable-trace-backends=simple`


alter ninja.build
libqemu-arm-linux-user.fa.p/target_arm_vec_helper.c.o libqemu-arm-linux-user.fa.p/target_arm_translate.c.o libqemu-arm-linux-user.fa.p/target_arm_cpu.c.o libqemu-arm-linux-user.fa.p/target_arm_debug_helper.c.o libqemu-arm-linux-user.fa.p/target_arm_neon_helper.c.o libqemu-arm-linux-user.fa.p/target_arm_tlb_helper.c.o libqemu-arm-linux-user.fa.p/target_arm_kvm-stub.c.o libqemu-arm-linux-user.fa.p/target_arm_cpu_tcg.c.o libqemu-arm-linux-user.fa.p/target_arm_arm-semi.c.o libqemu-arm-linux-user.fa.p/target_arm_gdbstub.c.o libqemu-arm-linux-user.fa.p/target_arm_m_helper.c.o libqemu-arm-linux-user.fa.p/target_arm_vfp_helper.c.o libqemu-arm-linux-user.fa.p/target_arm_crypto_helper.c.o libqemu-arm-linux-user.fa.p/target_arm_helper.c.o libqemu-arm-linux-user.fa.p/target_arm_op_helper.c.o libqemu-arm-linux-user.fa.p/target_arm_iwmmxt_helper.c.o 


libqemu-sparc32plus-linux-user.fa.p/target_sparc_win_helper.c.o libqemu-sparc32plus-linux-user.fa.p/target_sparc_fop_helper.c.o libqemu-sparc32plus-linux-user.fa.p/target_sparc_gdbstub.c.o libqemu-sparc32plus-linux-user.fa.p/target_sparc_cc_helper.c.o libqemu-sparc32plus-linux-user.fa.p/target_sparc_vis_helper.c.o libqemu-sparc32plus-linux-user.fa.p/target_sparc_mmu_helper.c.o libqemu-sparc32plus-linux-user.fa.p/target_sparc_cpu.c.o libqemu-sparc32plus-linux-user.fa.p/target_sparc_ldst_helper.c.o libqemu-sparc32plus-linux-user.fa.p/target_sparc_translate.c.o libqemu-sparc32plus-linux-user.fa.p/target_sparc_int64_helper.c.o libqemu-sparc32plus-linux-user.fa.p/target_sparc_helper.c.o  libqemu-sparc32plus-linux-user.fa.p/gdbstub.c.o

 /target_riscv_op_helper.c.o /target_riscv_fpu_helper.c.o /target_riscv_cpu.c.o /target_riscv_translate.c.o /target_riscv_cpu_helper.c.o /target_riscv_csr.c.o /target_riscv_vector_helper.c.o /target_riscv_gdbstub.c.o
 
#bin utils build
export TARGET=sparc-unknown-linux-gnu     
export PREFIX="/opt/sparc"     
export PATH="$PREFIX/bin:$PATH"

##binutils 
BINUTILS_VERSION=2.29.1; wget ftp://ftp.gnu.org/gnu/binutils/binutils-$BINUTILS_VERSION.tar.gz
`./configure \
  --target=$TARGET \
  --prefix=$PREFIX \
  --with-sysroot \
  --disable-nls \
  --disable-werror`

`make -j100 && make install`

##gcc 7.2.0
GCC_VERSION=7.2.0; wget ftp://ftp.gnu.org/gnu/gcc/gcc-$GCC_VERSION/gcc-$GCC_VERSION.tar.gz

`./contrib/download_prerequisites`

`./configure \
  --target=$TARGET \
  --prefix=$PREFIX \
  --enable-languages=c,c++ \
  --without-headers \
  --disable-nls \
  --disable-shared \
  --disable-decimal-float \
  --disable-threads \
  --disable-libmudflap \
  --disable-libssp \
  --disable-libgomp \
  --disable-libquadmath \
  --disable-libatomic \
  --disable-libmpx \
  --disable-libcc1  
make -j100 all-gcc && make install-gcc` 




__jmpbuf = {0x555555c445e0, 0xca267863c38ecd0, 0x5555555e1cf0, 0x7fffffffe0e0, 0x0, 0x0, 0xca267863ff8ecd0, 0x59f732b5d06eecd0},

```

