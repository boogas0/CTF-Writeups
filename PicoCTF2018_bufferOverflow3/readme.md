# Buffer Overflow 3
Navigating to the problem directory and running this program we see that is asks us how many bytes we want to write then asks for our input. If we write over 32 bytes we get a Stack Smashing Detected message and if we write under 32 bytes it asks us where the flag is.

Open up source and look at main and we can see two functions that give us an idea of what this program is doing. read_canary() and vuln().

The read_canary() function opens up the file called canary.txt and reads 4 bytes from that file and puts it in a global string called global_canary.

The vuln() function is the meat of this program and it does:
1. Copies the global_canary to the local canary 
2. Asks how many bytes you want to write into the buffer. You can put any number that is less than BUFSIZE (32) digits. So we have a lot of room to work with...
3. Next the function will put into buf what we write for our input up to how many bytes we specified we wanted to write. It has no bounds checking and the buf size is 32. This is susceptable to a buffer overflow.
4. The last thing the function does before returning is compare the local canary value to the global_canary.

Based on the order in which the local variables were declared means that the local canary is between the buf and the saved return address that we want to overwrite to call win(). If we overwrite canary the memcmp() function will notice that the local canary has changed and exit the program so that win() never gets called. This is similar to what a stack canary does on modern systems. The main difference between this program and modern system's implemenation of the stack canary are that the stack canary on modern system is created at run time and not read from a static file. Meaning that the stack canary would be different every time the program is run. Because we know that the stack canary is read from a static file and it is not changing it makes it a lot easier for us to exploit this program.

We could run the program in an automated fashion with pwntools and guess the entire stack canary but the search size for that is 2^32 which isn't terrible but not great either. A faster method would be to guess the stack canary one byte at a time reducing the search space to (2^8) * 4 which is much much smaller.

The solution script details how this is done. 
The script must be run in a tmp folder on the server and symbolic links to the vuln executable, the flag.txt and the canary.txt must be made in order for the script to complete.

symbolic links in your tmp directory can be made by:
```
ln -s /problems/buffer-overflow-3_0_dcd896c1491ad710043225eda6abcd8a/vuln buff3
ln -s /problems/buffer-overflow-3_0_dcd896c1491ad710043225eda6abcd8a/flag.txt flag.txt
ln -s /problems/buffer-overflow-3_0_dcd896c1491ad710043225eda6abcd8a/canary.txt canary.txt
```



picoCTF{eT_tU_bRuT3_F0Rc3_6b01eec0}
