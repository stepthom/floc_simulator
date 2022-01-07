package main

import (
	"fmt"
	"log"

	//"strconv"
	"math/rand"

	"github.com/shigeki/floc_simulator/packages/floc"
)

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
	preferred_domains    []int
}

type User struct {
	id              int
	persona         int
	visited_domains []string
	cohortID        uint64
}

func main() {

	sorting_lsh_cluster_data, err := floc.SetUpClusterData()
	if err != nil {
		log.Fatal(err)
	}

	n_domains := 20
	max_domains_per_category := 9
	n_categories := 4
	max_categories_per_persona := 3
	n_personas := 5
	n_users := 100
	max_visits_per_user := 10

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
		var _preferred_domains []int
		for j := 0; j < _n_categories_in_persona; j++ {
			_categoryID := rand.Intn(len(categories))
			_preferred_categories = append(_preferred_categories, _categoryID)
			_preferred_domains = append(_preferred_domains, categories[_categoryID].domains...)
		}

		//for k, v := range preferred_categories {

		_persona := Persona{
			id:                   n,
			preferred_categories: _preferred_categories,
			preferred_domains:    _preferred_domains,
		}
		personas[n] = _persona
	}

	// Randomly create users, i.e., a persona and set of visited domains
	for n := 0; n < n_users; n++ {
		_persona := rand.Intn(len(personas))

		// TODO: randomly select some domains based on persona_
		_num_visted_domains := rand.Intn(max_visits_per_user) + 1

		var _visited_domains []string
		for j := 0; j < _num_visted_domains; j++ {
			var _domainID int

			if rand.Float32() > 0.2 {
				// Pick from persona category

				_id := rand.Intn(len(personas[_persona].preferred_domains))
				_domainID = personas[_persona].preferred_domains[_id]

			} else {
				// Or truly random
				_domainID = rand.Intn(len(domains))
			}

			_visited_domains = append(_visited_domains, domains[_domainID].domain)
		}

		_cohortId, err := getCohortId(_visited_domains, sorting_lsh_cluster_data)
		if err != nil {
			log.Fatal(err)
		}

		_user := User{
			id:              n,
			persona:         _persona,
			visited_domains: _visited_domains,
			cohortID:        _cohortId,
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

}
