import socket
import sys

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 8888

    try:
        soc.connect((host, port))
    except:
        print("Connection error")
        sys.exit()

    #If connection successful:
    #Accept name and send to server:
    vname = input("Enter name: ")
    soc.sendall(vname.encode("utf8"))

    #Accept reg num and send to server:
    vregnum = input("Enter registration number: ")
    soc.sendall(vregnum.encode("utf8"))

    #Receive data from server
    data_received = soc.recv(5120).decode("utf8")
    print(data_received)

    #Quit
    soc.close()

if __name__ == "__main__":
    main()