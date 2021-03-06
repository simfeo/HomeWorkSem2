#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <vector>
#include <iomanip>
#include <bitset>


#include "GaloisFieldNumber.h"

#include "BCH_coder.h"

int main(int argc, char** argv)
{

	std::vector<unsigned char> ss = { 'c', 'o', 'd', 'e', 'w','o','r','d'};

	std::cout << "Word to encode" << std::endl;
	for (auto el : ss)
	{
		std::cout << el;
	}
	std::cout << std::endl;

	BCH_Codec bb (4, 2);
	
	auto res = bb.Encode(ss);
	
	res.encodedMessage[0] = res.encodedMessage[0] ^ (1 << 3);
	res.encodedMessage[0] = res.encodedMessage[0] ^ (1 << 4);
	res.encodedMessage[0] = res.encodedMessage[0] ^ (1 << 6); // too much errors

	std::cout << "Decoded word" << std::endl;

	auto decoded = bb.Decode(res);

	for (auto el : decoded)
	{
		std::cout << el;
	}
	std::cout << std::endl;


	return 0;
}
