```
		MIPS			ARM			SPARC			RISCV
0	|	zero	        |	R 0	        |	----	      |	x0 -zero
1	|	at	        |	R 1 - arg 0	|	----- 	      |	x1 - ret addr
2	|	v0 - syscall #	|	R 2 - arg 1	|	g1 - syscal   |	x2 - sp
3	|	v1 - results	|	R 3 - arg 2	|	-----	      |	x3 - glbl ptr
4	|	arg 0	        |	R 4 - arg 3	|	g2 -	      |	x4 - thread ptr
5	|	arg 1	        |	R 5 - arg 4	|	-----	      |	x5 - t/s 0
6	|	arg 2	        |	R 6	        |	g3	      |	x6 - t/s 1
7	|	arg 3	        |	R 7 syscal# 	|	----	      |	x7 - t2
8	|	temp 0	        |	R 8	        |	g4	      |	x8 - s0/fp
9	|	temp 1	        |	R 9	        |	-----         |	x9 - s1
10	|	temp 2	        |	R 10	    	|	g5	      |	x10 - arg 0
11	|	temp 3	        |	R 11 - FP	|	-----	      |	x11 - arg 1
12	|	temp 4	        |	R 12	    	|	g6	      |	x12 - arg 2
13	|	temp 5	        |	R 13 - SP	|	-----	      |	x13 - arg 3
14	|	temp 6	        |	R 14 - LR 	|	g7	        |	x14 - arg 4
15	|	temp 7	        |	R 15 - PC	|		        |	x15 - arg 5
16	|	saved 0	        |		        |	        	|	x16 - arg 6
17	|	saved 1	        |		        |		        |	x17 - arg 7 - syscall #
18	|	saved 2	        |		        |		        |	x18 - save 2
19	|	saved 3	        |		        |		        |	x19 - save 3
20	|	saved 4	        |		        |			|	x20 - save 4
21	|	saved 5        	|		        |	       		|	x23 - save 5
22	|	save 6	        |		        |	         	|	x22 - save 6
23	|	saved 7	        |		        |	        	|	x23 - save 7
24	|	temp 8	        |		        |	        	|	x24 - save 8
25	|	temp 9	        |		        |	        	|	x25 - save 9
26	|	k0	            |		        |	        	|	x26 - save 10
27	|	k1	            |		        |	        	|	x27 - save 11
28	|	gp - globals	|		        |	        	|	x28 - temp 3
29	|	sp	            |		        |	        	|	x29 - temp 4
30	|	fp (ie saved 8)	|		        |	        	|	x30 - temp 5
31	|	ra	            |		        |	        	|	x31 - temp 6
```