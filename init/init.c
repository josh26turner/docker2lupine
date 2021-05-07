#include <stdio.h>
#include <stdlib.h>
#include <sys/mount.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <dirent.h>
#include <sys/reboot.h>

#include "socket_client.h"
#include "reseed.h"
#include "env.h"

#define STRACE_FILE(name) "/" name

#define STRACE_ARGS "strace","-ff","-o"

#define exec_app(strace)                                    \
{                                                           \
    if (strace)                                             \
    {                                                       \
        puts("Tracing application...");                     \
        char *cmd[] = {STRACE_ARGS, STRACE_FILE(NAME), CMD};\
        execvp(cmd[0], cmd);                                \
    }                                                       \
    else                                                    \
    {                                                       \
        char *cmd[] = {CMD};                                \
        execvp(cmd[0], cmd);                                \
    }                                                       \
}

int main(int argc, char *argv[])
{
    int strace = argc >= 2 && strcmp("strace", argv[1]) == 0;

    #ifdef LOOPBACK_DEV
    puts("Loopback setup");
    system("/busybox-x86_64 ip addr add 127.0.0.1/24 dev lo");
    system("/busybox-x86_64 ip link set lo up");
    #endif

    #ifdef ENTROPY_GEN
    puts("Generating entropy");
    reseed();
    reseed();
    reseed();
    reseed();
    #endif

    #ifdef PROC_FS
    puts("Mounting procfs");
    mount("proc", "/proc", "proc", 0, NULL);
    #endif

    #ifdef TMP_FS
    puts("Mounting tmpfs");
    mount("tmp", "/tmp", "tmpfs", 0, NULL);
    #endif

    #ifdef SYS_FS
    puts("Mounting sysfs");
    mount("sys", "/sys", "sysfs", 0, NULL);
    #endif

    chdir(WORKING_DIR);

    char *env[] = {ENV_ARR};
    for (int i = 0; env[i] != NULL; i ++) putenv(env[i]);

    puts("=========APP INIT=========");
    if (fork() == 0) exec_app(strace);

    //Socket comms
    int sockfd = setup();

    if (sockfd == -1) goto INIT_REBOOT;

    while (get_rsp(sockfd) != 1) sleep(1);

    close(sockfd);
INIT_REBOOT:
    puts("=========FINISHED=========");
    sync();
    reboot(RB_AUTOBOOT);
}
