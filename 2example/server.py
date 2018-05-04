import socket
import sys
import traceback
import re
from threading import Thread
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

tim_votes = 0
linda_votes = 0

name = []
file_obj = open("list", "r+")
lines = file_obj.readlines()
file_obj.close()
for x in lines:
    name.append(x.split()[0])
no_of_voters = len(name)

public_key_string = open("cli_pub.der","r").read()
public_key = RSA.importKey(public_key_string)

private_key_string = open("serv_priv.der","r").read()
private_key = RSA.importKey(private_key_string)

def main():
    start_server()

def split_data(data):
    m = re.search("\d", data)
    return m.start()


def check_sign(name, signed_data):
    hashval = SHA256.new(name)
    verifier = PKCS1_v1_5.new(public_key)
    verified = verifier.verify(hashval, signed_data)
    return verified
    #print(verified)

def voterNameExists(vname):
    name = []
    file_obj = open("list", "r+")
    lines = file_obj.readlines()
    file_obj.close()
    for x in lines:
        name.append(x.split()[0])
    for x in name:
        if x == vname:
            return 1
    return -1

def voterRegNumExists(vregnum):
    regnum = []
    file_obj = open("list", "r+")
    lines = file_obj.readlines()
    file_obj.close()
    for x in lines:
        regnum.append(x.split()[1])
    for idx, x in enumerate(regnum):
        if x == vregnum:
            return 1
    return -1

def voterHasVoted(vname):
    name = []
    file_obj = open("history", "r+")
    lines = file_obj.readlines()
    for x in lines:
        name.append(x.split()[0])
    for idx, x in enumerate(name):
        if x == vname:
            return True
        else:
            return False

def start_server():
    host = "127.0.0.1"
    port = 9999         # arbitrary non-privileged port

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
    print("Socket created")
    tim_votes = 0
    linda_votes = 0

    

    try:
        soc.bind((host, port))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    soc.listen(5)       # queue up to 5 requests
    print("Socket now listening")

    # infinite loop- do not reset for every requests
    while True:
        connection, address = soc.accept()
        ip, port = str(address[0]), str(address[1])
        print("Connected with " + ip + ":" + port)

        try:
            Thread(target=client_thread, args=(connection, ip, port)).start()
        except:
            print("Thread did not start.")
            traceback.print_exc()
            
    soc.close()


def client_thread(connection, ip, port, max_buffer_size = 5120):
    data_received = connection.recv(max_buffer_size)
    #print("Data recieved: {}".format(data_received))

    global tim_votes
    global linda_votes
    global no_of_voters
    #Name + RegNum:
    enc_data = data_received[0:128]

    #Digital sign:
    signed_data = data_received[128:]

    dec_cypher = PKCS1_OAEP.new(private_key)
    dec_info = dec_cypher.decrypt(enc_data)
    dec_info_decoded = dec_info.decode()

    #Splitting the message into Name and RegNum:
    vname = dec_info_decoded[0:split_data(dec_info_decoded)]
    vregnum = dec_info_decoded[split_data(dec_info_decoded):]

    vname_encoded = str.encode(vname)

    print("Vname: {}".format(vname))
    print("Vregnum: {}".format(vregnum))

    ret_val_name = voterNameExists(vname)
    ret_val_regnum = voterRegNumExists(vregnum)

    if check_sign(vname_encoded, signed_data):
        if ret_val_name >= 0 and ret_val_regnum >= 0 :
            connection.sendall("1".encode("utf8"))
            is_active = True
            while is_active:
                choice_received = connection.recv(max_buffer_size).decode("utf8").rstrip()
                if choice_received == "1":
                    if voterHasVoted(vname):
                        connection.sendall("0".encode("utf8"))
                    else:
                        connection.sendall("1".encode("utf8"))

                        #Receive candidate no. from client and decrypt it:
                        data_received = connection.recv(max_buffer_size)
                        dec_cypher = PKCS1_OAEP.new(private_key)
                        dec_info = dec_cypher.decrypt(data_received)
                        dec_info_decoded = dec_info.decode()
                        if dec_info_decoded == "1":                    #Tim vote received
                            with open("result") as f:
                                lines = f.readlines()
                            tim_votes += 1
                            lines[0] = "Tim\t%d\n" % tim_votes
                            with open("result", "w") as f:
                                f.writelines(lines)

                        elif dec_info_decoded == "2":                   #Linda vote received
                            with open("result") as f:
                                lines = f.readlines()
                            linda_votes += 1
                            lines[1] = "Linda\t%d" % linda_votes
                            with open("result", "w") as f:
                                f.writelines(lines)

                        file_obj = open("history", "w+")
                        file_obj.write(vname+"\n")
                        file_obj.close()
                        no_of_voters -= 1
                        print("No. of voters: {}".format(no_of_voters))

                        if no_of_voters == 0:
                            if tim_votes > linda_votes:
                                print("Tim wins")
                                print("Tim\t%d" % tim_votes)
                                print("Linda\t%d" % linda_votes)
                            elif tim_votes < linda_votes:
                                print("Linda wins")
                                print("Tim\t%d" % tim_votes)
                                print("Linda\t%d" % linda_votes)

                elif choice_received == "2":
                    connection.sendall("TWO".encode("utf8"))
                elif choice_received == "3":
                    connection.sendall("THREE".encode("utf8"))
                elif choice_received == "4":
                    is_active = False

        else:
            connection.sendall("0".encode("utf8"))
    else:
        connection.sendall("-1".encode("utf8"))

if __name__ == "__main__":
    main()