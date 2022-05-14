# Overview

Project 1 for Columbia University W4111 Introduction to Databases


Estella Ye (UNI: xy2527) Will Wang (UNI: hw2869)




* Project Description

We aim to construct a DBMS with gaming data from Minecraft. This system will mimic the database of a multiplayer Minecraft server, tracking how players change the world with their characters in the game. We will populate our database with artificial data initially. Our design will revolve around characters in Minecraft who interact with and alter the environment. Our Minecraft universe is named “world”, which contains different terrains. To represent this universe, we will use a 2-D matrix, with each element representing the altitude of a small plot of land. Each terrain is a submatrix of the “world matrix”. In our design, each terrain has a uniform altitude, so the elements in that submatrix, which represent altitude, are the same. Characters, also known as players, exist in one and only one world and can alter terrains. Players can increase the altitude of a specific terrain, the magnitude of which depends on their ability, which is an integer attribute of the character (player). In addition to human players, animals and monsters, collectively known as creatures, also exist in the Minecraft world. Players can interact with these creatures using the tools they possess. Furthermore, we will keep track of the achievements of the players and allow players to send messages (weak entities) in the chat. On our website, we will allow users to specify whether they want to query about a player, a terrain, a tool, an achievement, a creature, or a chat message. The user can also specify what information they want displayed. For instance, when querying a player, they have the option to display only the player’s achievements and tools. We will also allow users to create new players and add them to our database. Users will be able to modify the attributes of existing players or manipulate them to change the terrain they are in as well. The main challenge is to realistically capture the intricacies of the core properties of Minecraft with a concise DBMS design.


* Entity-Relationship Diagram


![IMG_C5FAEB874E31-1](https://user-images.githubusercontent.com/72925272/168449964-f56bf521-83b1-4899-bc54-6f9ba81c34e8.jpeg)
