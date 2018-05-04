import socket
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA256

public_key_string = open("serv_pub.der","r").read()
public_key = RSA.importKey(public_key_string)

private_key_string = open("cli_priv.der","r").read()
private_key = RSA.importKey(private_key_string)


def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 9999

    try:
        soc.connect((host, port))
    except:
        print("Connection error")
        sys.exit()

    #If connection successful:
    #Accept name and send to server:
    vname = input("Enter name: ")

    #Accept reg num and send to server:
    vregnum = input("Enter registration number: ")

    #soc.sendall(vregnum.encode("utf8"))

    #Encrypt the message:
    vinfo = vname + vregnum
    vinfo_encoded = str.encode(vinfo)
    enc_cipher = PKCS1_OAEP.new(public_key)
    enc_info = enc_cipher.encrypt(vinfo_encoded)

    #Sign the message:
    vname_encoded = str.encode(vname)
    hashmsg = SHA256.new(vname_encoded)
    sign_cipher = PKCS1_v1_5.new(private_key)
    signature = sign_cipher.sign(hashmsg)

    data_to_be_sent = enc_info + signature
    soc.sendall(data_to_be_sent)



    #Receive data from server
    bit_received = soc.recv(5120).decode("utf8")
    
    if bit_received == "0":
        print("Invalid name or registration number")
        soc.close()
    elif bit_received == "1":
        while True:
            print("\nWelcome, {}".format(vname))
            print("\tMain Menu")
            print("Please enter a number (1-4)")
            print("1. Vote")
            print("2. My vote history")
            print("3. Election result")
            print("4. Quit")

            choice = input("Enter choice: ")
            if choice == "4":
                soc.close()
                sys.exit()
            else:
                soc.sendall(choice.encode("utf8"))                       #Send the choice to server
                data_received = soc.recv(5120).decode("utf8")
                if choice == "1" and data_received == "0":
                    print("You have already voted")
                elif choice == "1" and data_received == "1":
                    print("Please enter a number (1-2)")
                    print("1. Tim")
                    print("2. Linda")
                    candidate_name = input("Enter choice: ")
                    candidate_name_encoded = str.encode(candidate_name)
                    enc_cipher = PKCS1_OAEP.new(public_key)
                    enc_info = enc_cipher.encrypt(candidate_name_encoded)
                    soc.sendall(enc_info)

    elif bit_received == "-1":
        print("Digital signature not verified by server")
        soc.close()


    #Quit
    soc.close()

if __name__ == "__main__":
    main()