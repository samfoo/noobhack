#include <stdlib.h>
#include <stdio.h>
#include <dlfcn.h>

static long (*real_random)(void) = NULL;

static void __random_init(void)
{
    real_random = dlsym(RTLD_NEXT, "random");

    if (NULL == real_random) 
    {
        fprintf(stderr, "Error in `dlsym`: %s\n", dlerror());
        exit(0);
    }

    srandom(1);
}

long random(void)
{
    if (NULL == real_random)
    {
        __random_init();
    }

    return real_random();
}
