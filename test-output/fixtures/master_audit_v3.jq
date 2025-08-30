# MASTER AUDIT V3: FULL-SPECTRUM PERSONNEL-CENTRIC SYSTEM ANALYSIS
# This query is corrected to use proper jq function argument syntax (`;` separator)
# and is wrapped in an array constructor `[]` to guarantee a single array output.
# FIX: Ensure all numeric fields are treated as numbers, not strings.

def get_person($pid; $pdb):
  ($pdb.records[]? | select(.person_id == $pid));

def avg_facet($persons; $trait; $facet):
  # This function correctly returns a number.
  ([$persons[] | .personality_profile?[$trait]?.facets?[$facet]? | select(. != null)] | add / length) // 0;

# THE FIX: Wrap the entire pipeline in `[]`
[
  .schematics.system.subsystems[]?.assemblies[]?.parts[]? as $part |
  [ $part.owner_ids[]? as $owner_id | get_person($owner_id; .personnel) ] as $owners |
  select(($owners | length) > 0) |
  {
    part_id: $part.id,
    part_name: $part.name,
    # FIX: Ensure owner_count is a number
    owner_count: ($owners | length),
    owner_avg_personality: {
      # FIX: Call avg_facet directly to get a number, not a string
      avg_neuroticism_anxiety: (avg_facet($owners; "neuroticism"; "anxiety")),
      avg_neuroticism_vulnerability: (avg_facet($owners; "neuroticism"; "vulnerability"))
    },
    supplier: ( .supply_chain.suppliers[]? | select(.id == $part.supplier_id) | .name // "Unknown Supplier" ),
    last_test_passed: ( .test_logs.results[]? | select(.part_id == $part.id) | .passed // false )
  }
]
