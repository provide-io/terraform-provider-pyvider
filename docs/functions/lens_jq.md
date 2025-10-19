---
page_title: "Function: lens_jq"
description: |-
  Applies jq queries to JSON data for powerful data transformation and extraction
---

# lens_jq (Function)

> Applies jq queries to JSON data and returns transformed results as native objects

The `lens_jq` function enables powerful JSON data transformation using jq query syntax. It applies jq expressions to input data and returns the results as native Terraform objects, making it ideal for complex data manipulation and extraction tasks.

## When to Use This

- **JSON data transformation**: Transform complex JSON structures
- **API response processing**: Extract specific fields from API responses
- **Configuration manipulation**: Modify or extract configuration data
- **Data filtering**: Filter arrays and objects based on criteria
- **Complex data extraction**: Perform advanced queries on nested data

**Anti-patterns (when NOT to use):**
- Simple key access (use direct object access)
- Performance-critical paths (jq has overhead)
- When simpler functions suffice
- Non-JSON data types

## Quick Start

```terraform
# Extract specific field
locals {
  data = {
    users = [
      { name = "Alice", age = 30 },
      { name = "Bob", age = 25 }
    ]
  }
  names = provider::pyvider::lens_jq(".users[].name", local.data)  # Returns: ["Alice", "Bob"]
}

# Filter data
locals {
  filtered_users = provider::pyvider::lens_jq(".users[] | select(.age > 27)", local.data)
}
```

## Examples

### Basic Usage

```terraform
# Basic lens_jq function examples

# Example 1: Simple field extraction
locals {
  user_data = {
    id    = 123
    name  = "Alice Johnson"
    email = "alice@example.com"
  }

  user_name  = provider::pyvider::lens_jq(local.user_data, ".name")
  user_email = provider::pyvider::lens_jq(local.user_data, ".email")
  user_id    = provider::pyvider::lens_jq(local.user_data, ".id")
}

# Example 2: Array operations
locals {
  colors = ["red", "green", "blue", "yellow"]

  first_color = provider::pyvider::lens_jq(local.colors, ".[0]")
  last_color  = provider::pyvider::lens_jq(local.colors, ".[-1]")
  color_count = provider::pyvider::lens_jq(local.colors, "length")
}

# Example 3: Nested field access
locals {
  config = {
    database = {
      host = "localhost"
      port = 5432
    }
    cache = {
      host = "redis.local"
      port = 6379
    }
  }

  db_host    = provider::pyvider::lens_jq(local.config, ".database.host")
  db_port    = provider::pyvider::lens_jq(local.config, ".database.port")
  cache_host = provider::pyvider::lens_jq(local.config, ".cache.host")
}

# Example 4: Simple data transformation
locals {
  users = [
    { name = "Alice", active = true },
    { name = "Bob", active = false },
    { name = "Carol", active = true }
  ]

  active_users = provider::pyvider::lens_jq(local.users, "map(select(.active == true))")
  user_names   = provider::pyvider::lens_jq(local.users, "map(.name)")
}

# Output the results
output "lens_jq_examples" {
  value = {
    user_extraction = {
      name  = local.user_name
      email = local.user_email
      id    = local.user_id
    }
    array_operations = {
      first = local.first_color
      last  = local.last_color
      count = local.color_count
    }
    nested_access = {
      db_host    = local.db_host
      cache_host = local.cache_host
    }
    transformations = {
      active_users = length(local.active_users)
      all_names    = length(local.user_names)
    }
  }
}

```

### Advanced Usage

