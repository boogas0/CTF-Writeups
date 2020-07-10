# Fluff 64 bit

The problem told us this is similar to write4 so we know that the buffer overflow will occur at 40 characters and there should still be a pwnme function. Looking at this in a disassembler (I used Radare2 but you can use whatever you like) we can see that we still have usefulFunction which gives us a system() entry in the plt. But now we have questionableGadgets instead of usefulGadgets.

### questionableGadgets:
```Assembly
  400820:   41 5f                   pop    r15  
  400822:   4d 31 db                xor    r11,r11
  400825:   41 5e                   pop    r14  
  400827:   bf 50 10 60 00          mov    edi,0x601050
  40082c:   c3                      ret    
  40082d:   41 5e                   pop    r14  
  40082f:   4d 31 e3                xor    r11,r12
  400832:   41 5c                   pop    r12  
  400834:   41 bd 60 40 60 00       mov    r13d,0x604060
  40083a:   c3                      ret    
  40083b:   bf 50 10 60 00          mov    edi,0x601050
  400840:   4d 87 d3                xchg   r11,r10
  400843:   41 5f                   pop    r15  
  400845:   41 bb 50 20 60 00       mov    r11d,0x602050
  40084b:   c3                      ret    
  40084c:   41 5f                   pop    r15  
  40084e:   4d 89 1a                mov    QWORD PTR [r10],r11
  400851:   41 5d                   pop    r13  
  400853:   41 5c                   pop    r12  
  400855:   45 30 22                xor    BYTE PTR [r10],r12b
  400858:   c3                      ret    
  400859:   0f 1f 80 00 00 00 00    nop    DWORD PTR [rax+0x0]

```

We will use the same method that was used to solve write4: call system() with '/bin/sh'. All we need to call system('/bin/sh') is a gadget that can write to somewhere in memory and pop gadgets to go with it.

#### writeGadget:
```Assembly
  40084e:   4d 89 1a                mov    QWORD PTR [r10],r11
  400851:   41 5d                   pop    r13  
  400853:   41 5c                   pop    r12  
  400855:   45 30 22                xor    BYTE PTR [r10],r12b
  400858:   c3                      ret
```

This gadget is a good candidate for writing to memory. We can fill r13 with junk and zero out r12. r12 must be zero'ed out so that the xor instruction will not affect the data we just wrote. Luckily since we are using gets() to exploit this program we can write null bytes with no issue.

Now we just need to find gadgets to put the contents we want in r10 and r11... sadly there are no easy pop r10 or pop r11 gadgets. Now things start to get difficult and we have to use things like xchg and xor.

The gadget below means that as long as we can find a way to write to r11 or r10 then we will be able to xchg it with the other and then write to the first gadget again. So we only need to find one more gadget that can write to either r10 or r11.

#### xchgGadget:
```Assembly
  400840:   4d 87 d3                xchg   r11,r10
  400843:   41 5f                   pop    r15  
  400845:   41 bb 50 20 60 00       mov    r11d,0x602050
  40084b:   c3                      ret
```

Using the three gadgets below we can write to r11. We want to write the desired value of r10 to r11 first so that we can use the xchgGadget to populate r10 with the value we desire before we call writeGadget. Referencing the writeGadget above, r10 must have a value of somewhere in memory that is writable. A good place to look for that is the GOT section because it has to be writable in order for the GOT to accomplish its function. I chose 0x6010d0, because it was in a spot in memory not too far after the got but far enough that it shouldn't mess with anything. If you are having trouble finding the GOT section in radare2 use the command :iS which will give you addresses of the sections and then use the seek command. 

#### popR12:
```Assembly
  400832:   41 5c                   pop    r12  
  400834:   41 bd 60 40 60 00       mov    r13d,0x604060
  40083a:   c3                      ret
```

#### clearR11:
```Assembly
  400822:   4d 31 db                xor    r11,r11
  400825:   41 5e                   pop    r14  
  400827:   bf 50 10 60 00          mov    edi,0x601050
  40082c:   c3                      ret
```

#### xorR11R12:
```Assembly
  40082f:   4d 31 e3                xor    r11,r12
  400832:   41 5c                   pop    r12  
  400834:   41 bd 60 40 60 00       mov    r13d,0x604060
  40083a:   c3                      ret
```

##### Steps to write to r11:
1. Use the popR12 gadget to write 0x6010d0 (where we will put '/bin/sh\x00') into r12.
2. Use the clearR11 gadget to zero out r11 (anything xor'ed with itself is 0)
3. Use the xorR11R12 gadget to write r12's contents to r11. (anything xor'ed with 0 is itself)
   - Also thinking ahead. Now is a good time to write to r12 what we want in r11 ('/bin/sh\x00') since there is a pop r12 in the xorR11R12 gadget

Now r11 has the value we want in r10 before we use writeGadget.

Use the xchgGadget to put r11's contents in r10.

Repeat the write to r11 process skipping the first step because the side effect of step 3 made it so we can skip step 1.

Now both r11 and r10 should have the values they need to call writeGadget. Don't forget to put junk on the stack for the two pop's after the mov instruction.

All that is left is calling system('/bin/sh\x00') using the address of the entry of system in the plt.

To call system with an argument we need to put the argument in rdi. There are no pop rdi instructions in questionableGadgets however using ropper or any ropping tool you should be able to find one. (0x4008c3) You can find where you should put your arguments for function calls in a table at the bottom of this [wikipedia article](https://en.wikipedia.org/wiki/X86_calling_conventions#cite_note-AMD-24), it is based off architecture and compiler. Since you were given the binary and not the source, everyone should be the same and use rdi for this challenge.

Pop the data segment (0x6010d0) into rdi and put system_plt entry on the stack and you will call system with 'bin/sh\x00' giving you a shell to cat the flag. You could continue the process above and instead of calling system with 'bin/sh\x00' call it with 'cat flag.txt\x00' but that would take another writeGadget including all the setup that goes into writeGadget.
