#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <arpa/inet.h>

#include "socket_client.h"

#define SERVER_PORT 8080
#define SERVER_IP "192.168.100.1"

#define GET "get"
#define DONE "done"
#define STOP "stop"

#define MAX_MSG_LEN 10

int setup(void)
{
    struct sockaddr_in server;
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);

    if (sockfd < 0)
    {
        puts("Error opening socket");
        return -1;
    }

    server.sin_family = AF_INET;
    server.sin_port = htons(SERVER_PORT);

    inet_pton(AF_INET, SERVER_IP, &server.sin_addr);

    while (connect(sockfd, (struct sockaddr *)&server, sizeof(server)) < 0);

    return sockfd;
}

int get_rsp(int sockfd)
{
    char rd_buffer[MAX_MSG_LEN];

    send(sockfd, GET, strlen(GET), 0);

    read(sockfd, rd_buffer, MAX_MSG_LEN);

    int ret = strncmp(rd_buffer, STOP, strlen(STOP)) == 0;

    return ret;
}
