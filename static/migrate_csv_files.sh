for file in contact_details.csv employees.csv salary_details.csv affiliation_details.csv; do
  docker cp $file familia-db-1:/tmp/
done
