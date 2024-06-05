/*Spike ISS stuff*/
unsigned long long tohost = 0;
unsigned long long fromhost = 0;

#define N 10

void _start(void) {

    /*must set the stack pointer*/
    asm volatile("la sp, _sp");

    main();

}


int A[N] = {63, 37, 45, 23, 12, 67, 89, 12, 34, 56};
int B[N] = {63, 37, 45, 23, 12, 67, 89, 12, 34, 56};
int C[N];


int main(void) {

    for (int i = 0; i < N; i++)
    {
        C[i] = A[i] + B[i];
    }

    tohost = 1;

    return 0;

}