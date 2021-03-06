// lab1_generator.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <time.h>
#include <numeric>
#include <random>

#include <chrono>
#include <ctime>    

int main(int argc, char** argv)
{
	// generate 2 <<30 random integers

	const int CH_BUF_LEN = 32*4;
	int totalBuffSize = 1 << 30;
	int tmpBuf[CH_BUF_LEN] = { 0 };

	std::cout << "start gen" << std::endl;
	auto start = std::chrono::system_clock::now();

	std::random_device rd;
	std::mt19937 gen(rd());
	std::uniform_int_distribution<> dis(0, std::numeric_limits<int>::max() / 4);

	std::ofstream outfile("file_a.txt", std::ofstream::binary);

	if (!outfile.is_open())
	{
		return -1;
	}

	for (int i = 0; i < totalBuffSize; i += CH_BUF_LEN)
	{
		for (int j = 0; j < CH_BUF_LEN; ++j)
		{
			tmpBuf[j] = dis(gen);
		}
		size_t tt = sizeof(tmpBuf);
		outfile.write((char*)(&tmpBuf), tt);
	}

	outfile.close();

	auto end = std::chrono::system_clock::now();

	std::chrono::duration<double> elapsed_seconds = end - start;
	std::time_t end_time = std::chrono::system_clock::to_time_t(end);

#pragma warning(suppress : 4996)
	std::cout << "finished at " << std::ctime(&end_time) << "elapsed time: " << elapsed_seconds.count() << "s" << std::endl;
	return 0;
}