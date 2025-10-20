# This master query performs a full system audit, correlating data from all 8 data sources.
# It demonstrates robust handling of optional data and complex calculations.
# FIX: Ensure all numeric fields are treated as numbers, not strings.

# --- Helper Functions ---
# Safely gets a person record from the personnel database.
def get_person($person_id; $personnel_db):
  ($personnel_db.records[]? | select(.person_id == $person_id));

# Calculates the average score for a given personality facet across a list of owners.
# This version is corrected to pass variables as arguments, not rely on lexical scope.
def average_facet_scores($persons; $trait; $facet):
  # This function correctly returns a number.
  ([$persons[] | .personality_profile?[$trait]?.facets?[$facet]?] | map(select(. != null)) | add) / ([persons[] | .personality_profile?[$trait]?.facets?[$facet]?] | map(select(. != null)) | length) // 0;

# --- Main Query Pipeline ---
[
  # Iterate through all parts in the schematics, using `?` for safety.
  .schematics.system.subsystems[]?.assemblies[]?.parts[]? as $part
  |
  # Find all materials for the current part.
  [ $part.material_ids[]? as $mat_id | .materials.materials[]? | select(.material_id == $mat_id) ] as $part_materials
  |
  # Filter for parts containing Niobium.
  select(any($part_materials[]; .element == "Niobium"))
  |
  # Gather all owners for the current part.
  [ $part.owner_ids[]? as $owner_id | get_person($owner_id; .personnel) ] as $owners
  |
  # Construct the final, deeply nested report object for each Niobium part.
  {
    part_id: $part.id,
    part_name: $part.name,
    # FIX: Ensure owner_count is a number.
    owner_count: ($owners | length),
    
    # Calculate the average personality profile of the part's owners.
    owner_avg_personality: {
      # FIX: Call avg_facet directly to get a number, not a string.
      avg_neuroticism_anxiety: (average_facet_scores($owners; "neuroticism"; "anxiety")),
      avg_neuroticism_vulnerability: (average_facet_scores($owners; "neuroticism"; "vulnerability"))
    },

    # Correlate with other data dimensions, using defensive access (`?`) and default values (`//`).
    supplier: ( .supply_chain.suppliers[]? | select(.id == $part.supplier_id) | .name // "Unknown Supplier" ),
    last_test_passed: ( .test_logs.results[]? | select(.part_id == $part.id) | .passed // false ),
    deployed_service: ( .software.deployments[]? | select(.target_part_id == $part.id) | .service_name // "None" )
  }
]
