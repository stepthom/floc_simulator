package main

import (
	"fmt"
	//"log"
	//"strconv"
	"math/rand"

	"github.com/shigeki/floc_simulator/packages/floc"
)

//
// simulation1 calculate diff of cohortId when only one domain difference in two histories of n domains.
// user1_history = {"example0.com", "example1.com", "example2.com", "example3.com", "example4.com"}
// user2_history = {"example0.com", "example1.com", "example2.com", "example3.com", "example5.com"}
//
// diff =  cohortId_user1 - cohortId_user2
//
var kMaxNumberOfBitsInFloc uint8 = 50

func getCohortId(domain_list []string, sorting_lsh_cluster_data []byte) (uint64, error) {
	check_sensitiveness := false
	sim_hash := floc.SimHashString(domain_list, kMaxNumberOfBitsInFloc)
	cohortId, err := floc.ApplySortingLsh(sim_hash, sorting_lsh_cluster_data, kMaxNumberOfBitsInFloc, check_sensitiveness)
	return cohortId, err
}

type Domain struct {
	id     int
	domain string
}

type Category struct {
	id      int
	domains []int
}

type Persona struct {
	id                   int
	preferred_categories []int
}

type User struct {
	id              int
	persona         int
	visited_domains []int
}

func main() {

	n_domains := 20
	max_domains_per_category := 9
	n_categories := 4
	max_categories_per_persona := 3
	n_personas := 5
	n_users := 10
	//max_visits_per_user := 10

	domains := make(map[int]Domain)
	categories := make(map[int]Category)
	personas := make(map[int]Persona)
	users := make(map[int]User)

	// Randomly create domains
	for n := 0; n < n_domains; n++ {

		_domain := Domain{
			id:     n,
			domain: fmt.Sprintf("domain_%05d.com", n),
		}

		domains[n] = _domain
	}

	// Randomly create categories, and assign domains to categories
	for n := 0; n < n_categories; n++ {

		// Number of domains assigned category
		_n_domains_in_category := rand.Intn(max_domains_per_category) + 1

		var _domains []int
		for j := 1; j < _n_domains_in_category; j++ {
			_domains = append(_domains, rand.Intn(len(domains)))
		}

		_category := Category{
			id:      n,
			domains: _domains,
		}
		categories[n] = _category

	}

	// Randomly create persona, i.e., subset of categories
	for n := 0; n < n_personas; n++ {

		// Number of domains assigned category
		_n_categories_in_persona := rand.Intn(max_categories_per_persona) + 1

		var _preferred_categories []int
		for j := 0; j < _n_categories_in_persona; j++ {
			_preferred_categories = append(_preferred_categories, rand.Intn(len(categories)))
		}

		_persona := Persona{
			id:                   n,
			preferred_categories: _preferred_categories,
		}
		personas[n] = _persona
	}

	// Randomly create users, i.e., a persona and set of visited domains
	for n := 0; n < n_users; n++ {
		_persona = rand.Intn(len(personas))

		// TODO: randomly select some domains based on persona

		_user := User{
			id:      n,
			persona: _persona,
		}
		users[n] = _user
	}

	fmt.Println("Domains:")
	for _, value := range domains {
		fmt.Printf("%v\n", value)
	}

	fmt.Println("Categories:")
	for _, value := range categories {
		fmt.Printf("%v\n", value)
	}

	fmt.Println("Personas:")
	for _, value := range personas {
		fmt.Printf("%v\n", value)
	}

	fmt.Println("Users:")
	for _, value := range users {
		fmt.Printf("%v\n", value)
	}

	// Calculate cohort ID of each user

	/*max := 12

	for n := 11; n < max; n++ {
		var domainlist1 []string
		var domainlist2 []string

		for i := 0; i < n-2; i++ {
			j := strconv.Itoa(i)
			domainlist1 = append(domainlist1, "example"+j+".com")
			domainlist2 = append(domainlist2, "example"+j+".com")
		}
		domainlist1 = append(domainlist1, "example"+strconv.Itoa(n-1)+".com")
		domainlist2 = append(domainlist2, "example"+strconv.Itoa(n)+".com")

		sorting_lsh_cluster_data, err := floc.SetUpClusterData()
		if err != nil {
			log.Fatal(err)
		}

		fmt.Println("Getting Cohort ID for domain list 1:", domainlist1)

		cohortId1, err := getCohortId(domainlist1, sorting_lsh_cluster_data)
		if err != nil {
			log.Fatal(err)
		}

		fmt.Println("Getting Cohort ID for domain list 2:", domainlist2)
		cohortId2, err := getCohortId(domainlist2, sorting_lsh_cluster_data)
		if err != nil {
			log.Fatal(err)
		}
		diff := (int64)(cohortId1 - cohortId2)
		fmt.Println(n+1, ",", cohortId1, ",", cohortId2, ",", diff)
	}*/
}
