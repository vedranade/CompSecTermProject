import socket
import sys
import traceback
import re
from threading import Thread
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA256


public_key_string = open("cli_pub.der","r").read()
public_key = RSA.importKey(public_key_string)

private_key_string = open("serv_priv.der","r").read()
private_key = RSA.importKey(private_key_string)

def main():
    start_server()

def split_data(data):
    m = re.search("\d", data)
    return m.start()

def voterNameExists(vname):
    name = []
    file_obj = open("list", "r+")
    lines = file_obj.readlines()
    for x in lines:
        name.append(x.split()[0])
    for idx, x in enumerate(name):
        if x == vname:
            return idx
        else:
            return -1

def voterRegNumExists(vregnum):
    regnum = []
    file_obj = open("list", "r+")
    lines = file_obj.readlines()
    for x in lines:
        regnum.append(x.split()[1])
    for idx, x in enumerate(regnum):
        if x == vregnum:
            return idx
        else:
            return -1

def start_server():
    host = "127.0.0.1"
    port = 9999         # arbitrary non-privileged port

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
    print("Socket created")

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

    # vname = connection.recv(max_buffer_size).decode("utf8").rstrip()
    # vregnum = connection.recv(max_buffer_size).decode("utf8").rstrip()
    # enc_info = connection.recv(max_buffer_size).decode("utf8").rstrip()
    data_received = connection.recv(max_buffer_size)
    
    print("Data recieved: {}".format(data_received))

    enc_data = data_received[0:128]
    signed_data = data_received[128:]

    print("\n\nEncrypted data: {}".format(enc_data))
    print("\n\nSigned data: {}".format(signed_data))




    dec_cypher = PKCS1_OAEP.new(private_key)
    dec_info = dec_cypher.decrypt(enc_data)
    dec_info_decoded = dec_info.decode()

    print("Decrypted data: {}".format(dec_info_decoded))
    #dec_info_decoded = dec_info.decode()

    vname = dec_info_decoded[0:split_data(dec_info_decoded)]
    vregnum = dec_info_decoded[split_data(dec_info_decoded):]
    print("Vname: {}".format(vname))
    print("Vregnum: {}".format(vregnum))
    #print("Decrypted info: {}".format(dec_info_decoded))

    #print("Encrypted info: {}".format(enc_info))


    ret_val_name = voterNameExists(vname)
    ret_val_regnum = voterRegNumExists(vregnum)

    if ret_val_name >= 0 and ret_val_regnum >= 0:
        connection.sendall("1".encode("utf8"))
        is_active = True
        while is_active:
            choice_received = connection.recv(max_buffer_size).decode("utf8").rstrip()
            if choice_received == "1":
                connection.sendall("ONE".encode("utf8"))
            elif choice_received == "2":
                connection.sendall("TWO".encode("utf8"))
            elif choice_received == "3":
                connection.sendall("THREE".encode("utf8"))
            elif choice_received == "4":
                is_active = False

    else:
        connection.sendall("0".encode("utf8"))

if __name__ == "__main__":
    main()