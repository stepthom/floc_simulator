package main

import (
	"fmt"
	"log"

	//"strconv"
	//"math/rand"
   "golang.org/x/net/publicsuffix"

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
    
    // loop over all arguments by index and value
    var _visited_domains []string
    for i, arg := range os.Args {
        if i == 0 {
            continue
        }
        //fmt.Println("item", i, "is", arg)
        _visited_domain, err := publicsuffix.EffectiveTLDPlusOne(arg)
		if (err != nil) {
            log.Fatal(err)
		}
        _visited_domains = append(_visited_domains, _visited_domain)
    }
    //fmt.Println(_visited_domains)
   
	sorting_lsh_cluster_data, err := floc.SetUpClusterData()
	if err != nil {
		log.Fatal(err)
	}
    
    _cohortId, err := getCohortId(_visited_domains, sorting_lsh_cluster_data)
    if err != nil {
        log.Fatal(err)
    }

    f, err := os.Create("_tmp_cohortID.txt")
    if err != nil {
        log.Fatal(err)
    }
    defer f.Close()
    fmt.Fprintln(f, _cohortId)
    //fmt.Println(cohortIDs)

}

func checkError(message string, err error) {
	if err != nil {
		log.Fatal(message, err)
	}
}
