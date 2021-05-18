#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <linux/random.h>

#include "reseed.h"

void reseed(void)
{
    printf("Reseeding /dev/urandom\n");

    size_t len = 1024;
    struct rand_pool_info *info = malloc(sizeof(struct rand_pool_info) + sizeof(unsigned int) * len);
    info->buf_size = len;
    info->entropy_count = len * sizeof(unsigned int) * 8;

    int fd = open("/dev/urandom", O_RDWR);
    if (fd < 0)
    {
        puts("Could not open /dev/urandom");
        return;
    }

    for (int i = 0; i < 4; i ++)
    {
        __u32 num_buf[2];
        int pos = 0;
        while (pos <= len - 2)
        {
            __builtin_ia32_rdrand64_step((unsigned long long*)&num_buf);

            info->buf[pos] = num_buf[1];
            info->buf[pos+1] = num_buf[0];

            pos += 2;
        }

        if (ioctl(fd, RNDADDENTROPY, info) < 0)
        {
            puts("Could not add entropy to /dev/urandom");
            return;
        }
    }
}