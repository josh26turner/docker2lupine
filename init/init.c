#include <stdio.h>
#include <stdlib.h>
#include <sys/mount.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>

#include "socket_client.h"
#include "reseed.h"
#include "env.h"

#define STRACE_ARGS "strace","-ff","-o"

void load_env(char **env)
{
    for (int i = 0; env[i] != NULL; i ++) putenv(env[i]);
}

int main(int argc, char *argv[])
{
    #ifdef PROC_FS
    puts("Mounting procfs");
    mount("proc", "/proc", "proc", 0, NULL);
    #endif

    #ifdef NET_SETUP
    puts("Network setup");
    system("/busybox-x86_64 ip addr add 192.168.100.2/24 dev eth0");
    system("/busybox-x86_64 ip addr add 127.0.0.1/24 dev lo");
    system("/busybox-x86_64 ip link set eth0 up");
    system("/busybox-x86_64 ip link set lo up");
    system("/busybox-x86_64 ip route add default via 192.168.100.1 dev eth0");
    #endif

    #ifdef ENTROPY_GEN
    puts("Generating entropy");
    reseed();
    reseed();
    reseed();
    reseed();
    #endif

    #ifdef TMP_FS
    puts("Mounting tmpfs");
    mount("tmp", "/tmp", "tmpfs", 0, NULL);
    #endif

    chdir(WORKING_DIR);

    char *env[] = {ENV_ARR};
    load_env(env);

    puts("=========APP INIT=========");

    #ifdef NET_SETUP
    int pid = fork();

    if (pid == 0)
    {    
        if (argc >= 2 && strcmp("strace", argv[1]) == 0)
        {
            char *cmd[] = {STRACE_ARGS, NAME, CMD};
            execvp(cmd[0], cmd);
        }
        else
        {
            char *cmd[] = {CMD};
            execvp(cmd[0], cmd);
        }
    }

    //Socket comms
    setup();

    while (get_rsp() != 1) sleep(3);

    kill(pid, SIGKILL);

    done();
    #else
    if (argc >= 2 && strcmp("strace", argv[1]) == 0)
    {
        char *cmd[] = {STRACE_ARGS, NAME, CMD};
        execvp(cmd[0], cmd);
    }
    else
    {
        char *cmd[] = {CMD};
        execvp(cmd[0], cmd);
    }
    #endif

    puts("=========FINISHED=========");
}