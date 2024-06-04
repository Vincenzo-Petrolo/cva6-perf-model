/*Spike ISS stuff*/
unsigned long long tohost = 0;
unsigned long long fromhost = 0;

#define N 10

void _start(void) {

    /*must set the stack pointer*/
    asm volatile("la sp, _sp");

    main();

}

int main(void) {



    int data[N] = {63, 37, 45, 23, 12, 67, 89, 12, 34, 56};

    int sum = 0;

    for (int i = 0; i < N; i++)
    {
        sum += data[i];
    }

    tohost = 1;

    return 0;

}