```terraform
# JQ transformation function examples

# Example 1: Basic JSON data extraction
locals {
  user_data = {
    name = "John Doe"
    age  = 30
    email = "john.doe@example.com"
    address = {
      street = "123 Main St"
      city   = "Anytown"
      state  = "CA"
      zip    = "12345"
    }
    hobbies = ["reading", "hiking", "coding"]
  }

  # Extract specific fields
  user_name = provider::pyvider::lens_jq(local.user_data, ".name")
  user_city = provider::pyvider::lens_jq(local.user_data, ".address.city")
  hobby_count = provider::pyvider::lens_jq(local.user_data, ".hobbies | length")
}

# Example 2: Array manipulation and filtering
locals {
  employees = [
    {
      id = 1
      name = "Alice Smith"
      department = "Engineering"
      salary = 95000
      skills = ["Python", "Go", "Docker"]
    },
    {
      id = 2
      name = "Bob Johnson"
      department = "Marketing"
      salary = 75000
      skills = ["SEO", "Analytics", "Content"]
    },
    {
      id = 3
      name = "Carol Davis"
      department = "Engineering"
      salary = 105000
      skills = ["JavaScript", "React", "Node.js"]
    }
  ]

  # Filter and transform arrays
  engineers = provider::pyvider::lens_jq(
    local.employees,
    '[.[] | select(.department == "Engineering")]'
  )

  high_earners = provider::pyvider::lens_jq(
    local.employees,
    '[.[] | select(.salary > 80000) | {name, salary}]'
  )

  all_skills = provider::pyvider::lens_jq(
    local.employees,
    '[.[].skills[]] | unique'
  )

  avg_salary = provider::pyvider::lens_jq(
    local.employees,
    '[.[].salary] | add / length'
  )
}

# Example 3: Complex data transformation
locals {
  api_response = {
    status = "success"
    data = {
      users = [
        {
          id = "user1"
          profile = {
            firstName = "John"
            lastName = "Doe"
            settings = {
              theme = "dark"
              notifications = true
            }
          }
          posts = [
            { title = "Hello World", likes = 5 },
            { title = "JQ is Awesome", likes = 12 }
          ]
        },
        {
          id = "user2"
          profile = {
            firstName = "Jane"
            lastName = "Smith"
            settings = {
              theme = "light"
              notifications = false
            }
          }
          posts = [
            { title = "Getting Started", likes = 8 },
            { title = "Advanced Tips", likes = 15 }
          ]
        }
      ]
    }
  }

  # Complex transformations
  user_summaries = provider::pyvider::lens_jq(
    local.api_response,
    '.data.users | map({
      id,
      full_name: (.profile.firstName + " " + .profile.lastName),
      theme: .profile.settings.theme,
      total_likes: [.posts[].likes] | add,
      post_count: (.posts | length)
    })'
  )

  dark_theme_users = provider::pyvider::lens_jq(
    local.api_response,
    '.data.users | map(select(.profile.settings.theme == "dark")) | map(.profile.firstName)'
  )

  popular_posts = provider::pyvider::lens_jq(
    local.api_response,
    '.data.users[].posts[] | select(.likes > 10) | .title'
  )
}

# Example 4: Configuration management with JQ
data "pyvider_env_variables" "config_vars" {
  prefix = "APP_"
}

locals {
  # Transform environment variables using JQ
  env_config = provider::pyvider::lens_jq(
    data.pyvider_env_variables.config_vars.values,
    'to_entries | map({
      key: (.key | sub("APP_"; "") | ascii_downcase),
      value: .value
    }) | from_entries'
  )

  # Extract specific configuration groups
  database_config = provider::pyvider::lens_jq(
    local.env_config,
    'to_entries | map(select(.key | startswith("database"))) | from_entries'
  )

  # Validate configuration
  required_keys = ["database_url", "api_key", "port"]
  missing_config = provider::pyvider::lens_jq(
    {
      required = local.required_keys
      actual = keys(local.env_config)
    },
    '.required - .actual'
  )
}

# Example 5: JSON data processing from HTTP API
data "pyvider_http_api" "github_repos" {
  url = "https://api.github.com/users/octocat/repos"
  headers = {
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "Terraform-Pyvider-Example"
  }
}

locals {
  # Process GitHub API response with JQ
  repos_data = can(jsondecode(data.pyvider_http_api.github_repos.response_body)) ?
    jsondecode(data.pyvider_http_api.github_repos.response_body) : []

  # Extract repository information
  public_repos = provider::pyvider::lens_jq(
    local.repos_data,
    '[.[] | select(.private == false) | {name, description, language, stars: .stargazers_count}]'
  )

  languages_used = provider::pyvider::lens_jq(
    local.repos_data,
    '[.[].language] | map(select(. != null)) | unique'
  )

  most_starred = provider::pyvider::lens_jq(
    local.repos_data,
    'max_by(.stargazers_count) | {name, stars: .stargazers_count}'
  )

  repo_stats = provider::pyvider::lens_jq(
    local.repos_data,
    '{
      total_repos: length,
      total_stars: [.[].stargazers_count] | add,
      avg_stars: ([.[].stargazers_count] | add / length),
      has_forks: [.[].forks_count] | add > 0
    }'
  )
}

# Create comprehensive report of JQ transformations
resource "pyvider_file_content" "jq_examples_report" {
  filename = "/tmp/lens_jq_examples_report.json"
  content = jsonencode({
    timestamp = timestamp()

    basic_extractions = {
      user_name = local.user_name
      user_city = local.user_city
      hobby_count = local.hobby_count
    }

    array_operations = {
      engineer_count = length(local.engineers)
      high_earner_count = length(local.high_earners)
      unique_skills = local.all_skills
      average_salary = local.avg_salary
    }

    complex_transformations = {
      user_summaries = local.user_summaries
      dark_theme_users = local.dark_theme_users
      popular_posts = local.popular_posts
    }

    configuration_management = {
      processed_env_vars = local.env_config
      database_settings = local.database_config
      missing_required_config = local.missing_config
    }

    github_analysis = data.pyvider_http_api.github_repos.status_code == 200 ? {
      public_repos_count = length(local.public_repos)
      languages_found = local.languages_used
      most_starred_repo = local.most_starred
      repository_statistics = local.repo_stats
    } : {
      error = "GitHub API request failed"
      status_code = data.pyvider_http_api.github_repos.status_code
    }

    jq_patterns_demonstrated = [
      "Basic field extraction",
      "Array filtering and mapping",
      "Complex nested transformations",
      "Configuration processing",
      "API response analysis",
      "Statistical calculations",
      "Conditional logic",
      "Data validation"
    ]
  })
}

# Create a detailed JQ patterns guide
resource "pyvider_file_content" "jq_patterns_guide" {
  filename = "/tmp/jq_patterns_guide.md"
  content = join("\n", [
    "# JQ Transformation Patterns Guide",
    "",
    "## Basic Field Extraction",
    "```jq",
    ".name                    # Extract simple field",
    ".address.city           # Extract nested field",
    ".hobbies | length       # Get array length",
    "```",
    "",
    "## Array Operations",
    "```jq",
    "[.[] | select(.department == \"Engineering\")]   # Filter arrays",
    "[.[] | {name, salary}]                          # Map and transform",
    "[.[].skills[]] | unique                         # Flatten and deduplicate",
    "[.[].salary] | add / length                     # Calculate average",
    "```",
    "",
    "## Complex Transformations",
    "```jq",
    "map({                                           # Transform objects",
    "  id,",
    "  full_name: (.firstName + \" \" + .lastName),",
    "  total_likes: [.posts[].likes] | add",
    "})",
    "",
    "to_entries | map(select(.key | startswith(\"db\"))) | from_entries  # Key filtering",
    "```",
    "",
    "## Practical Examples from This Configuration",
    "",
    "### User Data Processing",
    "- Extracted user name: ${local.user_name}",
    "- User city: ${local.user_city}",
    "- Number of hobbies: ${local.hobby_count}",
    "",
    "### Employee Analysis",
    "- Engineers found: ${length(local.engineers)}",
    "- High earners (>$80k): ${length(local.high_earners)}",
    "- Unique skills across all employees: ${length(local.all_skills)}",
    "- Average salary: $${local.avg_salary}",
    "",
    "### Configuration Management",
    "- Environment variables processed: ${length(keys(local.env_config))}",
    "- Database config keys: ${length(keys(local.database_config))}",
    "- Missing required config: ${length(local.missing_config)}",
    "",
    data.pyvider_http_api.github_repos.status_code == 200 ? join("\n", [
      "### GitHub Repository Analysis",
      "- Public repositories: ${length(local.public_repos)}",
      "- Programming languages used: ${length(local.languages_used)}",
      "- Most starred repository: ${local.most_starred.name} (${local.most_starred.stars} stars)",
      "- Total repositories: ${local.repo_stats.total_repos}",
      "- Total stars across all repos: ${local.repo_stats.total_stars}"
    ]) : "### GitHub API: Request failed",
    "",
    "## Tips for Effective JQ Usage",
    "",
    "1. **Start Simple**: Begin with basic field extraction before complex transformations",
    "2. **Use Pipe Operators**: Chain operations with | for readable transformations",
    "3. **Test Incrementally**: Build complex queries step by step",
    "4. **Handle Nulls**: Use select() to filter out null values",
    "5. **Combine with Terraform**: Use with data sources for dynamic configuration",
    "",
    "Generated at: ${timestamp()}"
  ])
}

