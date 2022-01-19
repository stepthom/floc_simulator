package main

import (
	"fmt"
	"log"
    "bufio"

	//"strconv"
	//"math/rand"

	"strings"

	"os"

	"github.com/shigeki/floc_simulator/packages/floc"
)

var kMaxNumberOfBitsInFloc uint8 = 50

func getCohortId(domain_list []string, sorting_lsh_cluster_data []byte) (uint64, error) {
	check_sensitiveness := false
	sim_hash := floc.SimHashString(domain_list, kMaxNumberOfBitsInFloc)
	cohortId, err := floc.ApplySortingLsh(sim_hash, sorting_lsh_cluster_data, kMaxNumberOfBitsInFloc, check_sensitiveness)
	return cohortId, err
}

func main() {
    
    
	sorting_lsh_cluster_data, err := floc.SetUpClusterData()
	if err != nil {
		log.Fatal(err)
	}
    
    var cohortIDs []uint64
    in_fn := os.Args[1]
    out_fn := os.Args[2]
    
    // Read in the visited domains.
    // Assume each line contains a list of strings, comma seperated, per customer
    
    file, err := os.Open(in_fn)
    if err != nil {
        log.Fatal(err)
    }
    defer file.Close()

    scanner := bufio.NewScanner(file)
    // optionally, resize scanner's capacity for lines over 64K, see next example
    for scanner.Scan() {
        _visited_domains := strings.Split(scanner.Text(), " ")
        //fmt.Println(len(_visited_domains))
        _cohortId, err := getCohortId(_visited_domains, sorting_lsh_cluster_data)
        if err != nil {
            log.Fatal(err)
        }
        cohortIDs = append(cohortIDs, _cohortId)
    }

    if err := scanner.Err(); err != nil {
        log.Fatal(err)
    }


	//file, err := os.Create(out_fn)
	//checkError("Cannot create file", err)
	//defer file.Close()
    
    f, err := os.Create(out_fn)
    if err != nil {
        log.Fatal(err)
    }
    defer f.Close()
    fmt.Fprintln(f, "cohort_id")
    for _, value := range cohortIDs {
       fmt.Fprintln(f, value)  // print values to f, one per line
    }
    
    //fmt.Println(cohortIDs)

}

func checkError(message string, err error) {
	if err != nil {
		log.Fatal(message, err)
	}
}
