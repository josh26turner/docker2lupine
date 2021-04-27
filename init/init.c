#include <stdio.h>
#include <stdlib.h>
#include <sys/mount.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <dirent.h>

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

void file_write(char *file_name, char *data)         
{                                           
    FILE *file_ptr = fopen(file_name, "w"); 
    fprintf(file_ptr, data);                
    fclose(file_ptr);                       
}

int main(int argc, char *argv[])
{
    int strace = argc >= 2 && strcmp("strace", argv[1]) == 0;
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

    file_write("/etc/hosts", "127.0.0.1       localhost\n");
    file_write("/etc/resolv.conf", "nameserver 192.168.100.1\n");
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

    file_write("/etc/hostname", NAME "\n");
    chdir(WORKING_DIR);

    char *env[] = {ENV_ARR};
    for (int i = 0; env[i] != NULL; i ++) putenv(env[i]);

    puts("=========APP INIT=========");
    #ifdef NET_SETUP
    int pid = fork();

    if (pid == 0) exec_app(strace);

    //Socket comms
    setup();

    while (get_rsp() != 1) sleep(1);

    kill(pid, SIGKILL);

    if (strace)
    {
        puts("Sending strace logs...");
        chdir("/");
        DIR *dir_ptr = opendir("/");
        struct dirent *ent_ptr;

        while (ent_ptr = readdir(dir_ptr))
            if (strncmp(ent_ptr->d_name, NAME, strlen(NAME)) == 0) sendfile(ent_ptr->d_name);

    }
    done();
    #else
    exec_app(strace);
    #endif
    puts("=========FINISHED=========");
}
