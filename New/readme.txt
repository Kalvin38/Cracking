This project contains two parts, generate a password list and a cracking application. For the password list, we use Crunch to generate a random word list. 
For the cracking application, I established an application by using Python and it will link couple libraries to perform the SSH crack.

Step to use:
1. Use crunch to build the dictionary.
2. Install paramiko and cryptography (pip install paramiko) (pip install cryptography==2.4.2)
3. Run python. (python SSHCracker.py -H <target> -U <username> -T <timeout> -F <password dictionary> -P <port> -X <Max retry time> -M <max threads>) PS: retry time usually set to 4, port is 22, and timeout is 30.
4. Wait for it.

If the IP that block our server, it will shows the time out.
If found, it will show the message: password found!!
If it is not password, the program will print auth failed.
Since the whole program is a multi-process program, each process won’t stop unless all of them check the password. (Make less threads or use ctrl z to terminate if the right password is found)
