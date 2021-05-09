#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>

#include "reseed.h"

/* Clear the entropy pool and associated counters.  (Superuser only.) */
#define RNDCLEARPOOL	_IO( 'R', 0x06 )

/* 
 * Write bytes into the entropy pool and add to the entropy count.
 * (Superuser only.)
 */
#define RNDADDENTROPY	_IOW( 'R', 0x03, int [2] )

/* Get the entropy count. */
#define RNDGETENTCNT	_IOR( 'R', 0x00, int )

void exit_perror(const char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}

struct rand_pool_info
{
    int	entropy_count;
	int	buf_size;
	unsigned int buf[0];
};

void reseed(void)
{
    printf("Reseeding /dev/urandom\n");

    size_t len = 1024;
    struct rand_pool_info *info = malloc(sizeof(struct rand_pool_info) + sizeof(unsigned int) * len);
    info->buf_size = len;
    info->entropy_count = len * sizeof(unsigned int) * 8;

    int fd = open("/dev/urandom", O_RDWR);
    if (fd < 0) exit_perror("Unable to open /dev/urandom");

    for (int i = 0; i < 4; i ++)
    {
        // Add the entropy bytes supplied by the hwrng
        unsigned int num_buf[2];
        int pos = 0;
        while (pos <= len - 2)
        {
            __builtin_ia32_rdrand64_step((unsigned long long*)&num_buf);

            info->buf[pos] = num_buf[1];
            info->buf[pos+1] = num_buf[0];

            pos += 2;
        }

        if (ioctl(fd, RNDADDENTROPY, info) < 0) exit_perror("Error issuing RNDADDENTROPY operation");
    }
}