/*Spike ISS stuff*/
unsigned long long tohost = 0;
unsigned long long fromhost = 0;

#define N 10

void _start(void) {

    int data[N] = {0,1,2,3,4,5,6,7,8,9};

    int sum = 0;

    for (int i = 0; i < 10; i++)
    {
        sum += data[i];
    }

    tohost = 1;

    return;
    

}