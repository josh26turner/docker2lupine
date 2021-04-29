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
#define FINISH "finish"
#define DONE "done"
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

    while (connect(sockfd, (struct sockaddr *)&server, sizeof(server)) < 0);
}

int get_rsp(void)
{
    char rd_buffer[MAX_MSG_LEN];

    send(sockfd, GET, strlen(GET), 0);

    read(sockfd, rd_buffer, MAX_MSG_LEN);

    int ret = strncmp(rd_buffer, STOP, strlen(STOP)) == 0;

    if (ret) close(sockfd);

    return ret;
}

void done(void)
{
    setup();
    send(sockfd, FINISH, strlen(FINISH), 0);
    close(sockfd);
}

void sendfile(char *filename)
{
    setup();
    send(sockfd, filename, strlen(filename), 0);
    close(sockfd);

    int fd = open(filename, O_RDONLY);
    struct stat buf;
    fstat(fd, &buf);
    char len[8];
    sprintf(len, "%d", buf.st_size);

    setup();
    send(sockfd, len, strlen(len), 0);
    close(sockfd);

    setup();

    void *adr = mmap(NULL, buf.st_size, PROT_READ, MAP_SHARED, fd, 0);
    send(sockfd, adr, buf.st_size, 0);

    char rd_buffer[MAX_MSG_LEN];
    while (strncmp(rd_buffer, DONE, strlen(DONE)) != 0) read(sockfd, rd_buffer, MAX_MSG_LEN);

    close(sockfd);
}