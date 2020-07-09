# Seed_sPRiNG
When you connect to the server using the command provided in the problem you will see that it runs a program that is a guessing game. The game tells us that we are on level 1 out of 30 and to guess the height. When you enter your input, you will probably guess incorrectly and it will close the connection.

The source is not given but the binary for the program the server runs is given so go ahead and open that up in ghidra and go to main in the decompiler. You should get something similar to the code below from Ghidra. Start going through renaming variables and commenting as you like to get an understanding of what this program is doing.


```C
undefined4 main(void)
{
  uint local_20;
  uint local_1c;
  uint local_18;
  int local_14;
  undefined *local_10;
  
  local_10 = &stack0x00000004;
  puts("");
  puts("");
  puts("                                                                             "); 
  puts("                          #                mmmmm  mmmmm    \"    mm   m   mmm "); 
  puts("  mmm    mmm    mmm    mmm#          mmm   #   \"# #   \"# mmm    #\"m  # m\"   \"");
  puts(" #   \"  #\"  #  #\"  #  #\" \"#         #   \"  #mmm#\" #mmmm\"   #    # #m # #   mm");
  puts(
      "  \"\"\"m  #\"\"\"\"  #\"\"\"\"  #   #          \"\"\"m  #      #   \"m   #    #  # # #    #"  
      );  
  puts(" \"mmm\"  \"#mm\"  \"#mm\"  \"#m##         \"mmm\"  #      #    \" mm#mm  #   ##  \"mmm\"");
  puts("                                                                             "); 
  puts("");
  puts("");
  puts("Welcome! The game is easy: you jump on a sPRiNG.");
  puts("How high will you fly?");
  puts("");
  fflush(stdout);
  local_18 = time((time_t *)0x0);
  srand(local_18);
  local_14 = 1;
  while( true ) { 
    if (0x1e < local_14) {
      puts("Congratulation! You\'ve won! Here is your flag:\n");
      get_flag();
      fflush(stdout);
      return 0;
    }   
    printf("LEVEL (%d/30)\n",local_14);
    puts("");
    local_1c = rand();
    local_1c = local_1c & 0xf;
    printf("Guess the height: "); 
    fflush(stdout);
    __isoc99_scanf(&DAT_00010c9a,&local_20);
    fflush(stdin);
    if (local_1c != local_20) break;
    local_14 = local_14 + 1;
  }
  puts("WRONG! Sorry, better luck next time!");
  fflush(stdout);
                    /* WARNING: Subroutine does not return */
  exit(-1);
}
```
Below is what I ended up with after cleaning up the code. I edited the function signature of main, renamed all locals to logical names, took out anything that didn't contribute to the program (local_10 in above) and also removed all the puts function calls that made the ascii art because it was just in the way.

```C
int main(int argc,char **argv)
{
  uint userGuess;
  uint height;
  uint seedValue;
  int level;

  puts("Welcome! The game is easy: you jump on a sPRiNG.");
  puts("How high will you fly?");
  puts("");
  fflush(stdout);
  seedValue = time((time_t *)0x0);
  srand(seedValue);
  level = 1;
  while( true ) { 
    if (30 < level) {
      puts("Congratulation! You\'ve won! Here is your flag:\n");
      get_flag();
      fflush(stdout);
      return 0;
    }   
    printf("LEVEL (%d/30)\n",level);
    puts("");
    height = rand();
    height = height & 0xf;
    printf("Guess the height: "); 
    fflush(stdout);
    __isoc99_scanf(&DAT_00010c9a,&userGuess);
    fflush(stdin);
    if (height != userGuess) break;
    level = level + 1;
  }
  puts("WRONG! Sorry, better luck next time!");
  fflush(stdout);
  exit(-1);
}
```
Now that this program is more readable we can start to see what is going on. 
1. It makes a call to time() with an argument of zero which will return the current time in seconds.
2. It then takes the current time and calls it with srand() which will seed the random number generator... more on that later.
3. Next the program runs a loop
   1. The loop checks if level is 30 or above in which case it will print the flag and you win.
   2. Next it calls rand() which returns a random number based on the seed that was established from time that we saw before the loop.
   3. It then takes the random number and only keeps the last 4 bits `height = height &0xf` this means that the height will always be between 0-15
   4. The last thing the loop does is check the height against the user input and if they are the same you move on to the next level.

In summary all we have to do is input 30 correct guesses of the height which we know will be between 0-15 in a row to get the flag.

Guessing 0-15 30 times in a row is astronomically bad odds, even with automation it simply would not be possible so we will have to exploit the program in a different way.

This is where knowledge of how stdlib's rand and srand functions work is necessary. The rand() function does not actually return a truly random number and randomness in computing is actually a very difficult problem. The way stblib implements rand is by using a Psuedo Random Number Generator. This is basically a really long list of hand picked "random" numbers. When you use srand() it seeds the Random Number Generator by picking an index in that list and then every future call to rand will just iterate through that list.

So if we can call srand() with the same argument that the program calls it with and then call rand() 30 times we will get the same "random" numbers the program does then we can & 0xf those numbers to get the heights. srand() is called with the current server time in seconds. Luckily we already have access to the server through the picoCTF shell so we don't really need to worry about syncronizing, we can just run a program that calls srand() with current time and prints out 30 rand() numbers then run the program and as long as both run within the same second they will be the same "random" numbers.

Make a folder in the /tmp folder on the picoCTF server and make a program like below either using vim on the server or write it on your own and scp it over.

```C
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

int main(){
	srand(time(0));
	for(int i = 0; i < 30; i ++){
		printf(“%d\n”, rand() & 0xf);
	}
	return 0;
}
```
Compile and now you can just run the syncronizer program and pipe it to the connection and get your flag
`./syncronizer | nc 2019shell1.picoctf.com 47241`

picoCTF{pseudo_random_number_generator_not_so_random_1e980471db65a9f446af481d75490127}
