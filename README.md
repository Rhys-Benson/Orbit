# Overview

Orbit is a space adventure where the main objective is the reach a goal point without crashing into one of many planets.
The challenge? Each planet has a harsh gravitational pull that will threaten your fragile ship with imminent destruction without careful maneuvering.
Carefully analyzed and calculated movements along with good judgement a quick thinking will be required if you hope to navigate this treacherous galaxy.
Speed running is advised and celebrated. Have fun!

I made this game because the idea of writing a physics engine based around gravity was exciting to me. I love games and being able to make one myself
is a whole new kind of thrilling. I had a lot of fun writing this and spent more time than I want to admit watching the patterns of my ship as it orbited
planets. The gravity logic is based on the formula for gravity, because it is the most consistent (go figure). 

I have also begun to add multiplayer functionality to the game. My goal is to make the multiplayer a party style competitive combat game mode where 
the players fight each other with lasers and possibly missiles that are also affected by gravitational pull. For the time being I only have two 
independent ships that fly around are affected by gravity, each ship being controlled by a different process of course.

When running the game, you will be asked in the command line for single(S) or multiplayer(M) mode. When M is selected, a choice to be host will be given.
When playing as host, a message in the command will inform you of your own computer's host name for sharing. If you are not playing as host, another
prompt will ask for the name of the host you would like to play with. If the host name is entered correctly on the non-host process, the connection will 
succeed and your game will begin.

[Orbit Demo](https://youtu.be/qlJ2Imtu6Lo)

[Mulyiplayer so far](https://youtu.be/lmvHY2fVk-8)

# Network Communication

The multiplayer mode runs on a peer to peer model. One player will act as a host in order to establish the connection between the two.

I am using TCP with Python sockets. The port number used is 12345

The messages sent between the peers is structured as a dictionary which contains variables of the player's position on the map. The other
peer receives these variables and uses them to draw the opposing player in their own local version of the game.

# Development Environment

I made this game solely using visual studio code. It's a great IDE and I would definitely recommend it to anyone.

Orbit is written in python. The main libraries used are arcade and socket. Other required libraries include math and pickle.

# Useful Websites

* [Arcade tutorial and reference](https://api.arcade.academy/en/latest/)
* [Math library reference](https://docs.python.org/3/library/math.html)

# Future Work

* Even more levels!
* 2 player combat mode featuring missiles that are also affected by gravity
* Possibly turrets that automatically fire at the player, adding more complexity to later levels.
