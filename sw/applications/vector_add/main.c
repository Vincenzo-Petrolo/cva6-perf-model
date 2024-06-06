/*Spike ISS stuff*/
volatile unsigned long long tohost = 0;
volatile unsigned long long fromhost = 0;

#define N 10

void __attribute__((optimize("O0"))) _start(void) {

    /*must set the stack pointer*/
    asm volatile("la sp, _sp");

    main();

    asm volatile ("sw %0, 0(%1)" : : "r" (1), "r" (&tohost));

}


int A[N] = {63, 37, 45, 23, 12, 67, 89, 12, 34, 56};
int B[N] = {63, 37, 45, 23, 12, 67, 89, 12, 34, 56};
int C[N];


int main(void) {

    for (int i = 0; i < N; i++)
    {
        C[i] = A[i] + B[i];
    }

    return 0;

}