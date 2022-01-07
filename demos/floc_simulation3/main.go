package main

import (
	"fmt"
	"log"

	//"strconv"
	"math/rand"

	"encoding/csv"

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

type Domain struct {
	id     int64
	domain string
}

type Category struct {
	id      int64
	domains []int64
}

type Persona struct {
	id                   int64
	preferred_categories []int64
	preferred_domains    []int64
}

type User struct {
	id              int64
	persona         int64
	visited_domains []string
	cohortID        int64
}

func main() {

	sorting_lsh_cluster_data, err := floc.SetUpClusterData()
	if err != nil {
		log.Fatal(err)
	}

	n_domains := int64(10000)
	max_domains_per_category := int64(9)
	n_categories := int64(100)
	max_categories_per_persona := int64(10)
	n_personas := int64(500)
	n_users := int64(1000000)
	max_visits_per_user := int64(10)

	domains := make(map[int64]Domain)
	categories := make(map[int64]Category)
	personas := make(map[int64]Persona)
	users := make(map[int64]User)

	// Randomly create domains
	for n := int64(0); n < n_domains; n++ {

		_domain := Domain{
			id:     n,
			domain: fmt.Sprintf("domain_%05d.com", n),
		}

		domains[n] = _domain
	}

	// Randomly create categories, and assign domains to categories
	for n := int64(0); n < n_categories; n++ {

		// Number of domains assigned category
		_n_domains_in_category := rand.Int63n(max_domains_per_category) + 1

		var _domains []int64
		for j := int64(0); j < _n_domains_in_category; j++ {
			_domains = append(_domains, rand.Int63n(int64(len(domains))))
		}

		_category := Category{
			id:      n,
			domains: _domains,
		}
		categories[n] = _category

	}

	// Randomly create persona, i.e., subset of categories
	for n := int64(0); n < n_personas; n++ {

		// Number of domains assigned category
		_n_categories_in_persona := rand.Int63n(max_categories_per_persona) + 1

		var _preferred_categories []int64
		var _preferred_domains []int64
		for j := int64(0); j < _n_categories_in_persona; j++ {
			_categoryID := rand.Int63n(int64(len(categories)))
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
	for n := int64(0); n < n_users; n++ {
		_persona := rand.Int63n(int64(len(personas)))

		// Randomly select some domains that this user visits
		_num_visted_domains := rand.Int63n(max_visits_per_user) + 1

		var _visited_domains []string
		for j := int64(0); j < _num_visted_domains; j++ {
			var _domainID int64

			if rand.Float32() > 0.2 {
				// Pick from persona category
				_id := rand.Int63n(int64(len(personas[_persona].preferred_domains)))
				_domainID = personas[_persona].preferred_domains[_id]

			} else {
				// Or truly random
				_domainID = rand.Int63n(int64(len(domains)))
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
			cohortID:        int64(_cohortId),
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

	//fmt.Println("Users:")
	//for _, value := range users {
	//	fmt.Printf("%v\n", value)
	//}

	file, err := os.Create("users.csv")
	checkError("Cannot create file", err)
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, user := range users {
		var out []string
		out = append(out, fmt.Sprintf("%d", user.id))
		out = append(out, fmt.Sprintf("%d", user.persona))
		out = append(out, fmt.Sprintf("%d", user.cohortID))
		err := writer.Write(out)
		checkError("Cannot write to file", err)
	}

}

func checkError(message string, err error) {
	if err != nil {
		log.Fatal(message, err)
	}
}
