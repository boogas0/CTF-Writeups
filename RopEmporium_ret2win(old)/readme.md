# Ret2csu

This challenge has been recently updated this is how it used to be. The zip that you would grab from ropemporium is in this repo.

### Same same, but different
The challenge is simple: call the ret2win() function, the caveat this time is that the third argument (which you know by now is stored in the rdx register on x86_64 Linux) must be 0xdeadcafebabebeef. Populating this elusive register using ROP can prove more difficult than you might first think, especially in smaller binaries with fewer gadgets. This can become particularly irksome since many useful GLIBC functions require three arguments.

### So little room for activities
Start by using ropper to search for sensible gadgets, if there's no pop rdx perhaps there's a mov rdx, rbp that you could chain with a pop rbp. You might consider avoiding the issue entirely by returning to the fgets() code within the pwnme() function but this may prove to be difficult since the .got.plt entries of fgets() and some other functions have been tampered. If you're all out of ideas go ahead and read the last section.

### Universal
Fortunately some very smart people have come up with a solution to your problem and as is customary in infosec given it a collection of pretentious names, including "Universal ROP", "μROP", "return-to-csu" or just "ret2csu". You can learn all you need to on the subject from these [BlackHat Asia slides](https://web.archive.org/web/20190425162924/https://www.blackhat.com/docs/asia-18/asia-18-Marco-return-to-csu-a-new-method-to-bypass-the-64-bit-Linux-ASLR.pdf). Note that more recent versions of gcc may use different registers from the example in __libc_csu_init(), including the version that compiled this challenge.


© ROP Emporium 2019


You can also look at the [BlackHat Asia Paper](https://i.blackhat.com/briefings/asia/2018/asia-18-Marco-return-to-csu-a-new-method-to-bypass-the-64-bit-Linux-ASLR-wp.pdf) instead of the slides from the Universal section above.


Run through the typical security checks and find the length of the buffer overflow. None of this has changed for any of the challenges yet so I don't feel the need to go through that.

Going through the problem text from above all we need to do is populate the rdx register with a certain value and then call ret2win, which seems pretty simple. Sadly there is not a single viable gadget that can populate rdx with the value we want using typical rop gadget finders. In my case I used Ropper. This is where the BlackHat Asia Slides or Paper come in. Section 4 of the paper is where we will take most of the information from to help us with this challenge so read at least up to that point.

Using the two Gadgets outlined in section 4 of the return to csu paper we can see a way to populate the rdx register. (below is Intel syntax and the paper used AT&T syntax)

#### Gadget 1
```Assembly
  40089a:   5b                      pop    rbx  
  40089b:   5d                      pop    rbp  
  40089c:   41 5c                   pop    r12  
  40089e:   41 5d                   pop    r13  
  4008a0:   41 5e                   pop    r14  
  4008a2:   41 5f                   pop    r15  
  4008a4:   c3                      ret
```

#### Gadget 2
```Assembly
  400880:   4c 89 fa                mov    rdx,r15
  400883:   4c 89 f6                mov    rsi,r14
  400886:   44 89 ef                mov    edi,r13d
  400889:   41 ff 14 dc             call   QWORD PTR [r12+rbx*8]
```

We can use gadget 1 to poulate the r15 register and then use gadget 2 to put the value of r15 into rdx. However at the end of Gadget 2 there is a call instead of a return. Also the call is dereferencing the operand. What this means is that it will call whatever value r12+(rbx\*8) points to. We want to call ret2win. If there was a memory address that points to ret2win somewhere in memory we could set r12+(rbx\*8) to that value and we would have what we want.

Open up the ret2win binary in Ghidra and go to the search tab and search for the hex value of ret2win (0x4007b1). Sadly there is nowhere in memory that works. Instead of calling ret2win we could call a different function.

### Finding a Function to Call
Given that the GOT has the address of functions in its table and that table is in memory that seems like a good place to start. However if you look at the decompilation of pwnme, it knows that this was a good idea and it zero's out the memory at those regions in the function before it gets to return. Eventually I came across the \_init function and saw that its address was also in memory.

#### \_init
```Assembly
  400560:   48 83 ec 08             sub    rsp,0x8
  400564:   48 8b 05 8d 0a 20 00    mov    rax,QWORD PTR [rip+0x200a8d]        # 600ff8 <__gmon_start__>
  40056b:   48 85 c0                test   rax,rax
  40056e:   74 02                   je     400572 <_init+0x12>
  400570:   ff d0                   call   rax  
  400572:   48 83 c4 08             add    rsp,0x8
  400576:   c3                      ret
```
The \_init function puts a value in memory based off the rip and tests if that value is 0, if that value isnt 0 then it will return. So as long as \[rip+0x200a8d\] comes out to any value other than 0 then this function will basically do nothing, which is exactly what we want. If you make a script and run the program using gdb up to this point and look at the address in memory, you will see it is a non-zero value so this will work perfectly.

Okay now that we have the function we are going to call we have to see what happens after the call.

#### Gadget 2 (extended)
```Assembly
  400880:   4c 89 fa                mov    rdx,r15
  400883:   4c 89 f6                mov    rsi,r14
  400886:   44 89 ef                mov    edi,r13d
  400889:   41 ff 14 dc             call   QWORD PTR [r12+rbx*8]
  40088d:   48 83 c3 01             add    rbx,0x1
  400891:   48 39 dd                cmp    rbp,rbx
  400894:   75 ea                   jne    400880 <__libc_csu_init+0x40>
  400896:   48 83 c4 08             add    rsp,0x8
  40089a:   5b                      pop    rbx  
  40089b:   5d                      pop    rbp  
  40089c:   41 5c                   pop    r12  
  40089e:   41 5d                   pop    r13  
  4008a0:   41 5e                   pop    r14  
  4008a2:   41 5f                   pop    r15  
  4008a4:   c3                      ret
```

We can see a few extra instructions between the end of Gadget 2 and the start of Gadget 1.

```Assembly
  40088d:   48 83 c3 01             add    rbx,0x1
  400891:   48 39 dd                cmp    rbp,rbx
  400894:   75 ea                   jne    400880 <__libc_csu_init+0x40>
  400896:   48 83 c4 08             add    rsp,0x8
```
The few extra instructions are instructions used for loops. It will increment rbx, compare that value to rbp and if they are not equal then it jumps back to the start of Gadget 2. We don't want to jump back to the start of Gadget 2, we want to get to a return so that we can call ret2win now that rdx has 0xdeadcafebabebeef. So we need to make sure that before we get to this point that rbp = rbx + 1 and then getting the return will be smooth sailing.

Okay now lets recap on what we need to do:
1. populate rdx with 0xdeadcafebabebeef using Gadget 1 then Gadget 2
2. Call \_init by having r12+(rbx\*8) = 0x600e38 which is an address that points to \_init
3. Ensure rbp = rbx + 1 before using Gadget 2.


