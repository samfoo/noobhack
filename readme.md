nethack is hard
---------------

I know, right?! **noobhack** does it's best to augment playing nethack. 
It does anything and everything it can to help you along the way to a 
successful ascension.

how does noobhack help me?
--------------------------

noobhack remembers things about the dungeon that might be otherwise tedious for
you to think about. Found a rare bookshop on dlvl 5 but don't have the money to
pay for the books yet or the time to steal them? nooback remembers features
about the dungeon. 

Just heard a sound in the dungeon, but can't be bothered to check a spoilers
website and check what it means? noobhack translates noises and remembers it.

Standing toe-to-toe with an energy vortex and can't remember if you're shock 
resistant or not? noobhack remembers, and it's only a keystroke away.

Taught yourself a spell, but can't remember when it expires? noobhack's got you
covered.

Know you can price-identify an item, but don't want to keep switching windows
to enter values into a calculator? noobhack automatically price identifies 
items for you as you pick them up.

awesome! how do i get started?
------------------------------

Simple: Start noobhack by typing

    % noobhack

at the command line. This will start a seemingly normal game of nethack. You
can play nethack without ever consulting noobhack, but if you want to consult
the helper console simply press `tab`. To dismiss it press `tab` again.

You can also open an (experimental) map mode by typing the backtick key '`' and
dismiss it again by pressing the same. When in map mode, you can scroll the map
vertically with the 'j' and 'k' keys (just like walking in the game!)

but explanations are boring, show me screenshots!
-------------------------------------------------

Goodness gracious. Here's what noobhack looks like at the moment (the lack of
colors and the lack of bold makes it a bit harder to distinguish than it is 
during gameplay):

      -----         ---------
      |<  ---  ------       --    -------                       ---------------
      |     ---|         --  |    |.....|          -------      |.............|
      --  |    | ---------|  |    |.._..|          |>    |     --|---.--.----+|
       -- |-     ----     ----    |.....|  ------  --    |---  |.%|...|-.|.-..|
        --|         |     -----   ---|---  |  - |   ---  |  ---|..|--.-..--|..|
           --- |    |  ----   --    |.|    |  | |    ---|-.    -|--........--||
             -----  |    |     ---- |u|    |  | |--- -......--  ..............|
          ------ |  |             ---.--    --| -  | .......-|  --------|--..--
          |%%!.| --  ) % ---         . -----  | |  | ...{... ----     ....|..--
          |..%.|  |        |   |    .%.    ---| |  | -......        )%%[!?|...|
          ---|--------    -------   ---      -| |------....---     --------...|
       ------ ---.. -|   -|  |  |-   |  ---...| --  | ..|..  | ----- |       --
       |  |- ....%.. |% --|  |  |--     |-....|.       ---   -|.(((| | -------
    +- this level ----------+- status -+- resist -+--    |-   -.(((| | |   |
    |altar (chaotic)        |fast      |  (none)  | |-   |   -|.(((| | |   |
    |shop                   |          |          | |        | ----- |.--|-------
    |  * 83/14/3 food/drink |          |          |-|   |    |--------.....|    |
    |  * 97/3 light/m.lamp  |          |          | --  |   --      |...{..-% -||
    |  * random             |          |          |  -----     ----  ......|  |(|
    |  * tools              |          |          |      -------  ---------------
    Sam the Bachelor         St:16 Dx:9 Co:14 In:8 Wi:16 Ch:18  Lawful
    Dlvl:7  $:666 HP:46(46) Pw:54(54) AC:2  Xp:7/789 T:2522

And the map:

   +-- Legend: -------+                                           *
   | Press ` to exit  |                                     +- main:1 -+
   | j, k to scroll   |                                     |     ?    |
   |                  |                                     +----------+
   | a[cnl]     Altar |                                           |
   | b       Barracks |                                     +- main:2 -+
   | h        Beehive |                                     |     ?    |
   | o         Oracle |                                     +----------+
   | r          Rogue |                                           |
   | s           Shop |                                     +- main:3 -+
   | v          Vault |                                     |     v    |
   | w    Angry watch |                                     +----------+
   | z            Zoo |                                           |
   +------------------+                                     +- main:4 -+
                                                            |    al    |
                                                      .-----+----------+
                                                     /            |
                                        +- mines:5 -+       +- main:5 -+
                                        |     ?     |       |     ?    |
                                        +-----------+       +----------+
                                              |
                                        +- mines:6 -+
                                        |     ?     |
                                        +-----------+
                                              |
                                        +- mines:7 -+
                                        |   ac,s    |
                                        +-----------+


does noobhack work on public servers like nethack.alt.org?
----------------------------------------------------------

Yup, you can start a remote game by doing something like:

    % noobhack -h nethack.alt.org

isn't this cheating?
--------------------

Some people might (and I suspect *will*) consider noobhack cheating. However,
before you start chuggin' a gallon of haterade, consider this:

* noobhack doesn't actual know anything other than what it sees on screen.
* I spent more time working on noobhack than most people spend ascending.
* ...
* Screw you, it's not cheating.

