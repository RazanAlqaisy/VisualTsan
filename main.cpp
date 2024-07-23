#include <iostream>
#include <thread>
#include <vector>

#define NUM_THREADS 2

int shared_variable = 0;

void thread_function() {
    for (int i = 0; i < 100; i++) {
        shared_variable++;
    }
}

int main() {
    std::vector<std::thread> threads;

    // Create threads
    for (int i = 0; i < NUM_THREADS; i++) {
        threads.push_back(std::thread(thread_function));
    }

    for (auto& th : threads) {
        th.join();
    }

    std::cout << "Final value of shared_variable: " << shared_variable << std::endl;
    return 0;
}
