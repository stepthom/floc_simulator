package main

/*
#include <stdlib.h>
*/
import "C"
//import "fmt"
import "golang.org/x/net/publicsuffix"
import "log"
import "github.com/shigeki/floc_simulator/packages/floc"

var kMaxNumberOfBitsInFloc uint8 = 50

// With many thanks to https://medium.com/@wirelesser/python-extension-with-go-3b6760fcf73b

//export get_cohortId
func get_cohortId(_domains []*C.char,) uint64 {
    //fmt.Println(_domains)
    
    domains := make([]string,0)
    for _, _domain := range _domains {
        bs := C.GoString(_domain)  // to go string(copy) 
        
		eTLDPlusOne, err := publicsuffix.EffectiveTLDPlusOne(bs)
		if (err != nil) {
            log.Fatal(err)
		}
		domains = append(domains, eTLDPlusOne)
    }
    //fmt.Println(domains)
    
	sorting_lsh_cluster_data, err := floc.SetUpClusterData()
	if err != nil {
		log.Fatal(err)
	}
    
	check_sensitiveness := true
	sim_hash := floc.SimHashString(domains, kMaxNumberOfBitsInFloc)
	cohortId, err := floc.ApplySortingLsh(sim_hash, sorting_lsh_cluster_data, kMaxNumberOfBitsInFloc, check_sensitiveness)
    if err != nil {
        log.Fatal(err)
    }
    
    //fmt.Println(cohortId)
    
    return cohortId
}

func main() {}