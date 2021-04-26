#include <sys/socket.h>
#include <netinet/ip.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <arpa/inet.h>

#include <errno.h>

#define SERVER_PORT 8080
#define SERVER_IP "192.168.100.1"

#define GET "get"
#define FINISH "finish"

#define STOP "stop"

#define MAX_MSG_LEN 10

int sockfd;

void setup(void)
{
    struct sockaddr_in server;
    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    if (sockfd < 0)
    {
        puts("Error opening socket");
        exit(1);
    }

    server.sin_family = AF_INET;
    server.sin_port = htons(SERVER_PORT);

    inet_pton(AF_INET, SERVER_IP, &server.sin_addr);

    puts("Connecting to server...");
    while (connect(sockfd, (struct sockaddr *)&server, sizeof(server)) < 0);
    puts("Connected to server");
}

int get_rsp(void)
{
    char rd_buffer[MAX_MSG_LEN];
    ssize_t len;

    send(sockfd, GET, strlen(GET), 0);

    len = read(sockfd, rd_buffer, MAX_MSG_LEN);

    return strncmp(rd_buffer, STOP, strlen(STOP)) == 0;
}

void done(void)
{
    send(sockfd, FINISH, strlen(FINISH), 0);
}