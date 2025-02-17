#!/bin/bash

# **** REMEMBER *****
# Remember to update the env var ``LATEST_VERSION`` in ci.yml
#

# List of versions
versions=(
    # if added more "latest", change "$LATEST"
    'latest-ubuntu' 
    'latest-ubuntu-student'
    'v25.2.0'
    'v25.1.0'
    'v25.1-ubuntu'
    'v25.1-ubuntu-student'
    'v24.2.0'
    'v24.2-ubuntu'
    'v24.2-ubuntu-student'
    'v24.1.0'
    'v24.1-ubuntu'
    'v24.1-ubuntu-student'
    'v23.2.0'
    'v23.2-ubuntu'
    'v23.1.0'
    'v23.1-ubuntu'
    'v22.2.1'
    'v22.2-ubuntu'
)

LATEST=3 # for 'latest-ubuntu' and 'latest-ubuntu-student'

# Run only ubuntu jobs
ONLY_UBUNTU="${ONLY_UBUNTU:-false}"

# On remote
ON_REMOTE="${ON_REMOTE:-false}"

# Do not process more than the $AUTH_USER_LIMIT_VERSIONS versions in above list
AUTH_USER_LIMIT_VERSIONS="${AUTH_USER_LIMIT_VERSIONS:-2}"
AUTH_USER_LIMIT=$((LATEST+AUTH_USER_LIMIT_VERSIONS*3)) 

# Students licenses only last a year, hence $NON_AUTH_USER_LIMIT_VERSIONS cannot be more than 2.
NON_AUTH_USER_LIMIT_VERSIONS="${NON_AUTH_USER_LIMIT_VERSIONS:-2}"
NON_AUTH_USER_LIMIT=$((LATEST+NON_AUTH_USER_LIMIT_VERSIONS*3))

# Hard limit version. Generally do not process more than $HARD_LIMIT_VERSION
LIMIT_VERSIONS="${LIMIT_VERSIONS:-0}"
HARD_LIMIT_VERSION=$((LATEST+LIMIT_VERSIONS*3))

# Checking if extended testing must be done
# 

if [[ $ON_SCHEDULE || ( $ON_WORKFLOW_DISPATCH && $RUN_ALL_TEST ) || ( $ON_PUSH && $HAS_TAG ) ]]; then
    extended_testing=true
else
    extended_testing=false
fi

## Start
JSON="{\"include\":["
counter=0

# Loop through each version
for version in "${versions[@]}"; do
    
    # 1 based counter
    ((counter++))

    # Checking hardlimit
    if [[ $LIMIT_VERSIONS -ne 0 && $counter -gt $HARD_LIMIT_VERSION ]]; then
        echo "Reached limit."
        break
    fi

    # checking version config
    if [[ "$version" == *"ubuntu"* ]]; then
        ON_UBUNTU=true;
    else 
        ON_UBUNTU=false;
    fi

    if [[ "$version" == *"student"* ]]; then
        ON_STUDENT=true;
    else 
        ON_STUDENT=false;
    fi

    # Printing
    echo "Processing $counter"
    echo "  - Version: $version"
    echo "  - extended_testing: $extended_testing"
    echo "  - auth_user: $auth_user"
    echo "  - Student: $ON_STUDENT"
    echo "  - Ubuntu: $ON_UBUNTU"

    # Skipping if on Ubuntu only
    if [[ "$ON_UBUNTU" != "true" && "$ONLY_UBUNTU" == "true" ]]; then
        echo "Skipping non-ubuntu versions"
        echo ""
        continue
    fi

    # Skipping if on remote and on student
    if [[ "$ON_STUDENT" != "true" && "$ON_REMOTE" == "true" ]]; then
        echo "Skipping non-student versions when running on remote"
        echo ""
        continue
    fi

    # Skipping student versions on auth_user
    # if [[ "$auth_user" == "true" && "$ON_STUDENT" == "true" ]]; then
    #     echo "Skipping student versions when user is authenticated"
    #     echo ""
    #     continue
    # fi

    # main logic
    if [[ "$auth_user" == "true" ]]; then
        if [[ "$extended_testing" == "true" ]]; then
            # runs everything 
            add_line="true";
        else
            # Runs only "latest" and last two versions.
            # Last 6 entries in the list above.
            if [[ $counter -le $AUTH_USER_LIMIT ]]; then
                add_line="true";
            else
                add_line="false";
            fi
        fi
    else
        if [[ $ON_STUDENT == "true" &&  $counter -le $NON_AUTH_USER_LIMIT ]]; then
            add_line="true";
        else
            add_line="false";
        fi
    fi

    # Add line to json
    if [[ "$version" == *"latest-ubuntu"* ]] ; then
        version_num=$(echo $LATEST_VERSION)
    else
        version_num=$(echo "$version" | head -c 5 | tail -c 4 | tr -d '.')
    fi;

    if [[ "$add_line" == "true" ]]; then
        JSONline="{\"mapdl-version\": \"$version\", \"number\": \"$version_num\" },"

        echo "ADDED line: $JSONline"

        # checks that the line is not repeated before adding it.
        if [[ "$JSON" != *"$JSONline"* ]]; then
            JSON="$JSON$JSONline"
        fi
    else
        echo "NOT added line"
    fi
    echo ""

done

# Remove last "," and add closing brackets
if [[ $JSON == *, ]]; then
    JSON="${JSON%?}"
fi
JSON="$JSON]}"
echo "$JSON"

# Set output
echo "matrix=$( echo "$JSON" )" >> $GITHUB_OUTPUT