# DEFCON 2021 Quals

# Tiamat

```
                          {\__--_/}                             /===-_---~~~~~~~~~------____
                          /'   (_/ \            {\__--_/}      |===-~___                _,-'
                 -==\    |0  0 _/)  \          /'   (_/  \   `//~  \   ~~~~`---.___.-~~
             ______-==|  / /~ ,_/<|  \       ||0  0 _/)| |    | |   \           _-~`
       __--~~~  ,-/-==\ o o _// >-<\  |     / /~ ,_/   | |   / |    `\        ,'
    _-~       /'    |   (^(~  | >-<|  |     o o _//|>-</ | / /       \      /
  .'        /       |     \   \_>-<|  |   (^(~   |_>-<|  | /'/         \   /'
 /  ____  /         |       \ |_>-<| |          /_>-<_| | _ /           \/'
/-'~    ~~~~~---__  |       /        \    ____  |_>-<_/ |           _--~`
                  \_|      /        _)  /^    ^ />-</ _/           //
                    '~~--_/      _-~/-| \      \   _/          __//
                   {\__--_/}    / \_>-|  {\_--__/}           _/
                   /'   (_/  _-~  | |_/|  \_)   '\         /
                  |0  0 _/) )-~     | ||  (\_ 0  0| --~~~~
                  / /~ ,_/       / /__>--  \_, ~\ \
                 o o _//        /-~_>---<    \_ o o
                 (^(~          /~_>---<__     | ~)^)
                ,/|           /__>--<__/     |   \.\
             ,//('(          |__>--<__|     /     \.\_         .----_
            ( ( '))          |__>--<__|    |       \. \       /' _---_~
         `-)) )) (           |__>--<__|    |         \.\_   /'  /     ~\`
        ,/,'//( (             \__>--<__\    \         \_.\ /'  //       ||
      ,( ( ((, ))              ~-__>--<_~-_  ~--____---'\.\_ /'/        /'
    `~/  )` ) ,/|                 ~-_~>--<_/-__          \_.\ /
  ._-~//( )/ )) `                    ~~-'_/_/ /~~~~~__--~~ \_\
   ;'( ')/ ,)(                              ~~~~~~~~~~       \\
  ' ') '( (/                                                  '\
    '   '  `


```

Tiamat is a license checking utility that runs 8 32-bit architectures from inside a MIPS ELF binary. The architecutres include:
- SPARC LE/EB  
- MIPS LE/EB
- ARM LE/EB
- RISCV LE/EB

An instruction's architecutre is determined by the tmap section inside the binary, which is then used by qemooo to generate the intermediate TCG code. 


# Setup
- Build the docker container under service
- Run it 
- Interact with it on port 5000

You can also run it locally 
`./qemooo ./liccheck.bin`

The liccheck.tasm is located at `service/src/chal_builder/liccheck.tasm`

To build and test the tasm file locally 
```
cd service/src/chal_builder
./test_compiler.sh liccheck.tasm "nnnnvvvvrrrrr"

```

To build qemooo, you will need to clone https://github.com/o-o-overflow/qemooo
In the `service/src` folder and then build a container using the `cjbuilder.dockerfile`


# Bugs
To complete the challenge, it is necessary to figure out how qemooo implements the various architectures and find the bugs that result from the interaction between them.

1. SPARC, RISCV, MIPS all use a hardwired 0 in r0; however, for ARM the r0 register is where the syscall results are stored.
2. SPARC registers skip every other one because it uses 64-bit register values, which means on a `mov` it will overwrite the adjacent register.
3. The file close for one of the actions was the syscall value for a different architecure.
4. Another action failed to close the file.


Good luck!









