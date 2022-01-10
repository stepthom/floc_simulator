package floc

import (
	"encoding/binary"
	"fmt"
	"log"
	"math"
)

type WeightedFeatures map[uint64]int

func randomUniform(i uint64, j uint64, seed uint64) float64 {
	b_i := make([]byte, 8)
	b_j := make([]byte, 8)
	binary.LittleEndian.PutUint64(b_i, i)
	binary.LittleEndian.PutUint64(b_j, j)
	arr := append(b_i, b_j...)
	hashed := CityHash64WithSeedV103(arr, seed)
	return float64(hashed) / float64(math.MaxUint64)
}

func randomGaussian(i uint64, j uint64) float64 {
	var g_seed1 uint64 = 1
	var g_seed2 uint64 = 2
	var kTwoPi float64 = 2.0 * 3.141592653589793
	rv1 := randomUniform(i, j, g_seed1)
	rv2 := randomUniform(j, i, g_seed2)
	if rv1 > 1 || rv1 < 0 || rv2 > 1 || rv2 < 0 {
		log.Fatal("Invaild random rv1, rv2", rv1, rv2)
	}

	return math.Sqrt(float64(-2.0)*math.Log(rv1)) * math.Cos(kTwoPi*rv2)
}

func simHashBits(features WeightedFeatures, output_dimention uint8) uint64 {
	var result uint64 = 0
	var d uint8

	printLots := false

	if printLots {
		fmt.Println("\nIn simHashBits:")
	}
	for d = 0; d < output_dimention; d++ {
		var acc float64 = 0
		var rand float64 = 0

		if printLots {
			fmt.Printf("\ncurrent result: %050b\n", result)
			fmt.Println("\ncalculating bit:", d)
		}
		for hash, weight := range features {
			rand = randomGaussian(uint64(d), hash) * float64(weight)
			acc += rand

			if printLots {
				fmt.Printf("    bit=%d, hash=%22d -> rand = % .3f\n", d, hash, rand)
			}
		}
		if acc > 0 {

			result |= (1 << d)

			if printLots {
				fmt.Printf("  sum of rand = %.3f -> positive, setting bit to 1\n", acc)
			}
		} else {
			if printLots {
				fmt.Printf("  sum of rand = %.3f -> negative, leaving bit as 0\n", acc)
			}
		}
	}

	if printLots {
		fmt.Printf("\nFinal result in binary:  %050b\n", result)
		fmt.Println("Final result in decimal: ", result)
	}
	return result
}

func SimHashString(domain_list []string, kMaxNumberOfBitsInFloc uint8) uint64 {
	features := make(WeightedFeatures, len(domain_list))

	printLots := false

	if printLots {
		fmt.Println("\nIn SimHashString:")
	}
	//fmt.Println("features:", features)
	for _, domain := range domain_list {
		hash := CityHash64V103([]byte(domain))
		features[hash] = 1

		if printLots {
			fmt.Printf("domain = %20s -> hash = %d\n", domain, hash)
		}
	}
	sim_hash := simHashBits(features, kMaxNumberOfBitsInFloc)
	return sim_hash
}
