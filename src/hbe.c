#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// ==========================================
// CONFIGURATION
// ==========================================
#define N 40            // Number of dimensions (Lorenz 96 standard)
#define F 8.0           // Forcing term (Chaos threshold)
#define DT 0.01         // Time step
#define STEPS 1000      // Simulation steps

// ==========================================
// LORENZ 96 DYNAMICS
// ==========================================
void lorenz96_step(double *x, double *dxdt) {
    for (int i = 0; i < N; i++) {
        // Indices with periodic boundary conditions
        int ip1 = (i + 1) % N;
        int im1 = (i - 1 + N) % N;
        int im2 = (i - 2 + N) % N;

        // dx[i]/dt = (x[i+1] - x[i-2]) * x[i-1] - x[i] + F
        dxdt[i] = (x[ip1] - x[im2]) * x[im1] - x[i] + F;
    }
}

// ==========================================
// MAIN SIMULATION
// ==========================================
int main() {
    double x[N];
    double dxdt[N];
    double x_next[N];

    // 1. Initialize State (Perturbed Equilibrium)
    for (int i = 0; i < N; i++) {
        x[i] = F;
    }
    x[0] += 0.01; // Tiny perturbation to trigger chaos

    // Print Header
    printf("step");
    for (int i = 0; i < N; i++) {
        printf(",x%d", i);
    }
    printf("\n");

    // 2. Time Integration (Euler Method for simplicity)
    for (int t = 0; t < STEPS; t++) {
        // Calculate derivatives
        lorenz96_step(x, dxdt);

        // Update state
        for (int i = 0; i < N; i++) {
            x[i] += dxdt[i] * DT;
        }

        // Output CSV
        printf("%d", t);
        for (int i = 0; i < N; i++) {
            printf(",%.4f", x[i]);
        }
        printf("\n");
    }

    fprintf(stderr, "✅ Simulation Complete: %d steps, %d dimensions.\n", STEPS, N);
    return 0;
}
