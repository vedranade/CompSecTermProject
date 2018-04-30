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
                soc.sendall(choice.encode("utf8"))      #Send the choice to server
                data_received = soc.recv(5120).decode("utf8")
                print("Server says: {}".format(data_received))



    #Quit
    soc.close()

if __name__ == "__main__":
    main()