output "lens_jq_examples_results" {
  description = "Results from various JQ transformation examples"
  value = {
    basic_operations = {
      user_name = local.user_name
      user_city = local.user_city
      hobby_count = local.hobby_count
    }

    array_processing = {
      engineers_found = length(local.engineers)
      high_earners_found = length(local.high_earners)
      unique_skills_count = length(local.all_skills)
      average_salary = local.avg_salary
    }

    complex_data = {
      user_summaries_count = length(local.user_summaries)
      dark_theme_users = local.dark_theme_users
      popular_posts_found = length(local.popular_posts)
    }

    configuration = {
      env_vars_processed = length(keys(local.env_config))
      database_config_keys = length(keys(local.database_config))
      missing_config_count = length(local.missing_config)
    }

    github_integration = data.pyvider_http_api.github_repos.status_code == 200 ? {
      api_success = true
      repos_analyzed = length(local.public_repos)
      languages_found = length(local.languages_used)
      total_stars = local.repo_stats.total_stars
    } : {
      api_success = false
      status_code = data.pyvider_http_api.github_repos.status_code
    }

    files_created = [
      pyvider_file_content.jq_examples_report.filename,
      pyvider_file_content.jq_patterns_guide.filename
    ]
  }
}

```

## Signature

`lens_jq(query: string, data: any) -> any`

## Arguments

- **`query`** (string, required) - The jq expression to apply to the data
- **`data`** (any, required) - The input data to query (typically JSON-like objects)

## Return Value

Returns the result of applying the jq query to the input data. The return type depends on the query:
- Objects, arrays, strings, numbers, or booleans based on the query result
- `null` if the query returns null or if input data is null

## Common jq Query Patterns

### Field Extraction
```terraform
locals {
  config = { database = { host = "localhost", port = 5432 } }
  host = provider::pyvider::lens_jq(".database.host", local.config)  # "localhost"
  port = provider::pyvider::lens_jq(".database.port", local.config)  # 5432
}
```

### Array Processing
```terraform
locals {
  servers = {
    instances = [
      { name = "web-1", status = "running" },
      { name = "web-2", status = "stopped" },
      { name = "db-1", status = "running" }
    ]
  }

  running_servers = provider::pyvider::lens_jq(
    ".instances[] | select(.status == \"running\") | .name",
    local.servers
  )  # ["web-1", "db-1"]
}
```

### Data Transformation
```terraform
locals {
  raw_data = {
    metrics = [
      { service = "api", cpu = 75, memory = 60 },
      { service = "db", cpu = 45, memory = 80 }
    ]
  }

  transformed = provider::pyvider::lens_jq(
    ".metrics | map({name: .service, load: (.cpu + .memory) / 2})",
    local.raw_data
  )  # [{"name": "api", "load": 67.5}, {"name": "db", "load": 62.5}]
}
```

## Related Functions

- [`lookup`](../collection_functions/lookup.md) - Simple key-value lookups
- [`contains`](../collection_functions/contains.md) - Check array membership
- [`length`](../collection_functions/length.md) - Get collection sizes