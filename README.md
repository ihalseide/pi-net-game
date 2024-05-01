# Multiplayer networked battleship 

Run a server on one computer and connect with 2 clients to play.

```
        Your Board        |            Hits/Misses     
   1 2 3 4 5 6 7 8 9 10   |       1 2 3 4 5 6 7 8 9 10 
A  0 0 0 0 0 0 0 0 0 0    |    A  0 0 0 0 0 0 0 0 0 0  
B  0 0 0 0 0 0 0 0 0 0    |    B  0 0 0 0 0 0 0 0 0 0  
C  0 0 0 0 0 0 0 0 0 0    |    C  0 0 0 0 0 0 0 0 0 0  
D  0 0 0 0 0 0 0 0 0 0    |    D  0 0 0 0 0 0 0 0 0 0  
E  0 0 0 0 0 0 0 0 0 0    |    E  0 0 0 0 0 0 0 0 0 0  
F  0 0 0 0 0 0 0 0 0 0    |    F  0 0 0 0 0 0 0 0 0 0  
G  0 0 0 0 0 0 0 0 0 0    |    G  0 0 0 0 0 0 0 0 0 0  
H  0 0 0 0 0 0 0 0 0 0    |    H  0 0 0 0 0 0 0 0 0 0  
I  0 0 0 0 0 0 0 0 0 0    |    I  0 0 0 0 0 0 0 0 0 0  
J  0 0 0 0 0 0 0 0 0 0    |    J  0 0 0 0 0 0 0 0 0 0
```

## Running

To run the server:

```bash
python3 server.py
```

The client will prompt for a server address to connect to.
To run the client:

```bash
python3 client.py
```

## Program architecture

Both the server and client script use 'NetMessage.py' as a module for common networking code and use 'Battleship.py' as a module for the common gameplay code.

## Credits
- Ryan Andrews
- Tea Van Ausdall
- Izak Halseide