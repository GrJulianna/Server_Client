#include <string>
#include <iostream>
#include <ws2tcpip.h>

#pragma comment (lib, "Ws2_32.lib") // links library
using namespace std;

int main() {

	// Initialize winsock

	WSADATA WSAData;

	int startUp = WSAStartup(MAKEWORD(2, 2), &WSAData);
	if (startUp != 0)
	{
		cout << "Cannot initialize winsock." << endl;
		return 1;
	}

	// Create socket 

	SOCKET listening = socket(PF_INET, SOCK_STREAM, 0);
	if (listening == 0)
	{
		cout << "Cannot create socket." <<endl;
		return 1;
	}

	// Bind ip adderess and port to a socket

	sockaddr_in serv;
	serv.sin_family = PF_INET; //specifies family
	serv.sin_addr.S_addr = inet_addr("127.0.0.1");	//specifies IP
	serv.sin_port = htons(27015);	//specifies port

	bind(listening, (sockaddr*)&serv, sizeof(serv));
	if (bind(listening, (sockaddr*)&serv, sizeof(serv)) == SOCKET_ERROR)
	{
		cout << "Binding failed." << endl;
		return;
	}

	//Tell wonsock the socket is for listening

	listen(listening, 1);
	if listen((listening, 1) == SOCKET_ERROR)
	{
		cout << "Error listening for clients" << endl;
		return;
	}

	//accepts client request
	SOCKET AcceptClient;
	printf("Waiting for client to connect...\n");

	while (1)
	{
		AcceptClient = SOCKET_ERROR;
		while (AcceptClient == SOCKET_ERROR) {
			AcceptClient = accept(listening, NULL, NULL);
			cout << "Could not accept request" << endl;
		}
		printf("Request accepted.\n");
		listening = AcceptClient;
		break;
	}

	// connect to server

	if connect(listening, (sockaddr*)&serv, sizeof(serv) == SOCKET_ERROR)
	{
		printf("Could not connect to server.\n");
		WSACleanup();
		return;
	}
	printf("Connected to server.\n");

	//sending and receiving data

	int bytesSent;
	int bytesReceive = SOCKET_ERROR;
	char sentbuf[32] = "Sending data";
	char receivebuf[32] = "";

	bytesSent = send(listening, sentbuf, strlen(sentbuf), 0);
	printf("Bytes sent: %ld\n", bytesSent);

	while (bytesReceive == SOCKET_ERROR)
	{
		bytesReceive = recv(listening, receivebuf, 32, 0);
		if (bytesReceive == 0 || bytesReceive == WSAECONNRESET)
		{
			printf("Connection closed.\n");
			break;
		}
	}

	// Close socket 
	closesocket(clientSocket);
	// Shutdown winock
	WSACleanup();
}