#include <sys/socket.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <arpa/inet.h>
#include <linux/rtnetlink.h>

#include "socket_client.h"

#define SERVER_PORT 8080
#define DEFAULT_SERVER_IP "192.168.100.1"

#define GET "get"
#define DONE "done"
#define STOP "stop"

#define MAX_MSG_LEN 10

int get_gw(struct in_addr *gw)
{
    int ret = 0;
    int buff_size = 1024;
    void *ptr = malloc(buff_size);
    pid_t pid = getpid(); //1

    struct nlmsghdr *nlmsg = (struct nlmsghdr *)malloc(buff_size);
    nlmsg->nlmsg_len = NLMSG_LENGTH(sizeof(struct rtmsg));
    nlmsg->nlmsg_type = RTM_GETROUTE;
    nlmsg->nlmsg_flags = NLM_F_DUMP | NLM_F_REQUEST;
    nlmsg->nlmsg_seq = 1;
    nlmsg->nlmsg_pid = pid;

    int nl_rt_sock = socket(AF_NETLINK, SOCK_DGRAM, NETLINK_ROUTE);
    if (nl_rt_sock < 0)
    {
        ret = EXIT_FAILURE;
        goto RET_SOCK;
    }

    if (send(nl_rt_sock, nlmsg, nlmsg->nlmsg_len, 0) < 0)
    {
        ret = EXIT_FAILURE;
        goto RET;
    }

    int recv_len;
    struct nlmsghdr *nlh;
    do
    {
        int msg_len;

        recv_len = recv(nl_rt_sock, ptr + msg_len, buff_size - msg_len, 0);
        if (recv_len < 0)
        {
            ret = EXIT_FAILURE;
            goto RET;
        }

        nlh = (struct nlmsghdr *) ptr + msg_len;

        if((NLMSG_OK(nlmsg, recv_len) == 0) || (nlmsg->nlmsg_type == NLMSG_ERROR))
        {
            ret = EXIT_FAILURE;
            goto RET;
        }

        if (nlh->nlmsg_type == NLMSG_DONE)
            break;
        else
            msg_len += recv_len;
    }
    while ((nlmsg->nlmsg_seq != 1) || (nlmsg->nlmsg_pid != pid));

    for (;NLMSG_OK(nlh, recv_len); nlh = NLMSG_NEXT(nlh, recv_len))
    {
        struct rtmsg *rt_entry = (struct rtmsg *) NLMSG_DATA(nlh);

        if (rt_entry->rtm_table != RT_TABLE_MAIN)
            continue;

        struct rtattr *rt_attr = (struct rtattr *) RTM_RTA(rt_entry);
        int rt_attr_len = RTM_PAYLOAD(nlh);

        for (;RTA_OK(rt_attr, rt_attr_len); rt_attr = RTA_NEXT(rt_attr, rt_attr_len))
        {
            if (rt_attr->rta_type == RTA_GATEWAY)
            {
                *gw = *(struct in_addr *) RTA_DATA(rt_attr);
                goto RET;
            }
        }
    }

RET:
    close(nl_rt_sock);
RET_SOCK:
    free(ptr);
    free(nlmsg);

    return ret;
}

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

    if (get_gw(&server.sin_addr))
        inet_pton(AF_INET, DEFAULT_SERVER_IP, &server.sin_addr);

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
