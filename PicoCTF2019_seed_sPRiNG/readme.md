testing Readme




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
    if (0x1e < level) {
      puts("Congratulation! You\'ve won! Here is your flag:\n");
      get_flag();
      fflush(stdout);
      return 0;
    }   
    printf("LEVEL (%d/30)\n",level);
    puts("");
    height = rand();
    height = heightt & 0xf;
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
I took out the Seed Spring greeting ASCII art and one of the locals that was never used.
