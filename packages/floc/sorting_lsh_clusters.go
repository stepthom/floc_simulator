package floc

import (
	"errors"
	"fmt"
)

func ApplySortingLsh(sim_hash uint64, cluster_data []byte, kMaxNumberOfBitsInFloc uint8, check_sensiveness bool) (uint64, error) {
	var kExpectedFinalCumulativeSum uint64 = (1 << kMaxNumberOfBitsInFloc)
	var kSortingLshMaxBits uint8 = 7
	var kSortingLshBlockedMask uint8 = 0b1000000
	var kSortingLshSizeMask uint8 = 0b0111111
	var cumulative_sum uint64 = 0
	var index uint64

	fmt.Println("\nIn ApplySortingLsh:")

	fmt.Printf("\nGoing until cumulative_sum is bigger than sim_hash = %050b\n", sim_hash)

	for index = 0; index < uint64(len(cluster_data)); index++ {
		// TODO implement google::protobuf::io::CodedInputStream::ReadVarint32
		next_combined := uint8(cluster_data[index])

		if (next_combined >> kSortingLshMaxBits) > 0 {
			return 0, errors.New("need implement CodedInputStream::ReadVarint32")
		}

		is_blocked := next_combined & kSortingLshBlockedMask
		next := next_combined & kSortingLshSizeMask

		if next > kMaxNumberOfBitsInFloc {
			return 0, errors.New("invalid cluster data")
		}

		cumulative_sum += (1 << next)

		if index%100 == 0 {
			fmt.Println("")
			fmt.Printf("index = %d\n", index)
			fmt.Printf("  (decimal) next_combined = %8d, next = %8d, next shifted = %50d, cumulative_sum = %50d\n", next_combined, next, 1<<next, cumulative_sum)
			fmt.Printf("   (binary) next_combined = %08b, next = %08b, next shifted = %050b, cumulative_sum = %050b\n", next_combined, next, 1<<next, cumulative_sum)
			//fmt.Printf("index = %d, cumulative_sum = %d\n", index, cumulative_sum)
		}

		if cumulative_sum > kExpectedFinalCumulativeSum {
			return 0, errors.New("cumulative_sum overflowed")
		}

		if cumulative_sum > sim_hash {
			if check_sensiveness && (is_blocked != 0) {
				return 0, errors.New("blocked")
			}

			fmt.Printf("\ncumulative_sum = %050b is bigger than sim_hash = %050b --> returning cohort %d\n", cumulative_sum, sim_hash, index)
			return index, nil
		}

	}

	return 0, errors.New("index not found")
}
