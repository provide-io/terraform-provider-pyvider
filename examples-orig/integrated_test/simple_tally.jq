# This simple query creates a tally of all unique material types and their counts.
{
  material_types: (
    [.schematics.system.subsystems[].assemblies[].parts[].material_ids[]? as $mat_id | .materials.materials[] | select(.material_id == $mat_id) | .properties.type]
    | group_by(.)
    | map({(.[0]): . | length})
    | add
  )
}
